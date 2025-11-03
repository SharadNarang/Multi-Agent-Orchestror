# Multi-Agent Orchestrator

A sophisticated multi-agent orchestration system with A2A (Agent-to-Agent) protocol support, built with Python FastAPI backend and React frontend.

## 🌟 Features

- **Multi-Agent Architecture**: Coordinate multiple AI agents with different capabilities
- **A2A Protocol Support**: Agent-to-Agent communication protocol implementation
- **LangGraph Integration**: Complex agent workflows with state management
- **Task Planning & Execution**: Intelligent task decomposition and execution
- **Memory Management**: Conversation context and session management
- **REST API**: Full-featured API with automatic documentation
- **Modern UI**: React-based frontend with real-time updates
- **Docker Support**: Containerized deployment ready

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (React)                      │
│                   Port 3000                              │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│           Main Orchestrator (FastAPI)                    │
│                   Port 8000                              │
│  • Task Planning & Execution                             │
│  • Agent Registry                                        │
│  • Memory Service                                        │
└─────────┬──────────────────────┬────────────────────────┘
          │                      │
┌─────────▼────────────┐  ┌─────▼──────────────────────┐
│  A2A Server          │  │  API Agent                  │
│  (LangGraph)         │  │  (Simple API)               │
│  Port 8001           │  │  Port 8002                  │
│  • ResearchAgent     │  │  • DataAnalyzer             │
│  • Complex Workflows │  │  • Data Processing          │
└──────────────────────┘  └─────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 16+
- pip
- npm

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/SharadNarang/Multi-Agent-Orchestror.git
cd Multi-Agent-Orchestror
```

2. **Setup Backend**
```bash
cd backend
python -m venv venv

# Windows
.\venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

3. **Configure Environment**
```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your API keys
# OPENAI_API_KEY=your-openai-key-here
# GROQ_API_KEY=your-groq-key-here
```

4. **Setup Frontend**
```bash
cd ../frontend
npm install
```

### Running the Services

#### Option 1: Start All Services (PowerShell)

```powershell
# Start Backend Services
cd backend
Start-Job -Name "MainOrchestrator" -ScriptBlock { 
    Set-Location "path\to\multi-agent-orchestrator\backend"
    .\venv\Scripts\python.exe main.py 
}

Start-Job -Name "A2AServer" -ScriptBlock { 
    Set-Location "path\to\multi-agent-orchestrator\backend"
    .\venv\Scripts\python.exe a2a_server.py 
}

Start-Job -Name "APIAgent" -ScriptBlock { 
    Set-Location "path\to\multi-agent-orchestrator\backend"
    .\venv\Scripts\python.exe api_agent_server.py 
}

# Start Frontend
cd ..\frontend
npm run dev
```

#### Option 2: Start Services Individually

**Terminal 1 - Main Orchestrator:**
```bash
cd backend
python main.py
```

**Terminal 2 - A2A Server:**
```bash
cd backend
python a2a_server.py
```

**Terminal 3 - API Agent:**
```bash
cd backend
python api_agent_server.py
```

**Terminal 4 - Frontend:**
```bash
cd frontend
npm run dev
```

## 📡 API Endpoints

Once running, access:

- **Frontend UI**: http://localhost:3000
- **Main API Docs**: http://localhost:8000/docs
- **A2A Agent Docs**: http://localhost:8001/docs
- **API Agent Docs**: http://localhost:8002/docs

### Key Endpoints

#### Agent Management
- `POST /api/agents/register` - Register a new agent
- `GET /api/agents` - List all agents
- `GET /api/agents/{agent_id}` - Get agent details
- `PUT /api/agents/{agent_id}` - Update agent
- `POST /api/agents/{agent_id}/health` - Check agent health

#### Task Management
- `POST /api/tasks` - Create and execute a task
- `GET /api/tasks/{task_id}` - Get task status and results
- `POST /api/tasks/{task_id}/cancel` - Cancel a running task

#### Session Management
- `POST /api/sessions` - Create a new session
- `POST /api/sessions/{session_id}/messages` - Add message to session
- `GET /api/sessions/{session_id}/messages` - Get conversation history

## 💡 Usage Example

### Creating and Executing a Task

```python
import requests

# Create a task
task_data = {
    "description": "Research the latest trends in AI and summarize the findings",
    "user_id": "user123"
}

response = requests.post("http://localhost:8000/api/tasks", json=task_data)
task = response.json()

print(f"Task ID: {task['task_id']}")
print(f"Status: {task['status']}")

# Check task status
task_id = task['task_id']
status_response = requests.get(f"http://localhost:8000/api/tasks/{task_id}")
task_status = status_response.json()

print(f"Result: {task_status['result']}")
```

### PowerShell Example

```powershell
# Create a task
$taskBody = @{
    description = "Analyze the impact of climate change"
    user_id = "user1"
} | ConvertTo-Json

$response = Invoke-WebRequest -Uri "http://localhost:8000/api/tasks" `
    -Method Post -Body $taskBody -ContentType "application/json" -UseBasicParsing

$task = $response.Content | ConvertFrom-Json

# Check status
Invoke-WebRequest -Uri "http://localhost:8000/api/tasks/$($task.task_id)" `
    -UseBasicParsing | Select-Object -ExpandProperty Content
```

## 🔧 Configuration

### Backend Configuration

Edit `backend/.env`:

```env
# OpenAI API Key (for LangGraph agent)
OPENAI_API_KEY=sk-your-openai-key

# Groq API Key (alternative LLM provider)
GROQ_API_KEY=gsk-your-groq-key

# Database
DATABASE_URL=sqlite:///./agent_orchestrator.db

# Frontend URL (for CORS)
FRONTEND_URL=http://localhost:3000
```

### Frontend Configuration

Edit `frontend/vite.config.js` to change ports or proxy settings.

## 📦 Project Structure

```
multi-agent-orchestrator/
├── backend/
│   ├── agents/              # Agent implementations
│   │   ├── a2a_protocol.py  # A2A protocol definitions
│   │   ├── langgraph_agent.py  # LangGraph-based agent
│   │   └── api_agent.py     # Simple API agent
│   ├── models/              # Database models
│   │   ├── agent.py         # Agent model
│   │   ├── task.py          # Task model
│   │   └── memory.py        # Memory/context model
│   ├── orchestrator/        # Task orchestration
│   │   ├── task_planner.py  # Task planning logic
│   │   └── task_executor.py # Task execution
│   ├── services/            # Business logic services
│   │   ├── agent_registry.py  # Agent registration
│   │   └── memory_service.py  # Memory management
│   ├── main.py              # Main orchestrator server
│   ├── a2a_server.py        # A2A agent server
│   ├── api_agent_server.py  # API agent server
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # Main app component
│   │   └── main.jsx         # Entry point
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── .gitignore
└── README.md
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🐛 Troubleshooting

### Common Issues

**Port already in use:**
```bash
# Find process using port (Windows)
netstat -ano | findstr :8000

# Kill process
taskkill /PID <process_id> /F
```

**Module not found:**
```bash
# Ensure you're in the virtual environment
cd backend
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

**Database errors:**
```bash
# Reset database
cd backend
rm agent_orchestrator.db
python main.py  # Will recreate the database
```

## 📚 Additional Documentation

- [Service Flow](SERVICE_FLOW.md) - Architecture and service interaction diagrams
- [REST API Agent Flow](REST_API_AGENT_FLOW.md) - REST API agent adapter pattern explained
- [iFrame Integration](IFRAME_INTEGRATION.md) - Embedding in Adobe Agentic Builder
- [Backend README](backend/README.md) - Backend-specific documentation
- [Frontend README](frontend/README.md) - Frontend-specific documentation
- [API Guide](API_GUIDE.md) - Detailed API documentation
- [Contributing Guide](CONTRIBUTING.md) - How to contribute

## 🔗 Links

- [Repository](https://github.com/SharadNarang/Multi-Agent-Orchestror)
- [Issues](https://github.com/SharadNarang/Multi-Agent-Orchestror/issues)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## 👤 Author

**Sharad Narang**
- GitHub: [@SharadNarang](https://github.com/SharadNarang)

## ⭐ Show your support

Give a ⭐️ if this project helped you!

