# Dummy Agent Servers

## Overview

This directory contains **dummy/mock agent servers** that simulate different agent frameworks. These are used for testing the Multi-Agent Orchestrator's ability to connect to external agents via REST APIs.

## Available Dummy Agents

### 1. **CrewAI Agent** (`crewai_agent_server.py`)
- **Port:** 8003
- **Framework:** CrewAI multi-agent collaboration
- **Simulates:** A research team with multiple sub-agents (Researcher, Analyst, Writer)
- **Endpoints:**
  - `GET /health` - Health check
  - `GET /capabilities` - List agent capabilities
  - `POST /kickoff` - Start CrewAI workflow
  - `POST /process` - Generic processing endpoint

**Example Request:**
```bash
curl -X POST http://localhost:8003/process \
  -H "Content-Type: application/json" \
  -d '{"description": "Research AI trends in 2024"}'
```

### 2. **Databricks Foundation Model Agent** (`databricks_agent_server.py`)
- **Port:** 8004
- **Framework:** Databricks LLM serving (Llama, Mistral, etc.)
- **Simulates:** Databricks Foundation Model API responses
- **Endpoints:**
  - `GET /health` - Health check
  - `GET /api/2.0/serving-endpoints` - List endpoints
  - `POST /serving-endpoints/llama-2-70b-chat/invocations` - Model invocation
  - `POST /process` - Generic processing endpoint

**Example Request:**
```bash
curl -X POST http://localhost:8004/process \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer dummy-token" \
  -d '{"description": "What is artificial intelligence?"}'
```

### 3. **OpenAI-Compatible Agent** (`openai_compatible_agent_server.py`)
- **Port:** 8005
- **Framework:** OpenAI API compatible (GPT-3.5, GPT-4, etc.)
- **Simulates:** OpenAI chat completions API
- **Endpoints:**
  - `GET /health` - Health check
  - `GET /v1/models` - List available models
  - `POST /v1/chat/completions` - Chat completion
  - `POST /v1/completions` - Legacy completion
  - `POST /process` - Generic processing endpoint

**Example Request:**
```bash
curl -X POST http://localhost:8005/process \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-dummy-key" \
  -d '{"description": "Hello, how are you?"}'
```

## Quick Start

### Start Individual Agents

```bash
# CrewAI Agent
python crewai_agent_server.py

# Databricks Agent
python databricks_agent_server.py

# OpenAI Compatible Agent
python openai_compatible_agent_server.py
```

### Start All Agents (Windows PowerShell)

```powershell
# From backend/dummy_agents directory
cd backend/dummy_agents

# Start all three agents in separate windows
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python crewai_agent_server.py"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python databricks_agent_server.py"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python openai_compatible_agent_server.py"
```

### Start All Agents (Linux/Mac)

```bash
# From backend/dummy_agents directory
cd backend/dummy_agents

# Start in background
python crewai_agent_server.py &
python databricks_agent_server.py &
python openai_compatible_agent_server.py &

# Or use tmux/screen for better management
```

## Verify Agents are Running

```bash
# Check health endpoints
curl http://localhost:8003/health  # CrewAI
curl http://localhost:8004/health  # Databricks
curl http://localhost:8005/health  # OpenAI Compatible
```

Expected output:
```json
{
  "status": "healthy",
  "agent_type": "crewai",
  "service": "crewai-agent-dummy"
}
```

## Testing with the Orchestrator

### Register CrewAI Agent

```bash
curl -X POST http://localhost:8000/api/agents/register-with-template \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test_CrewAI_Agent",
    "description": "Test agent using CrewAI framework",
    "endpoint": "http://localhost:8003",
    "capabilities": ["research", "analysis", "writing"],
    "template_id": 1
  }'
```

### Register Databricks Agent

```bash
curl -X POST http://localhost:8000/api/agents/register-with-template \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test_Databricks_Agent",
    "description": "Test agent using Databricks Foundation Models",
    "endpoint": "http://localhost:8004",
    "capabilities": ["text_generation", "chat", "analysis"],
    "template_id": 2
  }'
```

### Register OpenAI Compatible Agent

```bash
curl -X POST http://localhost:8000/api/agents/register-with-template \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test_OpenAI_Agent",
    "description": "Test agent using OpenAI-compatible API",
    "endpoint": "http://localhost:8005",
    "capabilities": ["chat", "completion", "text_generation"],
    "template_id": 3
  }'
```

## Response Formats

### CrewAI Response Format
```json
{
  "result": "Final output from the writer agent",
  "workflow": [
    {
      "agent": "Researcher",
      "task": "Research",
      "output": "Research findings..."
    },
    {
      "agent": "Analyst",
      "task": "Analysis",
      "output": "Analysis results..."
    },
    {
      "agent": "Writer",
      "task": "Writing",
      "output": "Final report..."
    }
  ],
  "metadata": {
    "crew_name": "Research_Analysis_Team",
    "agents_used": ["Researcher", "Analyst", "Writer"],
    "execution_time": "3.2s"
  },
  "success": true
}
```

### Databricks Response Format
```json
{
  "id": "chatcmpl-abc123",
  "object": "chat.completion",
  "created": 1699564800,
  "model": "llama-2-70b-chat",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Response text here..."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 50,
    "total_tokens": 60
  }
}
```

### OpenAI Response Format
```json
{
  "id": "chatcmpl-xyz789",
  "object": "chat.completion",
  "created": 1699564800,
  "model": "gpt-3.5-turbo",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Response text here..."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 50,
    "total_tokens": 60
  }
}
```

## Notes

- These are **dummy/mock** servers for testing purposes only
- They don't actually call real LLMs - responses are pre-generated
- They simulate realistic response formats and latencies
- No API keys are required (any token will work)
- All endpoints return successful responses by default

## Troubleshooting

### Port Already in Use
If you get a "port already in use" error:

```bash
# Windows
netstat -ano | findstr :8003
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8003 | xargs kill -9
```

### Module Not Found
Ensure you have FastAPI and dependencies:

```bash
cd backend
pip install -r requirements.txt
```

### Connection Refused
Make sure the dummy agents are running before trying to register them in the orchestrator.

---

## Next Steps

1. Start all dummy agents
2. Start the main orchestrator (backend/main.py)
3. Use the frontend wizard to register agents
4. Test task execution through the orchestrator

---

**Happy Testing! 🚀**

