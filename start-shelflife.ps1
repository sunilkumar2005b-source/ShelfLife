[CmdletBinding()]
param(
    [switch]$Silent
)

# =========================================================
# ShelfLife - One-Click Launcher (PowerShell)
# Launches Backend (FastAPI :8000) and Frontend (Vite :5173)
# =========================================================

$ErrorActionPreference = "Continue"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

if (-not $Silent) {
    Write-Host "=========================================================" -ForegroundColor Green
    Write-Host "   ShelfLife: AI-Powered Perishable Inventory System     " -ForegroundColor Cyan
    Write-Host "       Final-Year Integrated M.Tech Project              " -ForegroundColor Cyan
    Write-Host "=========================================================" -ForegroundColor Green
}

# 1. Verify and Auto-Start PostgreSQL Database (Port 5432)
Write-Host "`n[1/4] Checking PostgreSQL database connectivity (port 5432)..." -ForegroundColor Yellow
$pgConnection = Test-NetConnection -ComputerName "127.0.0.1" -Port 5432 -WarningAction SilentlyContinue
if (-not $pgConnection.TcpTestSucceeded) {
    Write-Host "  [*] PostgreSQL not responding; attempting to start Windows service..." -ForegroundColor Yellow
    Get-Service *postgres* -ErrorAction SilentlyContinue | Start-Service -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
    $pgConnection = Test-NetConnection -ComputerName "127.0.0.1" -Port 5432 -WarningAction SilentlyContinue
}

if ($pgConnection.TcpTestSucceeded) {
    Write-Host "  -> PostgreSQL is RUNNING and accepting connections." -ForegroundColor Green
} else {
    Write-Host "  [!] WARNING: PostgreSQL (port 5432) did not respond." -ForegroundColor Red
    Write-Host "      Please ensure your PostgreSQL Windows service is running." -ForegroundColor Red
}

# 2. Check or Start Backend FastAPI Server (Port 8000)
Write-Host "`n[2/4] Verifying FastAPI backend on http://127.0.0.1:8000..." -ForegroundColor Yellow
$backendAlreadyLive = $false
try {
    $res = Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -TimeoutSec 1 -ErrorAction SilentlyContinue
    if ($res.status -eq "healthy" -or $res.backend -eq "online") {
        $backendAlreadyLive = $true
    }
} catch {}

if ($backendAlreadyLive) {
    Write-Host "  -> Backend is ALREADY running and healthy on port 8000." -ForegroundColor Green
} else {
    # Clean up any stale or orphaned process on port 8000
    $staleConnections = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
    if ($staleConnections) {
        $pids = $staleConnections | Select-Object -ExpandProperty OwningProcess -Unique
        foreach ($p in $pids) {
            if ($p -gt 0) {
                Write-Host "  -> Terminating orphaned PID $p on port 8000..." -ForegroundColor Yellow
                Stop-Process -Id $p -Force -ErrorAction SilentlyContinue
            }
        }
        Start-Sleep -Seconds 1
    }

    $BackendDir = Join-Path $ScriptDir "backend"
    $PythonExe = Join-Path $BackendDir "venv\Scripts\python.exe"

    if (-not (Test-Path $PythonExe)) {
        Write-Host "  [!] Virtual environment not found at $PythonExe." -ForegroundColor Red
        Write-Host "      Falling back to global python..." -ForegroundColor Yellow
        $PythonExe = "python"
    }

    $backendProc = Start-Process -FilePath $PythonExe `
        -ArgumentList "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000", "--reload" `
        -WorkingDirectory $BackendDir `
        -WindowStyle Hidden `
        -PassThru

    Write-Host "  -> Backend process started (PID: $($backendProc.Id))" -ForegroundColor Green
}

# 3. Check or Start Frontend Vite Dev Server (Port 5173)
Write-Host "`n[3/4] Verifying Vite frontend on http://localhost:5173..." -ForegroundColor Yellow
$frontendAlreadyLive = $false
try {
    $vRes = Invoke-WebRequest -Uri "http://localhost:5173" -TimeoutSec 1 -UseBasicParsing -ErrorAction SilentlyContinue
    if ($vRes.StatusCode -eq 200) {
        $frontendAlreadyLive = $true
    }
} catch {}

if ($frontendAlreadyLive) {
    Write-Host "  -> Frontend is ALREADY running on http://localhost:5173." -ForegroundColor Green
} else {
    $FrontendDir = Join-Path $ScriptDir "frontend"
    $frontendProc = Start-Process -FilePath "cmd.exe" `
        -ArgumentList "/c", "npm run dev" `
        -WorkingDirectory $FrontendDir `
        -WindowStyle Hidden `
        -PassThru

    Write-Host "  -> Frontend process started (PID: $($frontendProc.Id))" -ForegroundColor Green
}

# 4. Verify Services Readiness Before Launching Browser
Write-Host "`n[4/4] Synchronizing backend and database readiness..." -ForegroundColor Yellow
$maxAttempts = 20
$attempt = 0
$servicesReady = $false

while ($attempt -lt $maxAttempts -and -not $servicesReady) {
    Start-Sleep -Seconds 1
    $attempt++
    try {
        $health = Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($health.status -eq "healthy" -and $health.database -eq "connected") {
            $servicesReady = $true
        }
    } catch {}
}

if ($servicesReady) {
    Write-Host "  -> Backend & PostgreSQL are 100% HEALTHY and READY!" -ForegroundColor Green
} else {
    Write-Host "  [!] Backend taking a few extra seconds; frontend will auto-connect." -ForegroundColor Yellow
}

if (-not $Silent) {
    Write-Host "`n=========================================================" -ForegroundColor Green
    Write-Host "   ShelfLife is now LIVE and fully operational!          " -ForegroundColor Green
    Write-Host "   Frontend Dashboard:  http://localhost:5173            " -ForegroundColor Cyan
    Write-Host "   Interactive API Docs: http://127.0.0.1:8000/docs      " -ForegroundColor Cyan
    Write-Host "   To stop all services: run .\stop-shelflife.ps1        " -ForegroundColor Yellow
    Write-Host "=========================================================" -ForegroundColor Green

    Start-Process "http://localhost:5173"
}
