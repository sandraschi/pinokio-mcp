#Requires -Version 5.1
<#  Fleet shim: pack logic lives in mcp-central-docs so fixes reach every repo. #>
param()
$ErrorActionPreference = 'Stop'
$RepoRoot = Split-Path -Parent $PSScriptRoot
& (Join-Path (Split-Path -Parent $RepoRoot) 'mcp-central-docs\scripts\fleet-mcpb-pack.ps1') -RepoRoot $RepoRoot
