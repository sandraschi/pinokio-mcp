#!/usr/bin/env python3
"""Live smoke test for Pinokio MCP client (requires Pinokio running for full pass)."""

from __future__ import annotations

import asyncio
import sys

from pinokio_mcp.client import PinokioClient
from pinokio_mcp.tools.portmanteau.app_management import app_management
from pinokio_mcp.tools.portmanteau.system_management import system_management


async def main() -> int:
    client = PinokioClient()
    print(f"Home: {client.home}")

    ping = await system_management(client, action="ping")
    print("ping:", ping)

    apps = await app_management(client, action="list")
    print("list:", {k: apps[k] for k in ("success", "message")})
    if apps.get("data"):
        print("  apps:", len(apps["data"].get("apps", [])))

    if ping.get("data", {}).get("online"):
        info = await system_management(client, action="info")
        scripts = info.get("data", {}).get("scripts", [])
        print("info: scripts running:", len(scripts))
        localhost = await system_management(client, action="localhost_search")
        print("localhost_search:", localhost.get("message"))

    await client.aclose()
    return 0 if ping.get("success") else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
