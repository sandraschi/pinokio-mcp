"""Pydantic models for Pinokio API responses."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class PinokioApp(BaseModel):
    path: str
    title: str | None = None
    description: str | None = None
    icon: str | None = None
    running: bool = False
    running_scripts: list[dict[str, Any]] = Field(default_factory=list)
    source: str = "api"


class PinokioScript(BaseModel):
    path: str
    app: str
    script_path: str
    step: Any | None = None
    full_path: str | None = None


class PinokioProxy(BaseModel):
    name: str | None = None
    target: str | None = None
    port: int | None = None
    proxy: str | None = None
    running: bool = False
    app: str | None = None
    path: str | None = None


class PinokioDevice(BaseModel):
    name: str
    host: str
    port: int
    properties: dict[str, str] = Field(default_factory=dict)


class ToolResponse(BaseModel):
    success: bool
    message: str
    data: dict[str, Any] = Field(default_factory=dict)
    suggestions: list[str] = Field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "success": self.success,
            "message": self.message,
        }
        if self.data:
            out["data"] = self.data
        if self.suggestions:
            out["suggestions"] = self.suggestions
        return out
