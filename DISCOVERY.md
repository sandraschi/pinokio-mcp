# Pinokio API Discovery

Reverse-engineered from [pinokiod](https://github.com/pinokiocomputer/pinokiod) (`server/index.js`).

## Transport

- HTTP server on **42000** (falls forward through **42059** if busy)
- Health: `GET /check` → 200 when pinokiod is up
- No auth on localhost

## Core endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/check` | Daemon health |
| GET | `/pinokio/info` | System state: `api`, `scripts`, `proxies`, `home`, `version` |
| GET | `/pinokio/port` | Current port `{ result: N }` |
| GET | `/pinokio/launch/:name` | Open app launcher UI |
| GET | `/api/:app/:script` | Run Pinokio script (e.g. `start.js`) |
| GET | `/api/:app/:script?stop=true` | UI stop flow (WebSocket `kernel.api.stop` in browser) |
| POST | `/pinokio/delete` | Body `{ "name": "<app-folder>" }` |
| GET | `/proxy` | Proxied localhost services (HTML) |
| POST | `/proxy` | Start/stop proxy `{ action, name, target, port }` |

## Home discovery (Windows)

1. `PINOKIO_HOME` env
2. `%APPDATA%\Pinokio\config.json` → `home` key
3. `~/pinokio`

## Port discovery

1. `PINOKIO_PORT` env
2. Scan `42000-42059` for `GET /check`

## Offline fallback

When pinokiod is down, `app_management(list)` reads `~/pinokio/api/*/pinokio.js` metadata from disk.

## LAN Wide Web

- mDNS browse `_pinokio._tcp.local.` and `_http._tcp.local.` (ports 42000-42059)
- Verify candidates with `GET /check`
- Remote start: `GET http://{host}:{port}/api/{app}/{script}`

## Limitations

- **Stop** is WebSocket-driven in the Pinokio UI; HTTP `?stop=true` is best-effort only
- **Install** flows use browser redirects (`/pinokio/install`) — not exposed in MCP v1
