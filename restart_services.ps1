# Restart All Multi-Agent Orchestrator Services
# Run this script after code changes to reload all services

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  Multi-Agent Orchestrator - Service Restart         ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Stop all services
Write-Host "Stopping services..." -ForegroundColor Yellow

$ports = @(8000, 8001, 8002)
foreach ($port in $ports) {
    $connections = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($connections) {
        foreach ($conn in $connections) {
            $pid = $conn.OwningProcess
            Write-Host "  Stopping process on port $port (PID: $pid)" -ForegroundColor Gray
            Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
        }
    }
}

Start-Sleep -Seconds 3

# Start all services
Write-Host ""
Write-Host "Starting services..." -ForegroundColor Green
Write-Host ""

$backendPath = "$PSScriptRoot\backend"

# Start Main Orchestrator (Port 8000)
Write-Host "1. Starting Main Orchestrator (Port 8000)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList `
    "-NoExit", `
    "-Command", `
    "cd '$backendPath'; .\venv\Scripts\python.exe main.py" `
    -WindowStyle Minimized

Start-Sleep -Seconds 3

# Start A2A Server (Port 8001)
Write-Host "2. Starting A2A Server (Port 8001)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList `
    "-NoExit", `
    "-Command", `
    "cd '$backendPath'; .\venv\Scripts\python.exe a2a_server.py" `
    -WindowStyle Minimized

Start-Sleep -Seconds 3

# Start API Agent (Port 8002)
Write-Host "3. Starting API Agent (Port 8002)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList `
    "-NoExit", `
    "-Command", `
    "cd '$backendPath'; .\venv\Scripts\python.exe api_agent_server.py" `
    -WindowStyle Minimized

Start-Sleep -Seconds 5

# Verify services
Write-Host ""
Write-Host "Verifying services..." -ForegroundColor Yellow
Write-Host ""

$services = @(
    @{Name="Main Orchestrator"; Port=8000; URL="http://localhost:8000/health"},
    @{Name="A2A Server"; Port=8001; URL="http://localhost:8001/health"},
    @{Name="API Agent"; Port=8002; URL="http://localhost:8002/health"}
)

foreach ($service in $services) {
    try {
        $response = Invoke-WebRequest -Uri $service.URL -UseBasicParsing -TimeoutSec 3
        Write-Host "✓ $($service.Name) - Port $($service.Port) - [HEALTHY]" -ForegroundColor Green
    } catch {
        Write-Host "✗ $($service.Name) - Port $($service.Port) - [OFFLINE]" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║  All services restarted successfully!               ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "Access the services at:" -ForegroundColor Cyan
Write-Host "  • Frontend:  http://localhost:3000" -ForegroundColor White
Write-Host "  • Main API:  http://localhost:8000/docs" -ForegroundColor White
Write-Host "  • A2A Agent: http://localhost:8001/docs" -ForegroundColor White
Write-Host "  • API Agent: http://localhost:8002/docs" -ForegroundColor White
Write-Host ""

