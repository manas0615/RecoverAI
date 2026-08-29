# stop-all.ps1 - Unified shutdown script
$ErrorActionPreference = 'Continue'

Write-Host "Stopping n8n (Docker Compose)..." -ForegroundColor Cyan
docker compose -f n8n/compose.yaml down

Write-Host "Stopping Frontend (Node)..." -ForegroundColor Cyan
# Find node processes listening on port 5173
$connections = Get-NetTCPConnection -LocalPort 5173 -State Listen -ErrorAction SilentlyContinue
foreach ($conn in $connections) {
    if ($conn.OwningProcess) {
        Write-Host "Killing process $($conn.OwningProcess) for port 5173..."
        Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue
    }
}
# Also kill vite processes if any are dangling
Get-Process -Name "node" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -match "vite" } | Stop-Process -Force -ErrorAction SilentlyContinue

Write-Host "Stopping Backend (uvicorn/python)..." -ForegroundColor Cyan
$connections = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
foreach ($conn in $connections) {
    if ($conn.OwningProcess) {
        Write-Host "Killing process $($conn.OwningProcess) for port 8000..."
        # Try graceful termination first if possible, otherwise force.
        # Stop-Process in PowerShell forces kill, which doesn't allow FastAPI lifespan to run cleanly,
        # but on Windows it's hard to send SIGTERM via pure powershell without extra tools. 
        # Since SQLite is using WAL, forceful kill is safe enough for MVP.
        Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue
    }
}

Write-Host "All services stopped." -ForegroundColor Green
