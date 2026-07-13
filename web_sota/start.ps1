param([switch]$Headless)

# Stdio MCP - no fleet HTTP ports. Wrapper keeps manifest path consistent.
$FleetStartPath = Join-Path $Root "scripts\FleetStartMode.ps1"
if (-not (Test-Path -LiteralPath $FleetStartPath)) {
    Write-Host "ERROR: Missing vendored launcher helper: $FleetStartPath" -ForegroundColor Red
    exit 1
}
. $FleetStartPath
Enter-FleetHeadlessConsole -Headless:$Headless

$root = Split-Path -Parent $PSScriptRoot
& (Join-Path $root "start.ps1") @PSBoundParameters
exit $LASTEXITCODE

