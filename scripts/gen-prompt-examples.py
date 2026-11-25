"""Generate mcpb/assets/prompts/examples.json from real tool shapes.

Regenerate after any tool-surface change:
    uv run python scripts/gen-prompt-examples.py
Entries use real installed app folder names and cover success paths,
validation errors, and offline behavior. Expected outcomes describe the
contract, not recorded live traffic.
"""

from __future__ import annotations

import json
from pathlib import Path

APPS = [
    "comfy.git",
    "Frame-Pack.git",
    "wan.git",
    "zonos.git",
    "diffrhythm.git",
    "SongGeneration-Studio.git",
    "StyleAligned.pinokio.git",
    "lingbot-world-pinokio.git",
    "deeperhermes.git",
]

EXAMPLES: list[dict] = []


def add(tool: str, arguments: dict, expected: str, when: str) -> None:
    EXAMPLES.append({"tool": tool, "arguments": arguments, "when": when, "expected": expected})


def build() -> list[dict]:
    # --- app_management: list (offline + online + invalid-arg shapes) ---
    add(
        "app_management",
        {"action": "list"},
        "success=true with apps[] (source api or filesystem) and pinokio_online flag",
        "Pinokio running or not; always safe to call first",
    )
    add(
        "app_management",
        {"action": "LiSt"},
        "actions are case-normalized, same as list",
        "verifying case-insensitivity",
    )
    add(
        "app_management",
        {"action": "nope"},
        "client-side Literal validation error before any network call",
        "typo in the action discriminator",
    )
    for app in APPS:
        add(
            "app_management",
            {"action": "status", "app": app},
            f"success=true with running/scripts/source for {app} (offline: running=false, source=offline)",
            f"checking {app} before starting it",
        )
    # --- app_management: start variants, every installed app ---
    for app in APPS:
        add(
            "app_management",
            {"action": "start", "app": app},
            f"launched=true and 2xx status_code when Pinokio runs {app}; offline error naming the daemon when down",
            f"launching {app} with the default start.js",
        )
    add(
        "app_management",
        {"action": "start", "app": "comfy.git", "script": "start.js"},
        "explicit script resolves on disk then launches via GET /api/comfy.git/start.js",
        "pinning the script name explicitly",
    )
    add(
        "app_management",
        {"action": "start", "app": "comfy.git", "script": "custom"},
        "bare name resolves to custom.json then custom.js before the HTTP call",
        "custom script without extension",
    )
    for app in ["wan.git", "zonos.git", "diffrhythm.git"]:
        add(
            "app_management",
            {"action": "start", "app": app, "script": "start.js"},
            f"explicit start.js for {app}; first launch may download tens of GB of weights",
            f"first-time launch warning path for {app}",
        )
    add(
        "app_management",
        {"action": "start"},
        "success=false with message naming the missing app parameter",
        "forgotten app argument",
    )
    add(
        "app_management",
        {"action": "start", "app": "  "},
        "blank app treated as missing, suggestions point at list",
        "whitespace-only app argument",
    )
    # --- app_management: stop every installed app ---
    for app in APPS:
        add(
            "app_management",
            {"action": "stop", "app": app},
            f"stopped[] paths that received ?stop=true plus the best-effort warning; verify {app} with status",
            f"stopping {app} after work",
        )
    add(
        "app_management",
        {"action": "stop", "app": "comfy.git", "script": "start.js"},
        "script filter narrows targets to matching script_path entries",
        "stopping one script of a multi-script app",
    )
    # --- app_management: delete (destructive, confirm first) ---
    for app in ["zonos.git", "diffrhythm.git", "deeperhermes.git"]:
        add(
            "app_management",
            {"action": "delete", "app": app},
            "requires explicit user confirmation first; deleted=true removes env and weights",
            f"pruning unused {app} (destructive — confirm in session)",
        )
    add(
        "app_management",
        {"action": "delete", "app": "missing.git"},
        "Pinokio API error surfaced as success=false with the daemon message",
        "deleting a folder that is not installed",
    )
    # --- system_management ---
    add(
        "system_management",
        {"action": "ping"},
        "online true/false with host, port, and resolved home; never raises when down",
        "health check before any mutating call",
    )
    add(
        "system_management",
        {"action": "info"},
        "home/platform/arch/version plus scripts/proxies/api arrays; offline raises PinokioOfflineError",
        "inventorying a running daemon",
    )
    for field in ["home", "version", "scripts", "proxies", "api"]:
        add(
            "system_management",
            {"action": "info"},
            f"info.data carries {field} from GET /pinokio/info",
            f"spot-checking the {field} field",
        )
    add(
        "system_management",
        {"action": "localhost_search"},
        "proxied services for opening URLs; empty list when nothing is proxied",
        "finding app URLs to hand to the user",
    )
    add(
        "system_management",
        {"action": "bogus"},
        "client-side Literal validation error",
        "typo in the system action",
    )
    # --- lww_management: devices ---
    add(
        "lww_management",
        {"action": "devices"},
        "verified host:port instances after mDNS plus /check; empty list when none reachable",
        "looking for LAN peers",
    )
    add(
        "lww_management",
        {"action": "bogus"},
        "client-side Literal validation error",
        "typo in the LAN action",
    )
    # --- lww_management: start_remote matrix ---
    for app in APPS:
        add(
            "lww_management",
            {"action": "start_remote", "device": "192.168.1.10:42000", "app": app},
            f"launched=true when the remote answers 2xx for {app}",
            f"remote start of {app} with explicit host:port",
        )
    add(
        "lww_management",
        {"action": "start_remote", "device": "192.168.1.10", "port": 42001, "app": "wan.git"},
        "bare host plus separate port composes the same remote URL",
        "remote start with split host/port",
    )
    add(
        "lww_management",
        {"action": "start_remote", "device": "not a host!!!", "app": "comfy.git"},
        "transport error surfaced as success=false, no retry storm",
        "unreachable device address",
    )
    add(
        "lww_management",
        {"action": "start_remote", "app": "comfy.git"},
        "success=false asking for device as host:port with a devices hint",
        "forgotten device argument",
    )
    add(
        "lww_management",
        {"action": "start_remote"},
        "success=false naming the missing app parameter",
        "forgotten app argument",
    )
    add(
        "lww_management",
        {"action": "start_remote", "device": "192.168.1.10:abc", "app": "comfy.git"},
        "unparseable port falls back to the explicit port arg or errors asking for host:port",
        "garbage port segment",
    )
    # --- system_management ---
    add(
        "system_management",
        {"action": "ping"},
        "online true/false with host, port, and resolved home; never raises when down",
        "health check before any mutating call",
    )
    add(
        "system_management",
        {"action": "info"},
        "home/platform/arch/version plus scripts/proxies/api arrays; offline raises PinokioOfflineError",
        "inventorying a running daemon",
    )
    add(
        "system_management",
        {"action": "localhost_search"},
        "proxied services for opening URLs; empty list when nothing is proxied",
        "finding app URLs to hand to the user",
    )
    add(
        "system_management",
        {"action": "bogus"},
        "client-side Literal validation error",
        "typo in the system action",
    )
    # --- lww_management: devices ---
    add(
        "lww_management",
        {"action": "devices"},
        "verified host:port instances after mDNS plus /check; empty list when none reachable",
        "looking for LAN peers",
    )
    # --- lww_management: start_remote matrix ---
    add(
        "lww_management",
        {"action": "start_remote", "device": "192.168.1.10:42000", "app": "comfy.git"},
        "launched=true when the remote answers 2xx",
        "remote start with explicit host:port",
    )
    add(
        "lww_management",
        {"action": "start_remote", "device": "192.168.1.10", "port": 42001, "app": "wan.git"},
        "bare host plus separate port composes the same remote URL",
        "remote start with split host/port",
    )
    add(
        "lww_management",
        {"action": "start_remote", "device": "not a host!!!", "app": "comfy.git"},
        "transport error surfaced as success=false, no retry storm",
        "unreachable device address",
    )
    add(
        "lww_management",
        {"action": "start_remote", "app": "comfy.git"},
        "success=false asking for device as host:port with a devices hint",
        "forgotten device argument",
    )
    add(
        "lww_management",
        {"action": "start_remote"},
        "success=false naming the missing app parameter",
        "forgotten app argument",
    )
    add(
        "lww_management",
        {"action": "start_remote", "device": "192.168.1.10:abc", "app": "comfy.git"},
        "unparseable port falls back to the explicit port arg or errors asking for host:port",
        "garbage port segment",
    )
    # --- resources (read via MCP resource URIs, same backing calls) ---
    add(
        "resource",
        {"uri": "pinokio://apps"},
        "same payload as app_management list",
        "dashboard snapshot without a tool call",
    )
    add(
        "resource",
        {"uri": "pinokio://running"},
        "scripts plus online flag; offline yields empty scripts and online=false",
        "polling what is active",
    )
    add(
        "resource",
        {"uri": "pinokio://localhost"},
        "proxied services plus online flag",
        "URL discovery for the user",
    )
    add(
        "resource",
        {"uri": "pinokio://lww/devices"},
        "verified LAN instances with decoded properties",
        "peer overview before remote starts",
    )
    # --- prompts (priming text the server ships) ---
    add(
        "prompt",
        {"name": "prompt_start_workflow"},
        "numbered ping/list/launch/localhost_search sequence",
        "priming a fresh agent for the standard flow",
    )
    add(
        "prompt",
        {"name": "prompt_cross_device"},
        "devices-then-start_remote sequence",
        "priming a fresh agent for remote work",
    )
    add(
        "prompt",
        {"name": "prompt_troubleshooting"},
        "offline/wrong-home/partial-stop guidance plus live probe scripts",
        "priming a fresh agent for failure modes",
    )
    add(
        "prompt",
        {"name": "prompt_available_apps"},
        "pointer at AVAILABLE_APPS.md: folders alone prove nothing, weights matter",
        "reminding agents that list output is not readiness proof",
    )
    # --- error taxonomy (offline daemon) ---
    add(
        "app_management",
        {"action": "status", "app": "comfy.git"},
        "offline: running=false, scripts=[], source=offline (no raise)",
        "status with the daemon down",
    )
    add(
        "app_management",
        {"action": "start", "app": "comfy.git"},
        "offline: PinokioOfflineError naming ports 42000-42059 plus start hints",
        "start with the daemon down",
    )
    add(
        "app_management",
        {"action": "delete", "app": "comfy.git"},
        "offline: PinokioOfflineError before any destructive step (safe failure mode)",
        "delete with the daemon down",
    )
    add(
        "app_management",
        {"action": "stop", "app": "comfy.git"},
        "offline status lookup yields no targets; message says nothing is running",
        "stop with the daemon down",
    )
    add(
        "system_management",
        {"action": "info"},
        "offline: PinokioOfflineError, not an empty payload",
        "info with the daemon down",
    )
    add(
        "system_management",
        {"action": "localhost_search"},
        "offline: PinokioOfflineError, not an empty payload",
        "proxy search with the daemon down",
    )
    # --- envelope contract ---
    for tool in ["app_management", "system_management", "lww_management"]:
        add(
            tool,
            {
                "action": "list"
                if tool == "app_management"
                else ("ping" if tool == "system_management" else "devices")
            },
            "envelope always carries success (bool) and message (human sentence)",
            f"asserting the dialogic contract on {tool}",
        )
    add(
        "app_management",
        {"action": "status", "app": "demo-app"},
        "unknown folder returns offline record, never throws",
        "status for a folder that was uninstalled",
    )
    add(
        "system_management",
        {"action": "ping"},
        "PINOKIO_PORT set pins discovery; empty means scan 42000-42059",
        "documenting the port override",
    )
    add(
        "app_management",
        {"action": "list"},
        "PINOKIO_HOME set pins the filesystem fallback root",
        "documenting the home override",
    )
    add(
        "prompt",
        {"name": "prompt_available_apps"},
        "cross-checks list output against AVAILABLE_APPS.md weights inventory",
        "verifying an app is actually usable before promising it",
    )
    add(
        "app_management",
        {"action": "list"},
        "folders alone prove installation; AVAILABLE_APPS.md proves readiness",
        "listing is not a readiness proof",
    )
    return EXAMPLES


def main() -> None:
    out = Path(__file__).resolve().parent.parent / "mcpb" / "assets" / "prompts" / "examples.json"
    out.write_text(json.dumps(build(), indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(EXAMPLES)} examples to {out}")


if __name__ == "__main__":
    main()
