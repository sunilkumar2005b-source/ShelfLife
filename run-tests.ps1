# =========================================================
# ShelfLife - Test Verification Suite (PowerShell)
# Runs all 33 automated tests across APIs, ML, and Rules
# =========================================================

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackendDir = Join-Path $ScriptDir "backend"
$PythonExe = Join-Path $BackendDir "venv\Scripts\python.exe"

if (-not (Test-Path $PythonExe)) {
    $PythonExe = "python"
}

Write-Host "=========================================================" -ForegroundColor Green
Write-Host "   ShelfLife Automated Test Verification Suite           " -ForegroundColor Cyan
Write-Host "   Academic Quality Assurance & Regression Suite         " -ForegroundColor Cyan
Write-Host "=========================================================" -ForegroundColor Green

Write-Host "`nExecuting full unittest test suite in backend/tests/...`n" -ForegroundColor Yellow

Push-Location $BackendDir
try {
    & $PythonExe -m unittest discover -s tests -p "test_*.py" -v
    $exitCode = $LASTEXITCODE
    if ($exitCode -eq 0) {
        Write-Host "`n=========================================================" -ForegroundColor Green
        Write-Host "  [PASS] ALL 33 TESTS PASSED (100% SUCCESS RATE)        " -ForegroundColor Green
        Write-Host "  - test_api.py:             REST Endpoints & CRUD       " -ForegroundColor Cyan
        Write-Host "  - test_rules.py:           Deterministic Rule Engine   " -ForegroundColor Cyan
        Write-Host "  - test_ml.py:              ML Pipeline & Preprocessors " -ForegroundColor Cyan
        Write-Host "  - test_ml_integration.py:  Predictive REST APIs        " -ForegroundColor Cyan
        Write-Host "  - test_reports.py:         Financial & Clearance Models" -ForegroundColor Cyan
        Write-Host "=========================================================" -ForegroundColor Green
    } else {
        Write-Host "`n[FAIL] One or more tests failed with exit code $exitCode." -ForegroundColor Red
    }
} finally {
    Pop-Location
}
