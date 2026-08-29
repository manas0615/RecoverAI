# start.ps1 - Start the minimal application bootstrap
$ErrorActionPreference = 'Stop'

Write-Host "Starting RecoverAI foundation..." -ForegroundColor Cyan
uv run uvicorn recoverai.api.main:app --host 127.0.0.1 --port 8000
