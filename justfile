set windows-shell := ["powershell.exe", "-NoProfile", "-Command"]

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

# Bootstrap: install dev deps + pre-commit hook
bootstrap:
    uv sync --group dev
    uv run pre-commit install
    Write-Host "Pre-commit hooks installed." -ForegroundColor Green