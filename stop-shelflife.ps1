# =========================================================
# ShelfLife - Process Stopper (PowerShell)
# Terminates processes on ports 8000 (Backend) and 5173 (Frontend)
# =========================================================

Write-Host "Stopping ShelfLife background services..." -ForegroundColor Yellow

$ports = @(8000, 5173)

foreach ($port in $ports) {
    $connections = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($connections) {
        $pids = $connections | Select-Object -ExpandProperty OwningProcess -Unique
        foreach ($procId in $pids) {
            if ($procId -gt 0) {
                try {
                    $proc = Get-Process -Id $procId -ErrorAction SilentlyContinue
                    if ($proc) {
                        Write-Host "  -> Terminating process $($proc.ProcessName) (PID: $procId) on port $port..." -ForegroundColor Yellow
                        Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
                    }
                } catch {
                    Write-Host "  [!] Could not stop PID $procId" -ForegroundColor Red
                }
            }
        }
    } else {
        Write-Host "  -> Port $port is already free." -ForegroundColor Green
    }
}

Write-Host "`nAll ShelfLife services have been cleanly stopped." -ForegroundColor Green
