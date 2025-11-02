# Multi-Agent Orchestrator - Backend

The backend implementation of the Multi-Agent Orchestrator system, built with FastAPI and SQLAlchemy.

## 🏗️ Architecture

### Components

1. **Main Orchestrator** (`main.py`)
   - Central coordination service
   - REST API endpoints
   - Task management
   - Agent registry
   - Memory service

2. **A2A Server** (`a2a_server.py`)
   - LangGraph-based agent implementation
   - Complex workflow execution
   - Research and analysis capabilities
   - A2A protocol support

3. **API Agent** (`api_agent_server.py`)
   - Simple API-based agent
   - Data analysis and summarization
   - Direct API processing

### Directory Structure

```
backend/
├── agents/                  # Agent implementations
│   ├── __init__.py
│   ├── a2a_protocol.py     # A2A protocol definitions
│   ├── langgraph_agent.py  # LangGraph agent with workflows
│   └── api_agent.py        # Simple API agent
│
├── models/                  # SQLAlchemy database models
│   ├── __init__.py
│   ├── agent.py            # Agent model (registration, status)
│   ├── task.py             # Task and TaskStep models
│   └── memory.py           # Conversation context and messages
│
├── orchestrator/           # Core orchestration logic
│   ├── __init__.py
│   ├── task_planner.py    # Task decomposition and planning
│   └── task_executor.py   # Task execution engine
│
├── services/               # Business logic services
│   ├── __init__.py
│   ├── agent_registry.py  # Agent registration and discovery
│   └── memory_service.py  # Session and memory management
│
├── main.py                 # Main orchestrator server (Port 8000)
├── a2a_server.py          # A2A agent server (Port 8001)
├── api_agent_server.py    # API agent server (Port 8002)
├── config.py              # Configuration management
├── database.py            # Database setup and session management
├── requirements.txt       # Python dependencies
├── Dockerfile             # Docker containerization
└── .env.example           # Environment variables template
```

## 🚀 Setup

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Installation

1. **Create and activate virtual environment**

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Configure environment variables**

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
# OpenAI API Key for LangGraph agent
OPENAI_API_KEY=sk-your-openai-api-key

# Alternative: Groq API Key
GROQ_API_KEY=gsk-your-groq-api-key

# Database URL
DATABASE_URL=sqlite:///./agent_orchestrator.db

# Frontend URL for CORS
FRONTEND_URL=http://localhost:3000

# LLM Provider (openai or groq)
LLM_PROVIDER=openai
```

## 🎮 Running the Services

### Option 1: Run All Services (Windows PowerShell)

```powershell
# Terminal 1 - Main Orchestrator
python main.py

# Terminal 2 - A2A Server
python a2a_server.py

# Terminal 3 - API Agent
python api_agent_server.py
```

### Option 2: Run as Background Jobs (PowerShell)

```powershell
Start-Job -Name "MainOrchestrator" -ScriptBlock { 
    Set-Location "C:\path\to\backend"
    .\venv\Scripts\python.exe main.py 
}

Start-Job -Name "A2AServer" -ScriptBlock { 
    Set-Location "C:\path\to\backend"
    .\venv\Scripts\python.exe a2a_server.py 
}

Start-Job -Name "APIAgent" -ScriptBlock { 
    Set-Location "C:\path\to\backend"
    .\venv\Scripts\python.exe api_agent_server.py 
}

# Check job status
Get-Job

# View job output
Receive-Job -Name "MainOrchestrator"
```

### Option 3: Using Docker

```bash
docker build -t multi-agent-orchestrator .
docker run -p 8000:8000 -p 8001:8001 -p 8002:8002 multi-agent-orchestrator
```

## 📡 API Documentation

Once the services are running, access the interactive API documentation:

- **Main Orchestrator**: http://localhost:8000/docs
- **A2A Server**: http://localhost:8001/docs
- **API Agent**: http://localhost:8002/docs

## 🔌 Core Components

### 1. Database Models (`models/`)

#### Agent Model
```python
class Agent:
    id: int
    name: str
    description: str
    agent_type: AgentType  # A2A_SERVER, API, LANGGRAPH
    endpoint: str
    capabilities: List[str]
    status: AgentStatus  # ACTIVE, INACTIVE, ERROR
    config: Dict[str, Any]
    metadata: Dict[str, Any]
```

#### Task Model
```python
class Task:
    id: int
    session_id: str
    description: str
    status: TaskStatus  # PENDING, PLANNING, EXECUTING, COMPLETED, FAILED
    plan: Dict[str, Any]
    result: Dict[str, Any]
    created_at: datetime
    completed_at: datetime
```

#### Memory Model
```python
class ConversationContext:
    id: int
    session_id: str
    user_id: str
    messages: List[Message]
    metadata: Dict[str, Any]
```

### 2. Agent Registry (`services/agent_registry.py`)

Manages agent registration, discovery, and health monitoring.

```python
# Register a new agent
agent = registry.register_agent(
    name="ResearchAgent",
    description="AI research assistant",
    agent_type=AgentType.A2A_SERVER,
    endpoint="http://localhost:8001",
    capabilities=["research", "analysis"]
)

# Find agents by capability
agents = registry.find_agents_by_capability("research")

# Check agent health
health = await registry.check_agent_health(agent_id)
```

### 3. Task Planner (`orchestrator/task_planner.py`)

Decomposes complex tasks and creates execution plans.

```python
# Create execution plan
task = await planner.create_execution_plan(
    task_description="Research AI trends and create a summary",
    session_id="session-123"
)
```

### 4. Task Executor (`orchestrator/task_executor.py`)

Executes planned tasks using registered agents.

```python
# Execute task
result = await executor.execute_task(task_id)
```

### 5. Memory Service (`services/memory_service.py`)

Manages conversation sessions and context.

```python
# Create session
context = memory_service.create_session(
    user_id="user123",
    metadata={"source": "web"}
)

# Add message
message = memory_service.add_message(
    session_id=session_id,
    role="user",
    content="Tell me about AI"
)

# Get history
history = memory_service.get_conversation_history(session_id)
```

## 🧪 Testing

### Manual Testing

```bash
# Test task creation
python test_task.py
```

### Using curl

```bash
# Create a task
curl -X POST "http://localhost:8000/api/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Research recent AI developments",
    "user_id": "test_user"
  }'

# Check task status
curl "http://localhost:8000/api/tasks/1"
```

### Using Python

```python
import requests

# Create task
response = requests.post(
    "http://localhost:8000/api/tasks",
    json={
        "description": "Summarize the benefits of AI",
        "user_id": "user123"
    }
)
task = response.json()

# Get task status
task_status = requests.get(
    f"http://localhost:8000/api/tasks/{task['task_id']}"
).json()

print(task_status)
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key for LangGraph | Required |
| `GROQ_API_KEY` | Groq API key (alternative) | Optional |
| `DATABASE_URL` | Database connection string | `sqlite:///./agent_orchestrator.db` |
| `FRONTEND_URL` | Frontend URL for CORS | `http://localhost:3000` |
| `LLM_PROVIDER` | LLM provider (openai/groq) | `openai` |

### Database Configuration

The system uses SQLite by default. To use PostgreSQL:

```env
DATABASE_URL=postgresql://user:password@localhost/dbname
```

## 🐛 Troubleshooting

### Common Issues

**1. Database locked error**
```bash
# Remove database and restart
rm agent_orchestrator.db
python main.py
```

**2. Import errors**
```bash
# Ensure all dependencies are installed
pip install -r requirements.txt
```

**3. API key errors**
```bash
# Verify .env file exists and contains valid keys
cat .env
```

**4. Port already in use**
```bash
# Windows: Find and kill process
netstat -ano | findstr :8000
taskkill /PID <process_id> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

## 📚 Dependencies

Key dependencies:

- **FastAPI** - Modern web framework
- **SQLAlchemy** - ORM for database
- **LangChain** - LLM framework
- **LangGraph** - Agent workflow graphs
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation
- **OpenAI** - OpenAI API client
- **httpx** - Async HTTP client

See `requirements.txt` for complete list.

## 🔐 Security Considerations

1. **API Keys**: Never commit API keys to version control
2. **Environment Variables**: Use `.env` file (not tracked by git)
3. **CORS**: Configure `FRONTEND_URL` appropriately for production
4. **Database**: Use strong credentials for production databases
5. **Rate Limiting**: Implement rate limiting for production deployments

## 📈 Performance Tips

1. **Connection Pooling**: Configure SQLAlchemy connection pool
2. **Async Operations**: Use async/await for I/O operations
3. **Caching**: Implement caching for frequently accessed data
4. **Background Tasks**: Use BackgroundTasks for long-running operations

## 🚀 Production Deployment

### Using Docker

```bash
docker build -t multi-agent-orchestrator .
docker run -d -p 8000:8000 \
  -e OPENAI_API_KEY=your-key \
  multi-agent-orchestrator
```

### Using Gunicorn

```bash
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

## 📝 API Response Examples

### Create Task Response
```json
{
  "task_id": 1,
  "session_id": "sess_abc123",
  "status": "planning",
  "plan": {
    "steps": [
      {
        "step_number": 1,
        "agent_id": 1,
        "description": "Research AI trends"
      }
    ]
  },
  "created_at": "2025-11-02T19:30:00Z"
}
```

### Get Task Response
```json
{
  "id": 1,
  "session_id": "sess_abc123",
  "description": "Research AI trends",
  "status": "completed",
  "result": {
    "summary": "AI trends analysis...",
    "insights": ["Trend 1", "Trend 2"]
  },
  "steps": [
    {
      "step_number": 1,
      "status": "completed",
      "output_data": {...}
    }
  ],
  "completed_at": "2025-11-02T19:35:00Z"
}
```

## 🤝 Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

## 📄 License

MIT License - See LICENSE file for details.

