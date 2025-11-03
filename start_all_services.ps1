# Start All Services for Multi-Agent Orchestrator
# This script starts all backend servers and the frontend

Write-Host "🚀 Starting Multi-Agent Orchestrator Services..." -ForegroundColor Green

# Start Dummy Agents
Write-Host "`n📡 Starting Dummy Agent Servers..." -ForegroundColor Cyan

Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd C:\Users\shnarang\multi-agent-orchestrator\backend\dummy_agents; Write-Host '🤖 Starting CrewAI Agent (Port 8003)...' -ForegroundColor Yellow; python crewai_agent_server.py"

Start-Sleep -Seconds 2

Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd C:\Users\shnarang\multi-agent-orchestrator\backend\dummy_agents; Write-Host '🤖 Starting Databricks Agent (Port 8004)...' -ForegroundColor Yellow; python databricks_agent_server.py"

Start-Sleep -Seconds 2

Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd C:\Users\shnarang\multi-agent-orchestrator\backend\dummy_agents; Write-Host '🤖 Starting OpenAI Compatible Agent (Port 8005)...' -ForegroundColor Yellow; python openai_compatible_agent_server.py"

Start-Sleep -Seconds 3

# Start Main Backend Services
Write-Host "`n🔧 Starting Backend Services..." -ForegroundColor Cyan

Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd C:\Users\shnarang\multi-agent-orchestrator\backend; Write-Host '⚙️ Starting Main Orchestrator (Port 8000)...' -ForegroundColor Magenta; python main.py"

Start-Sleep -Seconds 2

Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd C:\Users\shnarang\multi-agent-orchestrator\backend; Write-Host '⚙️ Starting A2A Server (Port 8001)...' -ForegroundColor Magenta; python a2a_server.py"

Start-Sleep -Seconds 2

Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd C:\Users\shnarang\multi-agent-orchestrator\backend; Write-Host '⚙️ Starting API Agent (Port 8002)...' -ForegroundColor Magenta; python api_agent_server.py"

Start-Sleep -Seconds 5

# Start Frontend
Write-Host "`n🎨 Starting Frontend (Port 3000)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd C:\Users\shnarang\multi-agent-orchestrator\frontend; Write-Host '🌐 Starting Vite Dev Server...' -ForegroundColor Blue; npm run dev"

Start-Sleep -Seconds 3

Write-Host "`n✅ All services started!" -ForegroundColor Green
Write-Host "`n📋 Service URLs:" -ForegroundColor White
Write-Host "   Frontend:              http://localhost:3000" -ForegroundColor White
Write-Host "   Main Orchestrator:     http://localhost:8000" -ForegroundColor White
Write-Host "   A2A Server:            http://localhost:8001" -ForegroundColor White
Write-Host "   API Agent:             http://localhost:8002" -ForegroundColor White
Write-Host "   CrewAI Agent:          http://localhost:8003" -ForegroundColor White
Write-Host "   Databricks Agent:      http://localhost:8004" -ForegroundColor White
Write-Host "   OpenAI Agent:          http://localhost:8005" -ForegroundColor White

Write-Host "`n🧪 Test Registration:" -ForegroundColor Yellow
Write-Host "   1. Open http://localhost:3000" -ForegroundColor White
Write-Host "   2. Toggle Power User mode" -ForegroundColor White
Write-Host "   3. Click 'Register Agent'" -ForegroundColor White
Write-Host "   4. Select CrewAI template" -ForegroundColor White
Write-Host "   5. Endpoint: http://localhost:8003" -ForegroundColor White

Write-Host "`n⌛ Waiting 10 seconds for all services to be ready..." -ForegroundColor Cyan
Start-Sleep -Seconds 10

# Open browser
Start-Process "http://localhost:3000"

Write-Host "`n✨ Browser opened! Ready to test!" -ForegroundColor Green

