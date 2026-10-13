"""FastMCP server for Pinokio - stdio transport."""

from __future__ import annotations

import json
import os
from typing import Literal

from fastmcp import FastMCP

from pinokio_mcp.client import PinokioClient
from pinokio_mcp.tools.portmanteau.app_management import app_management as _app_management
from pinokio_mcp.tools.portmanteau.lww_management import lww_management as _lww_management
from pinokio_mcp.tools.portmanteau.system_management import system_management as _system_management

mcp = FastMCP(
    "pinokio-mcp",
    instructions=(
        "Control Pinokio (1-click localhost AI app launcher). "
        "Use app_management for apps, system_management for health/info/proxies, "
        "lww_management for LAN devices. Pinokio must be running for start/stop/delete; "
        "list works offline via filesystem."
    ),
)

_client: PinokioClient | None = None


def _get_client() -> PinokioClient:
    global _client
    if _client is None:
        _client = PinokioClient()
    return _client


@mcp.tool()
async def app_management(
    action: Literal["list", "status", "start", "stop", "delete"],
    app: str | None = None,
    script: str | None = None,
) -> dict:
    """Manage Pinokio apps: list, status, start, stop, delete."""
    return await _app_management(_get_client(), action=action, app=app, script=script)


@mcp.tool()
async def system_management(
    action: Literal["ping", "info", "localhost_search"],
) -> dict:
    """Pinokio system operations: ping, info, localhost_search."""
    return await _system_management(_get_client(), action=action)


@mcp.tool()
async def lww_management(
    action: Literal["devices", "start_remote"],
    device: str | None = None,
    app: str | None = None,
    script: str | None = None,
    port: int | None = None,
) -> dict:
    """LAN Wide Web: discover Pinokio instances and start apps remotely."""
    return await _lww_management(
        _get_client(),
        action=action,
        device=device,
        app=app,
        script=script,
        port=port,
    )


@mcp.resource("pinokio://apps")
async def resource_apps() -> str:
    apps = await _get_client().list_apps()
    return json.dumps({"apps": apps}, indent=2)


@mcp.resource("pinokio://running")
async def resource_running() -> str:
    client = _get_client()
    if not await client.ping():
        return json.dumps({"scripts": [], "online": False})
    info = await client.get_info()
    return json.dumps({"scripts": info.get("scripts") or [], "online": True}, indent=2)


@mcp.resource("pinokio://localhost")
async def resource_localhost() -> str:
    client = _get_client()
    if not await client.ping():
        return json.dumps({"services": [], "online": False})
    services = await client.localhost_search()
    return json.dumps({"services": services, "online": True}, indent=2)


@mcp.resource("pinokio://lww/devices")
async def resource_lww_devices() -> str:
    from pinokio_mcp.tools.portmanteau.lww_management import _discover_devices

    devices = await _discover_devices()
    return json.dumps({"devices": [d.model_dump() for d in devices]}, indent=2)


@mcp.prompt()
def prompt_start_workflow() -> str:
    return (
        "To start a Pinokio AI workflow:\n"
        "1. system_management(action='ping') - confirm Pinokio is running\n"
        "2. app_management(action='list') - list installed apps\n"
        "3. app_management(action='start', app='<folder>', script='start.js') - launch\n"
        "4. system_management(action='localhost_search') - find proxied URLs\n"
    )


@mcp.prompt()
def prompt_cross_device() -> str:
    return (
        "LAN Wide Web orchestration:\n"
        "1. lww_management(action='devices') - find Pinokio on the LAN\n"
        "2. lww_management(action='start_remote', device='192.168.x.x:42000', app='<name>')\n"
    )


@mcp.prompt()
def prompt_troubleshooting() -> str:
    return (
        "Pinokio MCP troubleshooting:\n"
        "- Pinokio offline: start the Pinokio app; ports 42000-42059 must answer GET /check\n"
        "- Wrong home: set PINOKIO_HOME or check %APPDATA%\\Pinokio\\config.json on Windows\n"
        "- Stop incomplete: HTTP stop is best-effort; use Pinokio UI to kill stubborn scripts\n"
        "- Run scripts/discover-api.ps1 or scripts/test_tools.py for live verification\n"
    )


@mcp.prompt()
def prompt_available_apps() -> str:
    return (
        "app_management(action='list') tells you an app exists and whether it's running -\n"
        "it does NOT tell you whether that app has real model weights downloaded (some\n"
        "apps here are just an empty environment - checked and confirmed for at least one\n"
        "app on this install as of 2026-07-14). For a real, hand-verified inventory of\n"
        "what's actually usable, what it's good for, and where to start, read\n"
        "AVAILABLE_APPS.md in this repo's root before assuming an app is ready to use.\n"
    )


def main() -> None:
    os.environ.setdefault("FASTMCP_LOG_LEVEL", "WARNING")
    mcp.run()


if __name__ == "__main__":
    main()
