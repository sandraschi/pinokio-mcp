"""LAN Wide Web - discover Pinokio instances and start apps remotely."""

from __future__ import annotations

import asyncio
import socket
from typing import Any, Literal

import httpx
from zeroconf import Zeroconf
from zeroconf.asyncio import AsyncServiceBrowser, AsyncZeroconf

from pinokio_mcp.client import PORT_MAX, PORT_MIN, PinokioClient
from pinokio_mcp.models import PinokioDevice, ToolResponse

_SERVICE_TYPES = ("_pinokio._tcp.local.", "_http._tcp.local.")


class _PinokioListener:
    def __init__(self) -> None:
        self.devices: dict[str, PinokioDevice] = {}

    def add_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        info = zc.get_service_info(type_, name)
        if info is None:
            return
        host = socket.inet_ntoa(info.addresses[0]) if info.addresses else ""
        port = int(info.port or 0)
        if not host:
            return
        if type_ == "_http._tcp.local." and not (PORT_MIN <= port <= PORT_MAX):
            return
        key = f"{host}:{port}"
        self.devices[key] = PinokioDevice(
            name=name.removesuffix("." + type_.rstrip(".")),
            host=host,
            port=port,
            properties={k.decode(): v.decode(errors="ignore") for k, v in info.properties.items()},
        )

    def remove_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        del zc, type_, name

    def update_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        self.add_service(zc, type_, name)


async def _discover_devices(timeout: float = 3.0) -> list[PinokioDevice]:
    listener = _PinokioListener()
    aiozc = AsyncZeroconf()
    browsers: list[AsyncServiceBrowser] = []
    try:
        for service_type in _SERVICE_TYPES:
            browsers.append(AsyncServiceBrowser(aiozc.zeroconf, service_type, handlers=[listener]))
        await asyncio.sleep(timeout)
    finally:
        for browser in browsers:
            await browser.async_cancel()
        await aiozc.async_close()

    # Verify /check on discovered ports; also scan localhost range if empty
    verified: dict[str, PinokioDevice] = {}
    async with httpx.AsyncClient(timeout=2.0) as http:
        candidates = list(listener.devices.values())
        if not candidates:
            for port in range(PORT_MIN, PORT_MAX + 1):
                candidates.append(
                    PinokioDevice(name=f"localhost:{port}", host="127.0.0.1", port=port)
                )

        for device in candidates:
            try:
                resp = await http.get(f"http://{device.host}:{device.port}/check")
                if resp.status_code == 200:
                    key = f"{device.host}:{device.port}"
                    verified[key] = device
            except httpx.HTTPError:
                continue

    return list(verified.values())


async def lww_management(
    client: PinokioClient,
    action: Literal["devices", "start_remote"],
    device: str | None = None,
    app: str | None = None,
    script: str | None = None,
    port: int | None = None,
) -> dict[str, Any]:
    action = action.strip().lower()  # type: ignore[assignment]

    try:
        if action == "devices":
            devices = await _discover_devices()
            payload = [d.model_dump() for d in devices]
            return ToolResponse(
                success=True,
                message=f"Found {len(payload)} Pinokio instance(s) on the LAN",
                data={"devices": payload},
            ).to_dict()

        if action == "start_remote":
            if not app or not app.strip():
                return ToolResponse(
                    success=False,
                    message="Parameter 'app' is required",
                    suggestions=["lww_management(action='devices') first"],
                ).to_dict()

            host: str | None = None
            remote_port: int | None = port

            if device:
                if ":" in device:
                    host_part, port_part = device.rsplit(":", 1)
                    host = host_part.strip()
                    try:
                        remote_port = int(port_part)
                    except ValueError:
                        remote_port = port
                else:
                    host = device.strip()

            if not host or remote_port is None:
                return ToolResponse(
                    success=False,
                    message="Provide device as host:port (e.g. 192.168.1.10:42000)",
                    suggestions=["lww_management(action='devices') to list reachable instances"],
                ).to_dict()

            result = await client.remote_start(host, remote_port, app, script=script)
            return ToolResponse(
                success=bool(result.get("launched")),
                message=f"Remote start requested for {app} on {host}:{remote_port}",
                data=result,
            ).to_dict()

        return ToolResponse(
            success=False,
            message=f"Unknown action: {action}",
            suggestions=["Use devices or start_remote"],
        ).to_dict()

    except Exception as exc:  # noqa: BLE001
        return ToolResponse(success=False, message=f"Unexpected error: {exc}").to_dict()
