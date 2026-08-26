# start.ps1 - Start the minimal application bootstrap
$ErrorActionPreference = 'Stop'

Write-Host "Starting RecoverAI foundation..." -ForegroundColor Cyan
uv run python -m recoverai.main
