"""Pinokio system queries."""

from __future__ import annotations

from typing import Any, Literal

from pinokio_mcp.client import PinokioClient, PinokioOfflineError
from pinokio_mcp.models import ToolResponse


async def system_management(
    client: PinokioClient,
    action: Literal["ping", "info", "localhost_search"],
) -> dict[str, Any]:
    action = action.strip().lower()  # type: ignore[assignment]

    try:
        if action == "ping":
            online = await client.ping()
            port = client.port
            return ToolResponse(
                success=True,
                message="Pinokio is running" if online else "Pinokio is not reachable",
                data={
                    "online": online,
                    "host": client.host,
                    "port": port,
                    "home": str(client.home),
                },
            ).to_dict()

        if action == "info":
            if not await client.ping():
                raise PinokioOfflineError("Pinokio is offline")
            info = await client.get_info()
            return ToolResponse(
                success=True,
                message="Pinokio system info",
                data={
                    "home": info.get("home") or str(client.home),
                    "platform": info.get("platform"),
                    "arch": info.get("arch"),
                    "version": info.get("version"),
                    "scripts": info.get("scripts") or [],
                    "proxies": info.get("proxies") or [],
                    "api": info.get("api") or [],
                    "port": client.port,
                },
            ).to_dict()

        if action == "localhost_search":
            if not await client.ping():
                raise PinokioOfflineError("Pinokio is offline")
            proxies = await client.localhost_search()
            return ToolResponse(
                success=True,
                message=f"Found {len(proxies)} proxied service(s)",
                data={"services": proxies},
            ).to_dict()

        return ToolResponse(
            success=False,
            message=f"Unknown action: {action}",
            suggestions=["Use ping, info, or localhost_search"],
        ).to_dict()

    except PinokioOfflineError as exc:
        return ToolResponse(
            success=False,
            message=str(exc),
            data={"online": False, "home": str(client.home)},
            suggestions=["Start Pinokio", "Run scripts/discover-api.ps1 to probe ports"],
        ).to_dict()
    except Exception as exc:  # noqa: BLE001
        return ToolResponse(success=False, message=f"Unexpected error: {exc}").to_dict()
