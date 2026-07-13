"""Portmanteau tool tests with mocked client."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from pinokio_mcp.tools.portmanteau import app_management, system_management


@pytest.mark.asyncio
async def test_app_management_list() -> None:
    client = MagicMock()
    client.ping = AsyncMock(return_value=False)
    client.home = MagicMock()
    client.home.__str__ = lambda _s: "D:/pinokio"  # type: ignore[method-assign]
    client.list_apps = AsyncMock(
        return_value=[{"path": "foo", "title": "Foo", "source": "filesystem"}]
    )

    result = await app_management.app_management(client, action="list")
    assert result["success"] is True
    assert len(result["data"]["apps"]) == 1


@pytest.mark.asyncio
async def test_system_management_ping_online() -> None:
    client = MagicMock()
    client.ping = AsyncMock(return_value=True)
    client.port = 42000
    client.host = "localhost"
    client.home = MagicMock()
    client.home.__str__ = lambda _s: "D:/pinokio"  # type: ignore[method-assign]

    result = await system_management.system_management(client, action="ping")
    assert result["success"] is True
    assert result["data"]["online"] is True
