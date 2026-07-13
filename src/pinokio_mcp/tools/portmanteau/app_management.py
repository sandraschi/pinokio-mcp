"""App lifecycle operations."""

from __future__ import annotations

from typing import Any, Literal

from pinokio_mcp.client import PinokioAPIError, PinokioClient, PinokioOfflineError
from pinokio_mcp.models import ToolResponse


async def app_management(
    client: PinokioClient,
    action: Literal["list", "status", "start", "stop", "delete"],
    app: str | None = None,
    script: str | None = None,
) -> dict[str, Any]:
    action = action.strip().lower()  # type: ignore[assignment]

    try:
        if action == "list":
            apps = await client.list_apps()
            online = await client.ping()
            return ToolResponse(
                success=True,
                message=f"Found {len(apps)} app(s)",
                data={"apps": apps, "pinokio_online": online, "home": str(client.home)},
            ).to_dict()

        if not app or not app.strip():
            return ToolResponse(
                success=False,
                message="Parameter 'app' is required for this action",
                suggestions=["Call app_management(action='list') to see installed apps"],
            ).to_dict()

        if action == "status":
            status = await client.app_status(app)
            return ToolResponse(success=True, message=f"Status for {app}", data=status).to_dict()

        if action == "start":
            result = await client.start_app(app, script=script)
            return ToolResponse(
                success=bool(result.get("launched")),
                message=f"Start requested for {app}",
                data=result,
            ).to_dict()

        if action == "stop":
            result = await client.stop_app(app, script=script)
            stopped = result.get("stopped") or []
            return ToolResponse(
                success=True,
                message=str(result.get("message") or f"Stop requested for {app}"),
                data=result,
                suggestions=[] if stopped else ["App may not be running"],
            ).to_dict()

        if action == "delete":
            result = await client.delete_app(app)
            return ToolResponse(
                success=bool(result.get("deleted")),
                message=f"Deleted {app}" if result.get("deleted") else f"Delete failed for {app}",
                data=result,
            ).to_dict()

        return ToolResponse(
            success=False,
            message=f"Unknown action: {action}",
            suggestions=["Use list, status, start, stop, or delete"],
        ).to_dict()

    except PinokioOfflineError as exc:
        if action == "list":
            apps = client._list_apps_filesystem()  # noqa: SLF001
            return ToolResponse(
                success=True,
                message=f"Pinokio offline — listed {len(apps)} app(s) from filesystem",
                data={"apps": apps, "pinokio_online": False, "home": str(client.home)},
                suggestions=[str(exc)],
            ).to_dict()
        return ToolResponse(
            success=False,
            message=str(exc),
            suggestions=[
                "Start Pinokio desktop app",
                "Set PINOKIO_PORT if Pinokio uses a non-default port",
            ],
        ).to_dict()
    except PinokioAPIError as exc:
        return ToolResponse(success=False, message=str(exc)).to_dict()
    except Exception as exc:  # noqa: BLE001
        return ToolResponse(success=False, message=f"Unexpected error: {exc}").to_dict()
