# Pinokio-MCP user guide

Control your local Pinokio AI apps from Claude or Cursor: list what is
installed, start and stop apps, find their web URLs, and reach Pinokio on
other machines on your LAN. This guide covers setup, everyday workflows,
and what to do when things fail.

## 1. What you need

- The Pinokio desktop app installed and able to start (https://pinokio.co).
  The MCP server talks to it over localhost HTTP; without Pinokio running,
  only `list` works (it reads the install folders from disk).
- A Claude Desktop (or Cursor) MCP client with this server registered:

```json
{
  "mcpServers": {
    "pinokio": {
      "command": "uvx",
      "args": ["pinokio-mcp"],
      "env": { "PINOKIO_HOST": "localhost" }
    }
  }
}
```

- Optional environment overrides: `PINOKIO_PORT` pins a port instead of
  auto-scanning 42000-42059; `PINOKIO_HOME` pins the install directory
  instead of reading `%APPDATA%\Pinokio\config.json` (Windows) or falling
  back to `~/pinokio`.

## 2. Verify the setup

Ask your agent, in order:

1. `system_management(action="ping")` — expect `online: true` and a port.
   `online: false` means Pinokio is not running: start the desktop app.
2. `app_management(action="list")` — expect your installed apps with
   `running: false` and `"source": "api"`. `"source": "filesystem"`
   means the daemon is down and the list came from disk: titles are
   present but nothing about running state can be trusted.
3. `system_management(action="info")` — expect `home`, `platform`,
   `version`, plus `scripts` (usually empty when idle) and `proxies`.

If step 1 fails, check: is Pinokio actually open (not just installed)?
Is something else on port 42000? Did you set a wrong `PINOKIO_PORT`?
The repo's `scripts/discover-api.ps1` probes the same surface from
PowerShell if you want a second opinion outside the agent.

## 3. Everyday workflows

### 3.1 Start an app and open it

1. `app_management(action="list")` — find the folder, e.g. `comfy.git`.
2. `app_management(action="status", app="comfy.git")` — confirm stopped.
3. `app_management(action="start", app="comfy.git", script="start.js")` —
   the default script is `start.js`, so you can omit it.
4. `system_management(action="localhost_search")` — copy the proxied URL
   into your browser.
5. When done: `app_management(action="stop", app="comfy.git")`, then
   `status` again to confirm the scripts are gone. If scripts remain,
   finish them in the Pinokio UI: HTTP stop is best-effort by design.

First launch of an app can take a long time (model downloads of tens of
gigabytes) and needs GPU memory free. Ask the agent to check
`AVAILABLE_APPS.md` first: it records which apps actually have weights
downloaded versus bare environments.

### 3.2 Check what is running

- `pinokio://running` resource, or
  `app_management(action="list")` and look for `"running": true` plus the
  `running_scripts` entries.
- `system_management(action="localhost_search")` shows every proxied
  service with its target port — the fastest way to find URLs.

### 3.3 Work queues across apps

Start one GPU-heavy app at a time. If you queue two video generators,
the second will crawl or crash on out-of-memory. The agent should `stop`
the current app and confirm `running: false` before starting the next.

### 3.4 Reach a second machine

1. `lww_management(action="devices")` — wait a few seconds for mDNS plus
   `/check` verification; expect `host:port` entries.
2. `lww_management(action="start_remote", device="192.168.1.10:42000", app="comfy.git")`.
3. Open `http://192.168.1.10:<port>` from the device list in a browser.
   Remote start launches; it does not report the proxied URL, so confirm
   it in that machine's Pinokio UI or via its own `localhost_search`.

### 3.5 Delete an app you no longer use

1. `app_management(action="status", app="<folder>")` — stop it first if running.
2. Confirm explicitly with the human in-session (deletion removes the
   environment and all downloaded weights, typically 5-25 GB, and is not
   undoable except by reinstalling).
3. `app_management(action="delete", app="<folder>")` — expect
   `"deleted": true` in `data`.

## 4. Understanding answers

Every tool answers `{success, message, data?, suggestions?}`. `message` is
the sentence to show the human; `data` is the machine payload; `suggestions`
lists sensible next steps (for example, "list first" after an unknown app
name). App folders end in `.git` by Pinokio convention (`comfy.git`,
`wan.git`) — always use the full folder name, not the display title.

## 5. Troubleshooting FAQ

**"Pinokio is not running" but it is open.** The daemon may be on a
non-default port (auto-scan covers 42000-42059) or bound to a restart. Run
`ping` again; if it persists, restart Pinokio and check nothing else holds
42000.

**`status` shows running scripts I never started.** Pinokio resumes
scripts across restarts. `stop` the app, verify with `status`, and clear
leftovers in the UI.

**Stop says sent but scripts remain.** Expected limitation: HTTP stop is
best-effort; the authoritative stop is the Pinokio UI's WebSocket flow.
The tool says this in its own message — believe it.

**An app folder exists but the agent says weights are missing.** Folders
prove installation, not downloads. `AVAILABLE_APPS.md` is the verified
inventory; a first `start` downloads whatever is missing (slow, large).

**`devices` is empty but Pinokio runs here.** mDNS may be blocked on this
network. Localhost probing still covers 127.0.0.1; remote boxes need
real mDNS or an explicit `device` + `port` on `start_remote`.

**Install a brand-new app.** Not exposed in MCP v1 (browser-redirect
flow): do it in the Pinokio UI, then manage it here.

## 6. Configuration and limits

Environment: `PINOKIO_HOST` (default localhost), `PINOKIO_PORT`
(auto-discover 42000-42059 when empty), `PINOKIO_HOME` (auto-discover
when empty). No accounts, no tokens. Timeouts: 15 s per request, 3 s LAN
discovery, 2 s per LAN verification probe.

Hard limits: no install flow, no inbound access point, no guaranteed
remote stop, no filing or uploading anywhere. Everything is local-first;
the only network traffic is localhost HTTP plus LAN mDNS/HTTP for
`devices` and `start_remote`.

## 7. For the curious: how detection works

Port discovery probes `GET /check` across 42000-42059 with a 0.75 s
per-port timeout, concurrently. Home discovery reads `PINOKIO_HOME`, then
`%APPDATA%\Pinokio\config.json`, then `~/pinokio`. Offline `list` parses
each `<home>/api/*/pinokio.js` for its `title:` and `description:` fields.
LAN discovery browses `_pinokio._tcp.local.` and `_http._tcp.local.` via
mDNS, verifies each candidate with `GET /check`, and falls back to probing
the localhost range when mDNS yields nothing. Start resolves a bare
script name to `.json` then `.js` on disk before calling
`GET /api/{app}/{script}`; stop calls the same URL with `?stop=true`.

## 8. Installed-app quick cards (re-surveyed 2026-11-25)

Folder names are what `app` arguments take. Sizes are approximate install
footprints including environments and weights.

- **`comfy.git`** (~5GB) — Pinokio's ComfyUI wrapper. Note: a separate
  direct ComfyUI install may already be in active use on this machine
  (`D:\ComfyUI`); prefer whichever one is maintained and stop the other
  before heavy work so they don't fight over GPU memory.
- **`diffrhythm.git`** (~18GB) — songs up to ~4m45s, lyrics or
  instrumental. Good first music pick: mid-size, self-contained.
- **`Frame-Pack.git`** (~27GB) — progressive next-frame-section video
  generation (HunyuanVideo family). Needs substantial VRAM; close other
  GPU apps first.
- **`lingbot-world-pinokio.git`** (~5GB) — purpose-built world model for
  image-to-video, valued for spatial/physical consistency. Untested here;
  treat first runs as experiments.
- **`SongGeneration-Studio.git`** (~16GB) — full songs with lyrics,
  vocals, instrumental, and style control. The studio UI of the music options.
- **`StyleAligned.pinokio.git`** (~12GB) — style-consistent image
  generation via shared attention. Needs a style reference image.
- **`wan.git`** (~5GB) — Wan 2.1 video generation, tuned for GPU-poor
  machines. Proven working on this install.
- **`zonos.git`** (~5GB) — open-weight multilingual text-to-speech
  (Zonos-v0.1, 200k+ training hours). Smallest serious app here.
- **`deeperhermes.git`** (~0GB) — essentially empty, failed or abandoned
  install. Do not try to run it; delete or reinstall if the model is
  ever wanted.

Before promising any app works, cross-check `AVAILABLE_APPS.md`: folders
prove installation, only downloaded weights prove readiness (an app can
be a 6GB environment with zero model checkpoints).

## 9. Uninstall walkthrough (reclaim 5-27GB per app)

1. `app_management(action="status", app="<folder>")` — must show
   `running: false`. If not, `stop` it and re-check.
2. Say which app and how much space it holds, and get an explicit yes.
   There is no undo except reinstalling and re-downloading weights.
3. `app_management(action="delete", app="<folder>")` — expect
   `"deleted": true`.
4. Optionally delete the now-empty folder remnant in `D:/pinokio/api`
   if Pinokio left one, and update `AVAILABLE_APPS.md` so the next
   session does not offer a ghost app.

## 10. Backup guidance

Back up outputs, not environments: the `output/` or `user/` folders
inside an app directory hold your creations; `env/` (Python virtualenv,
multi-GB) and `hf_download/` (model weights, tens of GB) are
re-downloadable and safe to exclude from backups. The one exception is
metered or removed models — if a weight file can no longer be fetched,
treat its folder like an output and back it up.

## 11. Repo scripts reference

- `scripts/discover-api.ps1` — probes the Pinokio HTTP surface
  (`/check`, `/pinokio/info`) independent of this MCP server. Use it
  when the agent and the daemon disagree about reachability.
- `scripts/test_tools.py` — exercises the MCP tools against a live
  daemon. Needs Pinokio running; read-only except for `start`/`stop`
  on the app you point it at.
- `scripts/gen-prompt-examples.py` — regenerates
  `mcpb/assets/prompts/examples.json` from real tool shapes and the
  current app inventory. Re-run after any tool-surface change.
- `scripts/mcpb-pack.ps1` — fleet-shim pack entry (`just mcpb-pack`).
- `start.ps1` / `start.bat` — stdio launcher for Claude Desktop;
  `web_sota/start.ps1` + `web_sota/catalog.html` — static catalog page
  via the fleet launcher (no dev server, no backend).

## 12. Extended FAQ

**Which app for a quick 3D model from one photo?** None of the current
nine is a 3D app (the 3D installs were pruned). Say so rather than
forcing a video model into the job.

**Which music app?** `SongGeneration-Studio.git` for full songs with a
UI, `diffrhythm.git` for quick lyrics-or-instrumental pieces.

**Which video app on a weak GPU?** `wan.git` first (tuned for GPU-poor
machines and proven here); `Frame-Pack.git` only with VRAM to spare.

**Text-to-speech?** `zonos.git`. Multilingual, small, proven weights.

**The agent says an app is running that I never started.** Pinokio
resumes scripts across restarts. `status` the app, `stop` it, verify.

**Two apps fight over the GPU.** Stop one and confirm `running: false`
before starting the other. `localhost_search` shows what is actually
proxied right now.

**How do I know a first launch is stuck vs downloading?** First launches
download weights (tens of GB, slow). Check the app's folder for growing
files under `hf_download/` or the model dir; no growth plus no error for
30+ minutes means a stuck script — stop it and retry.

**Can the agent install new apps?** No (MCP v1 has no install flow).
Install in the Pinokio UI, then hand the folder name to the agent.

**Where do URLs come from?** `localhost_search` (local) or the remote
machine's own search (remote). The agent should hand you a clickable
`http://localhost:<port>` style URL, not a description of one.
