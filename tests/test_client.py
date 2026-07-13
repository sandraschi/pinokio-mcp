"""Unit tests for PinokioClient."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from pinokio_mcp.client import PinokioClient, _read_pinokio_js_meta


@pytest.fixture
def pinokio_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    api = tmp_path / "api" / "demo-app"
    api.mkdir(parents=True)
    (api / "pinokio.js").write_text(
        'module.exports = { title: "Demo", description: "Test app" }',
        encoding="utf-8",
    )
    monkeypatch.setenv("PINOKIO_HOME", str(tmp_path))
    return tmp_path


def test_discover_home_from_env(pinokio_home: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PINOKIO_HOME", str(pinokio_home))
    client = PinokioClient()
    assert client.home == pinokio_home


def test_discover_home_windows_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    appdata = tmp_path / "Pinokio"
    appdata.mkdir()
    (appdata / "config.json").write_text(json.dumps({"home": "D:/pinokio"}), encoding="utf-8")
    monkeypatch.setenv("APPDATA", str(tmp_path))
    monkeypatch.delenv("PINOKIO_HOME", raising=False)
    client = PinokioClient()
    assert client.home == Path("D:/pinokio")


def test_list_apps_filesystem(pinokio_home: Path) -> None:
    client = PinokioClient(home=str(pinokio_home))
    apps = client._list_apps_filesystem()  # noqa: SLF001
    assert len(apps) == 1
    assert apps[0]["path"] == "demo-app"
    assert apps[0]["title"] == "Demo"
    assert apps[0]["source"] == "filesystem"


def test_read_pinokio_js_meta(tmp_path: Path) -> None:
    meta = _read_pinokio_js_meta(tmp_path / "missing.js")
    assert meta == {}


@pytest.mark.asyncio
async def test_ping_with_fixed_port(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeResponse:
        status_code = 200

        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return {"home": "D:/pinokio", "api": [{"path": "demo"}], "scripts": []}

    class FakeHttp:
        async def get(self, url: str, **kwargs):  # noqa: ANN003
            del kwargs
            return FakeResponse()

        async def request(self, method: str, url: str, **kwargs):  # noqa: ANN003
            del method, kwargs
            return FakeResponse()

        async def aclose(self) -> None:
            return None

    client = PinokioClient(port=42000)

    async def _fake_http() -> FakeHttp:
        return FakeHttp()

    monkeypatch.setattr(client, "_get_http", _fake_http)
    assert await client.ping() is True
    info = await client.get_info()
    assert info["home"] == "D:/pinokio"
    await client.aclose()
