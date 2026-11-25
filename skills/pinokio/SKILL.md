# Pinokio-MCP domain skill

Control Pinokio (1-click localhost AI app launcher) through this repo's MCP tools.
Pinokio itself must be running for start/stop/delete; `list` works offline via the filesystem.

## Who does what

- Agent (you): discover apps, check status, launch, monitor, stop. Never delete an app without the user's explicit go — `delete` removes 5-25 GB and its models.
- Human: starts/stops the Pinokio desktop app, confirms deletions, uses untested apps from `AVAILABLE_APPS.md`.

## Tool catalog (real operations)

- `app_management(action=...)` — `list` (installed apps + running state + home path), `status` (needs `app`), `start` (needs `app`, optional `script`, default `start.js`), `stop` (needs `app`, optional `script`; best-effort over HTTP, verify in Pinokio UI), `delete` (needs `app`; explicit user confirmation first).
- `system_management(action=...)` — `ping` (reachability + port + home), `info` (version, scripts, proxies, api list), `localhost_search` (proxied local services).
- `lww_management(action=...)` — `devices` (zeroconf + /check-verified LAN instances), `start_remote` (needs `device` as `host:port`, `app`, optional `script`/`port`).
- Resources: `pinokio://apps`, `pinokio://running`, `pinokio://localhost`, `pinokio://lww/devices`.
- Prompts: start workflow, cross-device orchestration, troubleshooting, available-apps inventory pointer.

All tools return `{success, message, data?, suggestions?}`. `message` is human-readable; `suggestions` lists next steps.

## Workflows

### 1. Launch something and get its URL
1. `system_management(action="ping")` — if offline, tell the user to start Pinokio (ports 42000-42059) and stop.
2. `app_management(action="list")` — pick the app folder (e.g. `comfy.git`).
3. `app_management(action="start", app="<folder>")` — note `launched` in `data`.
4. `system_management(action="localhost_search")` — hand the user the proxied URL.
5. At end of work: `app_management(action="stop", app="<folder>")`.

### 2. Check what is actually usable
`app_management(action="list")` tells you an app exists — not whether its model weights are downloaded. Cross-check `AVAILABLE_APPS.md` (hand-verified inventory, re-surveyed 2026-11-25) before promising an app works.

### 3. Remote start on another machine
1. `lww_management(action="devices")` — pick `host:port`.
2. `lww_management(action="start_remote", device="<host:port>", app="<folder>")`.

## Troubleshooting

- Offline (`Pinokio is not running`): start the Pinokio desktop app; discovery scans ports 42000-42059 for `GET /check`.
- Wrong home: set `PINOKIO_HOME`, or check `%APPDATA%\Pinokio\config.json` on Windows.
- Stop incomplete: HTTP stop is best-effort (Pinokio needs its UI/WebSocket to kill stubborn scripts) — verify in Pinokio, do not retry blindly.
- Live probes: `scripts/discover-api.ps1`, `scripts/test_tools.py`.

## Config

`PINOKIO_HOST` (default localhost), `PINOKIO_PORT` (auto-discover if empty), `PINOKIO_HOME` (auto-discover if empty). No secrets, no auth on localhost.
