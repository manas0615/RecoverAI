# check-health.ps1 - Verify local services
$ErrorActionPreference = 'Continue'

Write-Host "Verifying Backend..." -NoNewline
try {
    $backend = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -TimeoutSec 3 -ErrorAction Stop
    if ($backend.status -eq "ok") { Write-Host "[OK]" -ForegroundColor Green }
    else { Write-Host "[FAIL] Status not ok" -ForegroundColor Red }
} catch {
    Write-Host "[FAIL] Could not reach backend at http://localhost:8000/health" -ForegroundColor Red
}

Write-Host "Verifying n8n..." -NoNewline
try {
    $n8n = Invoke-WebRequest -Uri "http://localhost:5678" -Method Get -TimeoutSec 3 -ErrorAction Stop
    Write-Host "[OK]" -ForegroundColor Green
} catch {
    Write-Host "[FAIL] Could not reach n8n at http://localhost:5678" -ForegroundColor Red
}

Write-Host "Verifying Frontend..." -NoNewline
try {
    $frontend = Invoke-WebRequest -Uri "http://localhost:5173" -Method Get -TimeoutSec 3 -ErrorAction Stop
    Write-Host "[OK]" -ForegroundColor Green
} catch {
    Write-Host "[FAIL] Could not reach frontend at http://localhost:5173" -ForegroundColor Red
}
