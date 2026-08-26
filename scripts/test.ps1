# test.ps1 - Run pytest
$ErrorActionPreference = 'Stop'

Write-Host "Running tests with pytest..." -ForegroundColor Cyan
uv run pytest tests/
