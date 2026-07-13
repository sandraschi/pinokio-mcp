param([switch]$Headless)

if ($Headless -and ($Host.UI.RawUI.WindowTitle -notmatch 'Hidden')) {
    Start-Process pwsh -ArgumentList '-NoProfile', '-File', $PSCommandPath, '-Headless' -WindowStyle Hidden
    exit
}

$env:FASTMCP_LOG_LEVEL = 'WARNING'
Write-Host 'Starting pinokio-mcp (stdio)...' -ForegroundColor Cyan
Set-Location $PSScriptRoot
uv run pinokio-mcp
