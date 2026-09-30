# =========================================================
# ShelfLife - One-Click Launcher (PowerShell)
# Launches Backend (FastAPI :8000) and Frontend (Vite :5173)
# =========================================================

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "=========================================================" -ForegroundColor Green
Write-Host "   ShelfLife: AI-Powered Perishable Inventory System     " -ForegroundColor Cyan
Write-Host "       Final-Year Integrated M.Tech Project              " -ForegroundColor Cyan
Write-Host "=========================================================" -ForegroundColor Green

# 1. Verify PostgreSQL Database Connectivity
Write-Host "`n[1/4] Checking PostgreSQL database connectivity (port 5432)..." -ForegroundColor Yellow
$pgConnection = Test-NetConnection -ComputerName "127.0.0.1" -Port 5432 -WarningAction SilentlyContinue
if ($pgConnection.TcpTestSucceeded) {
    Write-Host "  -> PostgreSQL is RUNNING and accepting connections." -ForegroundColor Green
} else {
    Write-Host "  [!] WARNING: PostgreSQL (port 5432) did not respond." -ForegroundColor Red
    Write-Host "      Please ensure your PostgreSQL Windows service is running." -ForegroundColor Red
}

# 2. Start Backend FastAPI Server
Write-Host "`n[2/4] Starting FastAPI backend on http://127.0.0.1:8000..." -ForegroundColor Yellow
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
    -PassThru

Write-Host "  -> Backend process started (PID: $($backendProc.Id))" -ForegroundColor Green

# 3. Start Frontend Vite Dev Server
Write-Host "`n[3/4] Starting Vite frontend on http://localhost:5173..." -ForegroundColor Yellow
$FrontendDir = Join-Path $ScriptDir "frontend"
$frontendProc = Start-Process -FilePath "cmd.exe" `
    -ArgumentList "/c", "npm run dev" `
    -WorkingDirectory $FrontendDir `
    -PassThru

Write-Host "  -> Frontend process started (PID: $($frontendProc.Id))" -ForegroundColor Green

# 4. Wait for readiness and launch browser
Write-Host "`n[4/4] Waiting 3 seconds for services to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

Write-Host "`n=========================================================" -ForegroundColor Green
Write-Host "   ShelfLife is now LIVE and fully operational!          " -ForegroundColor Green
Write-Host "   Frontend Dashboard:  http://localhost:5173            " -ForegroundColor Cyan
Write-Host "   Interactive API Docs: http://127.0.0.1:8000/docs      " -ForegroundColor Cyan
Write-Host "   To stop all services: run .\stop-shelflife.ps1        " -ForegroundColor Yellow
Write-Host "=========================================================" -ForegroundColor Green

Start-Process "http://localhost:5173"
