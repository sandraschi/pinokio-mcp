# pinokio-mcp — Claude Code Guide

MCP server for controlling Pinokio — the 1-click localhost cloud for AI apps.

## Entry Points
- `uv run pinokio-mcp` → `pinokio_mcp.server:main`

## Standards
- FastMCP 3.4+ tools
- Dual transport: stdio + HTTP
- See mcp-central-docs for fleet-wide coding standards

## Quick Ref
```powershell
uv run pinokio-mcp
uv run pytest tests/ -q
```
