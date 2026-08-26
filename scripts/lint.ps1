# lint.ps1 - Run formatting, linting, and type checking
$ErrorActionPreference = 'Stop'

Write-Host "Running code formatting check (ruff format)..." -ForegroundColor Cyan
uv run ruff format --check .

Write-Host "Running lint check (ruff check)..." -ForegroundColor Cyan
uv run ruff check .

Write-Host "Running static type check (mypy)..." -ForegroundColor Cyan
uv run mypy recoverai/ tests/
