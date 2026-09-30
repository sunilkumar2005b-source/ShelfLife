# =========================================================
# ShelfLife - Reset / Seed Demo Scenario (PowerShell)
# Resets the store inventory state to baseline normal scenario
# =========================================================

Write-Host "Resetting ShelfLife to Baseline Normal Scenario..." -ForegroundColor Yellow

try {
    $response = Invoke-RestMethod -Uri "http://127.0.0.1:8000/demo/apply-scenario" `
        -Method Post `
        -Headers @{ "Content-Type" = "application/json" } `
        -Body '{"scenario": "normal"}' `
        -ErrorAction Stop

    Write-Host "  -> Success: $($response.message)" -ForegroundColor Green
    Write-Host "  -> Active Scenario: $($response.scenario)" -ForegroundColor Cyan
    Write-Host "  -> Database records synchronized." -ForegroundColor Green
} catch {
    Write-Host "  [!] Could not connect to running backend at http://127.0.0.1:8000." -ForegroundColor Red
    Write-Host "      Please ensure the backend is running with .\start-shelflife.ps1 first." -ForegroundColor Yellow
}
