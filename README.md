# pinokio-mcp

MCP server for controlling [Pinokio](https://pinokio.co) - the 1-click localhost cloud for AI apps.

## Quick start

```powershell
cd D:\Dev\repos\pinokio-mcp
uv sync
uv run pinokio-mcp
```

Or via fleet launcher: `mcp-central-docs\starts\pinokio-start.bat`

## Cursor / Claude MCP config

```json
{
  "mcpServers": {
    "pinokio": {
      "command": "uv",
      "args": ["--directory", "D:/Dev/repos/pinokio-mcp", "run", "pinokio-mcp"],
      "env": {
        "PINOKIO_HOST": "localhost"
      }
    }
  }
}
```

## Tools

| Tool | Operations |
|------|------------|
| `app_management` | `list`, `status`, `start`, `stop`, `delete` |
| `system_management` | `ping`, `info`, `localhost_search` |
| `lww_management` | `devices`, `start_remote` |

## What's actually installed

`app_management(action="list")` tells you an app exists and whether it's running - it doesn't tell you whether that app has any real model weights downloaded (some apps here are just an empty environment). See **[AVAILABLE_APPS.md](AVAILABLE_APPS.md)** for a real, hand-verified inventory of what's here, what it's good for, and where to start.

## Environment

| Variable | Default | Description |
|----------|---------|-------------|
| `PINOKIO_HOST` | `localhost` | Pinokio host |
| `PINOKIO_PORT` | auto | Pinokio port (scan 42000-42059) |
| `PINOKIO_HOME` | auto | Pinokio home (`config.json` on Windows) |

## Verify

```powershell
.\scripts\discover-api.ps1
uv run python scripts\test_tools.py
uv run pytest
```

## API notes

See [DISCOVERY.md](DISCOVERY.md). Stop via HTTP is best-effort; Pinokio UI WebSocket completes termination.

## License

MIT
