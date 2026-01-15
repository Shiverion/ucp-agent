# Restart UCP Server Script

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "UCP Server Restart Script" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# 1. Kill any existing servers on port 8183
Write-Host "1. Stopping existing servers on port 8183..." -ForegroundColor Yellow
$connections = netstat -ano | Select-String ":8183.*LISTENING"
$pids = @()
foreach ($line in $connections) {
    if ($line -match '(\d+)$') {
        $pids += $matches[1]
    }
}
$uniquePids = $pids | Select-Object -Unique
if ($uniquePids) {
    foreach ($pid in $uniquePids) {
        Write-Host "   Killing process $pid..." -ForegroundColor Gray
        Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
    }
    Start-Sleep -Seconds 2
    Write-Host "   Done!" -ForegroundColor Green
} else {
    Write-Host "   No existing servers found." -ForegroundColor Gray
}

# 2. Verify port is free
Write-Host "`n2. Verifying port 8183 is free..." -ForegroundColor Yellow
$check = netstat -ano | Select-String ":8183.*LISTENING"
if ($check) {
    Write-Host "   WARNING: Port 8183 is still in use!" -ForegroundColor Red
    Write-Host "   You may need to manually kill processes." -ForegroundColor Red
    exit 1
} else {
    Write-Host "   Port 8183 is free!" -ForegroundColor Green
}

# 3. Start the server
Write-Host "`n3. Starting UCP server..." -ForegroundColor Yellow
Write-Host "   Server will run on http://localhost:8183" -ForegroundColor Cyan
Write-Host "   Press Ctrl+C to stop the server`n" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Navigate to project directory and start server
Set-Location -Path $PSScriptRoot
& "$PSScriptRoot\.venv\Scripts\python.exe" -m uvicorn src.server.app:app --host 0.0.0.0 --port 8183 --reload
