# Changelog

## [Unreleased]

### Fixed
- Tool-surface docs named tools that do not exist (`.cursorrules`, `llms.txt`, `llms-full.txt` listed `discover_apps`/`launch_app`/etc.); corrected to the real portmanteau tools. Removed false "Dual transport: stdio + HTTP" claim (stdio only).
- `mcpb/manifest.json`: `${PWD}` replaced with `${__dirname}` (bundle now starts on real installs); all three tools listed with real descriptions.
- Added `src/pinokio_mcp/__main__.py` so the manifest's `python -m pinokio_mcp` entry works.
- `pyproject.toml`: `[dependency-groups]` dev (fixes `uv sync --group dev` and fresh-clone `just lint`/`test`); T20 print-ban enabled; pytest-cov gate (`--cov-fail-under=50`).
- Tool docstrings: `## Return Format` + `## Examples`; `Annotated` params with descriptions; tool annotations (mutating vs read-only); `output_schema`.
- Logging: `logging.basicConfig` in `main()`, `logger.exception` in broad handlers.
- Session context codecs corrected to real tool names; added `.windsurfrules` copy, Copilot instructions, opencode + Antigravity skills, `.claude-plugin` SessionStart hook.
- Added `just mcpb-pack` (fleet shim) + `just certify`; `.pre-commit-config.yaml` with hook installed; `renovate.json`.
- `AVAILABLE_APPS.md` re-surveyed (124GB / 15 apps, 2026-11-25).

## [1.0.0] - 2026-06-06

### Added

- Rebuilt from `mcp-central-docs/projects/pinokio-mcp` PRD after missing local repo
- `PinokioClient`: port scan 42000-42059, Windows home from `%APPDATA%\Pinokio\config.json`
- Portmanteau tools: `app_management`, `system_management`, `lww_management`
- MCP resources: `pinokio://apps`, `running`, `localhost`, `lww/devices`
- Prompts: start workflow, cross-device, troubleshooting
- Stdio `start.ps1` + fleet `web_sota/start.ps1` wrapper
- Tests, `scripts/discover-api.ps1`, `scripts/test_tools.py`
