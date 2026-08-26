# setup.ps1 - Bootstrap the local development environment using uv
$ErrorActionPreference = 'Stop'

Write-Host "Setting up RecoverAI foundation..." -ForegroundColor Cyan

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "uv is not installed. Please install uv first." -ForegroundColor Red
    exit 1
}

Write-Host "Installing dependencies with uv..."
uv sync

Write-Host "Checking .env file..."
if (-not (Test-Path .env)) {
    Write-Host "Creating .env from .env.example..."
    Copy-Item .env.example .env
}

Write-Host "Setup complete." -ForegroundColor Green
