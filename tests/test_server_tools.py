"""Exercise the registered MCP tools through an in-memory FastMCP client.

Uses a real PinokioClient pointed at an empty tmp home: with Pinokio
offline every call takes the filesystem/offline path, so no network
beyond refused localhost probes is involved.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from fastmcp import Client

from pinokio_mcp import server as server_module
from pinokio_mcp.client import PinokioClient


@pytest.fixture
def offline_home(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    api = tmp_path / "api" / "demo-app"
    api.mkdir(parents=True)
    (api / "pinokio.js").write_text(
        'module.exports = { title: "Demo", description: "Test app" }',
        encoding="utf-8",
    )
    monkeypatch.setenv("PINOKIO_HOME", str(tmp_path))
    monkeypatch.delenv("PINOKIO_PORT", raising=False)
    return tmp_path


def _client() -> PinokioClient:
    return PinokioClient()


@pytest.mark.asyncio
async def test_mcp_lists_three_portmanteau_tools() -> None:
    async with Client(server_module.mcp) as mcp_client:
        tools = await mcp_client.list_tools()
    assert sorted(t.name for t in tools) == [
        "app_management",
        "lww_management",
        "system_management",
    ]


@pytest.mark.asyncio
async def test_mcp_app_list_offline_uses_filesystem(offline_home: Path) -> None:
    _ = offline_home
    async with Client(server_module.mcp) as mcp_client:
        result = await mcp_client.call_tool("app_management", {"action": "list"})
    apps = result.data["data"]["apps"]
    assert apps[0]["path"] == "demo-app"
    assert result.data["data"]["pinokio_online"] is False


@pytest.mark.asyncio
async def test_mcp_status_and_ping_offline(offline_home: Path) -> None:
    _ = offline_home
    async with Client(server_module.mcp) as mcp_client:
        status = await mcp_client.call_tool(
            "app_management", {"action": "status", "app": "demo-app"}
        )
        ping = await mcp_client.call_tool("system_management", {"action": "ping"})
    assert status.data["data"]["running"] is False
    assert ping.data["data"]["online"] is False


@pytest.mark.asyncio
async def test_mcp_rejects_bad_actions_without_network() -> None:
    from fastmcp.exceptions import ToolError

    async with Client(server_module.mcp) as mcp_client:
        with pytest.raises(ToolError):
            await mcp_client.call_tool("app_management", {"action": "nope"})
        missing = await mcp_client.call_tool("app_management", {"action": "start"})
    assert "required" in missing.data["message"]
