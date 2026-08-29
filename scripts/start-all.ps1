# start-all.ps1 - Unified startup script
$ErrorActionPreference = 'Stop'

Write-Host "Checking prerequisites..." -ForegroundColor Cyan
if (-not (Test-Path .env)) {
    Write-Host "[ERROR] .env file not found. Run ./scripts/setup.ps1 first." -ForegroundColor Red
    exit 1
}

if (-not (Test-Path frontend/.env)) {
    Write-Host "[WARNING] frontend/.env not found. Creating from frontend/.env.example if it exists." -ForegroundColor Yellow
    if (Test-Path frontend/.env.example) {
        Copy-Item frontend/.env.example frontend/.env
    }
}

Write-Host "Starting Backend in new window..." -ForegroundColor Cyan
Start-Process -FilePath "uv" -ArgumentList "run", "uvicorn", "recoverai.api.main:app", "--host", "127.0.0.1", "--port", "8000"

Write-Host "Waiting for backend to become ready..." -ForegroundColor Cyan
$backendReady = $false
for ($i = 0; $i -lt 15; $i++) {
    try {
        $res = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -TimeoutSec 2 -ErrorAction Stop
        if ($res.status -eq "ok") {
            $backendReady = $true
            break
        }
    } catch {
        Start-Sleep -Seconds 2
    }
}

if (-not $backendReady) {
    Write-Host "[ERROR] Backend failed to become ready." -ForegroundColor Red
    exit 1
}
Write-Host "Backend is ready." -ForegroundColor Green

Write-Host "Starting n8n (Docker Compose)..." -ForegroundColor Cyan
docker compose -f n8n/compose.yaml up -d

Write-Host "Waiting for n8n to become ready..." -ForegroundColor Cyan
$n8nReady = $false
for ($i = 0; $i -lt 30; $i++) {
    try {
        $res = Invoke-WebRequest -Uri "http://localhost:5678" -Method Get -TimeoutSec 2 -ErrorAction Stop
        $n8nReady = $true
        break
    } catch {
        Start-Sleep -Seconds 2
    }
}

if (-not $n8nReady) {
    Write-Host "[ERROR] n8n failed to become ready." -ForegroundColor Red
    exit 1
}
Write-Host "n8n is ready." -ForegroundColor Green

Write-Host "Starting Frontend in new window..." -ForegroundColor Cyan
Start-Process -WorkingDirectory "frontend" -FilePath "npm" -ArgumentList "run", "dev"

Write-Host "Waiting for frontend to become ready..." -ForegroundColor Cyan
$frontendReady = $false
for ($i = 0; $i -lt 15; $i++) {
    try {
        $res = Invoke-WebRequest -Uri "http://localhost:5173" -Method Get -TimeoutSec 2 -ErrorAction Stop
        $frontendReady = $true
        break
    } catch {
        Start-Sleep -Seconds 2
    }
}

if (-not $frontendReady) {
    Write-Host "[ERROR] Frontend failed to become ready." -ForegroundColor Red
    exit 1
}
Write-Host "Frontend is ready." -ForegroundColor Green

Write-Host "All services started successfully!" -ForegroundColor Green
Write-Host "Backend: http://localhost:8000"
Write-Host "n8n: http://localhost:5678"
Write-Host "Frontend: http://localhost:5173"
