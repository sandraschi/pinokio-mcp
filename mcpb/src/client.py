"""Pinokio HTTP client with port/home discovery and filesystem fallback."""

from __future__ import annotations

import asyncio
import json
import os
import re
from pathlib import Path
from typing import Any

import httpx

PORT_MIN = 42000
PORT_MAX = 42059
DEFAULT_SCRIPT = "start.js"
_TITLE_RE = re.compile(r"""title\s*:\s*["']([^"']+)["']""")
_DESC_RE = re.compile(r"""description\s*:\s*["']([^"']+)["']""")


def _expand_home(path: str) -> Path:
    return Path(path).expanduser()


class PinokioClient:
    """Talks to pinokiod over HTTP; falls back to filesystem when offline."""

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        home: str | None = None,
        timeout: float = 15.0,
    ) -> None:
        self.host = (host or os.getenv("PINOKIO_HOST") or "localhost").strip()
        self._port_override = port or _env_int("PINOKIO_PORT")
        self._home_override = home or os.getenv("PINOKIO_HOME")
        self.timeout = timeout
        self._port: int | None = None
        self._home: Path | None = None
        self._http: httpx.AsyncClient | None = None

    @property
    def home(self) -> Path:
        if self._home is None:
            self._home = self._discover_home()
        return self._home

    @property
    def port(self) -> int | None:
        return self._port_override or self._port

    @property
    def base_url(self) -> str | None:
        p = self.port
        if p is None:
            return None
        return f"http://{self.host}:{p}"

    async def _get_http(self) -> httpx.AsyncClient:
        if self._http is None:
            self._http = httpx.AsyncClient(timeout=self.timeout, follow_redirects=True)
        return self._http

    async def aclose(self) -> None:
        if self._http is not None:
            await self._http.aclose()
            self._http = None

    def _discover_home(self) -> Path:
        if self._home_override:
            return _expand_home(self._home_override)

        if os.name == "nt":
            config_path = Path(os.environ.get("APPDATA", "")) / "Pinokio" / "config.json"
            if config_path.is_file():
                try:
                    raw = json.loads(config_path.read_text(encoding="utf-8"))
                    home = raw.get("home")
                    if isinstance(home, str) and home.strip():
                        return Path(home)
                except (json.JSONDecodeError, OSError):
                    pass

        return _expand_home("~/pinokio")

    async def discover_port(self) -> int | None:
        if self._port_override is not None:
            self._port = self._port_override
            return self._port

        if self._port is not None:
            return self._port

        http = await self._get_http()

        async def _probe(candidate: int) -> int | None:
            url = f"http://{self.host}:{candidate}/check"
            try:
                resp = await http.get(url, timeout=0.75)
                if resp.status_code == 200:
                    return candidate
            except httpx.HTTPError:
                return None
            return None

        results = await asyncio.gather(
            *(_probe(port) for port in range(PORT_MIN, PORT_MAX + 1))
        )
        for candidate in results:
            if candidate is not None:
                self._port = candidate
                return candidate
        return None

    async def ping(self) -> bool:
        port = await self.discover_port()
        if port is None:
            return False
        http = await self._get_http()
        try:
            resp = await http.get(f"http://{self.host}:{port}/check", timeout=3.0)
            return resp.status_code == 200
        except httpx.HTTPError:
            return False

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, str] | None = None,
        json_body: dict[str, Any] | None = None,
        retries: int = 2,
    ) -> httpx.Response:
        port = await self.discover_port()
        if port is None:
            raise PinokioOfflineError("Pinokio is not running (no /check on ports 42000-42059)")

        url = f"http://{self.host}:{port}{path}"
        http = await self._get_http()
        last_err: Exception | None = None
        for attempt in range(retries + 1):
            try:
                resp = await http.request(method, url, params=params, json=json_body)
                return resp
            except httpx.HTTPError as exc:
                last_err = exc
                if attempt < retries:
                    await asyncio.sleep(0.5 * (attempt + 1))
        raise PinokioOfflineError(f"Pinokio request failed: {last_err}") from last_err

    async def get_info(self) -> dict[str, Any]:
        resp = await self.request("GET", "/pinokio/info")
        resp.raise_for_status()
        data = resp.json()
        if not isinstance(data, dict):
            raise PinokioAPIError("Unexpected /pinokio/info payload")
        return data

    async def list_apps(self) -> list[dict[str, Any]]:
        if await self.ping():
            try:
                info = await self.get_info()
                apps = info.get("api") or []
                scripts = info.get("scripts") or []
                running_by_app: dict[str, list[dict[str, Any]]] = {}
                for script in scripts:
                    if not isinstance(script, dict):
                        continue
                    app_name = str(script.get("app") or "")
                    running_by_app.setdefault(app_name, []).append(script)

                result: list[dict[str, Any]] = []
                for item in apps:
                    if not isinstance(item, dict):
                        continue
                    path = str(item.get("path") or "")
                    result.append(
                        {
                            "path": path,
                            "title": item.get("title"),
                            "description": item.get("description"),
                            "icon": item.get("icon"),
                            "running": path in running_by_app or any(
                                s.get("app") == path for s in scripts if isinstance(s, dict)
                            ),
                            "running_scripts": running_by_app.get(path, []),
                            "source": "api",
                        }
                    )
                return result
            except (PinokioOfflineError, PinokioAPIError, httpx.HTTPError):
                pass

        return self._list_apps_filesystem()

    def _list_apps_filesystem(self) -> list[dict[str, Any]]:
        api_dir = self.home / "api"
        if not api_dir.is_dir():
            return []

        apps: list[dict[str, Any]] = []
        for child in sorted(api_dir.iterdir()):
            if not child.is_dir():
                continue
            meta = _read_pinokio_js_meta(child / "pinokio.js")
            apps.append(
                {
                    "path": child.name,
                    "title": meta.get("title") or child.name,
                    "description": meta.get("description"),
                    "icon": None,
                    "running": False,
                    "running_scripts": [],
                    "source": "filesystem",
                }
            )
        return apps

    async def app_status(self, app: str) -> dict[str, Any]:
        app = app.strip().strip("/")
        if await self.ping():
            info = await self.get_info()
            scripts = [
                s
                for s in info.get("scripts") or []
                if isinstance(s, dict) and str(s.get("app") or "") == app
            ]
            return {
                "app": app,
                "running": len(scripts) > 0,
                "scripts": scripts,
                "source": "api",
            }

        return {"app": app, "running": False, "scripts": [], "source": "offline"}

    async def start_app(self, app: str, script: str | None = None) -> dict[str, Any]:
        app = app.strip().strip("/")
        script_name = (script or DEFAULT_SCRIPT).strip().lstrip("/")
        if not script_name.endswith((".js", ".json", ".sh")):
            if (self.home / "api" / app / f"{script_name}.json").exists():
                script_name = f"{script_name}.json"
            elif (self.home / "api" / app / f"{script_name}.js").exists():
                script_name = f"{script_name}.js"

        resp = await self.request("GET", f"/api/{app}/{script_name}")
        return {
            "app": app,
            "script": script_name,
            "status_code": resp.status_code,
            "launched": resp.status_code < 500,
        }

    async def stop_app(self, app: str, script: str | None = None) -> dict[str, Any]:
        """Best-effort stop via ?stop=true (Pinokio UI uses WebSocket rpc after page load)."""
        app = app.strip().strip("/")
        status = await self.app_status(app)
        targets = status.get("scripts") or []
        if script:
            needle = script.strip().lstrip("/")
            targets = [
                t
                for t in targets
                if isinstance(t, dict)
                and (
                    needle in str(t.get("script_path") or "")
                    or needle in str(t.get("path") or "")
                )
            ]

        if not targets:
            return {
                "app": app,
                "stopped": [],
                "message": "No running scripts found for this app",
            }

        stopped: list[dict[str, Any]] = []
        for item in targets:
            if not isinstance(item, dict):
                continue
            rel = str(item.get("path") or "")
            script_path = str(item.get("script_path") or "")
            api_path = rel if rel else f"{app}/{script_path}"
            resp = await self.request("GET", f"/api/{api_path}", params={"stop": "true"})
            stopped.append(
                {
                    "path": api_path,
                    "status_code": resp.status_code,
                }
            )

        return {
            "app": app,
            "stopped": stopped,
            "message": (
                "Stop signal sent via HTTP. Pinokio may require the desktop UI/WebSocket "
                "to fully terminate processes — verify in Pinokio if scripts remain."
            ),
        }

    async def delete_app(self, app: str) -> dict[str, Any]:
        app = app.strip().strip("/")
        resp = await self.request("POST", "/pinokio/delete", json_body={"name": app})
        data: dict[str, Any] = {}
        try:
            payload = resp.json()
            if isinstance(payload, dict):
                data = payload
        except json.JSONDecodeError:
            data = {"raw": resp.text[:500]}
        if data.get("error"):
            raise PinokioAPIError(str(data["error"]))
        deleted = data.get("success", resp.status_code == 200)
        return {"app": app, "deleted": deleted, "response": data}

    async def localhost_search(self) -> list[dict[str, Any]]:
        info = await self.get_info()
        proxies = info.get("proxies") or []
        return [p for p in proxies if isinstance(p, dict)]

    async def remote_start(
        self,
        host: str,
        port: int,
        app: str,
        script: str | None = None,
    ) -> dict[str, Any]:
        app = app.strip().strip("/")
        script_name = (script or DEFAULT_SCRIPT).strip().lstrip("/")
        url = f"http://{host}:{port}/api/{app}/{script_name}"
        http = await self._get_http()
        resp = await http.get(url, timeout=self.timeout)
        return {
            "host": host,
            "port": port,
            "app": app,
            "script": script_name,
            "status_code": resp.status_code,
            "launched": resp.status_code < 500,
        }


def _env_int(name: str) -> int | None:
    raw = (os.getenv(name) or "").strip()
    if not raw:
        return None
    try:
        return int(raw)
    except ValueError:
        return None


def _read_pinokio_js_meta(pinokio_js: Path) -> dict[str, str]:
    if not pinokio_js.is_file():
        return {}
    try:
        text = pinokio_js.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return {}
    meta: dict[str, str] = {}
    if m := _TITLE_RE.search(text):
        meta["title"] = m.group(1)
    if m := _DESC_RE.search(text):
        meta["description"] = m.group(1)
    return meta


class PinokioError(Exception):
    """Base Pinokio client error."""


class PinokioOfflineError(PinokioError):
    """Pinokio daemon is not reachable."""


class PinokioAPIError(PinokioError):
    """Pinokio returned an error response."""
