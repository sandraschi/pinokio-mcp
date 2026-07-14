set windows-shell := ["pwsh.exe", "-NoLogo", "-Command"]

default:
    @just --list

lint:
    uv run ruff check src/

fmt:
    uv run ruff format src/

test:
    uv run pytest -q

serve:
    uv run pinokio-mcp
