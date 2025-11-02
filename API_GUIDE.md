# API Guide - Multi-Agent Orchestrator

Comprehensive API documentation for the Multi-Agent Orchestrator system.

## 📡 Base URLs

- **Main Orchestrator**: `http://localhost:8000`
- **A2A Server**: `http://localhost:8001`
- **API Agent**: `http://localhost:8002`

## 🔐 Authentication

Currently, the API does not require authentication. For production deployments, implement:
- API Keys
- OAuth 2.0
- JWT tokens

## 📚 Main Orchestrator API

### Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "multi-agent-orchestrator"
}
```

---

## 🤖 Agent Management

### Register Agent

```http
POST /api/agents/register
```

**Request Body:**
```json
{
  "name": "ResearchAgent",
  "description": "AI research assistant with analysis capabilities",
  "agent_type": "A2A_SERVER",
  "endpoint": "http://localhost:8001",
  "capabilities": ["research", "analysis", "summarization"],
  "config": {
    "model": "gpt-4",
    "temperature": 0.7
  },
  "metadata": {
    "version": "1.0.0",
    "author": "system"
  }
}
```

**Response:**
```json
{
  "id": 1,
  "name": "ResearchAgent",
  "status": "ACTIVE",
  "agent_type": "A2A_SERVER"
}
```

**Agent Types:**
- `A2A_SERVER` - Agent-to-Agent protocol server
- `API` - Simple API-based agent
- `LANGGRAPH` - LangGraph workflow agent

---

### List All Agents

```http
GET /api/agents
```

**Query Parameters:**
- `agent_type` (optional): Filter by agent type
- `status` (optional): Filter by status (ACTIVE, INACTIVE, ERROR)

**Response:**
```json
[
  {
    "id": 1,
    "name": "ResearchAgent",
    "description": "AI research assistant",
    "agent_type": "A2A_SERVER",
    "endpoint": "http://localhost:8001",
    "capabilities": ["research", "analysis"],
    "status": "ACTIVE",
    "created_at": "2025-11-02T19:00:00Z"
  },
  {
    "id": 2,
    "name": "DataAnalyzer",
    "description": "Data analysis agent",
    "agent_type": "API",
    "endpoint": "http://localhost:8002",
    "capabilities": ["data_analysis", "summarization"],
    "status": "ACTIVE",
    "created_at": "2025-11-02T19:05:00Z"
  }
]
```

---

### Get Agent Details

```http
GET /api/agents/{agent_id}
```

**Response:**
```json
{
  "id": 1,
  "name": "ResearchAgent",
  "description": "AI research assistant",
  "agent_type": "A2A_SERVER",
  "endpoint": "http://localhost:8001",
  "capabilities": ["research", "analysis"],
  "status": "ACTIVE",
  "config": {
    "model": "gpt-4",
    "temperature": 0.7
  },
  "metadata": {
    "version": "1.0.0"
  },
  "created_at": "2025-11-02T19:00:00Z"
}
```

---

### Update Agent

```http
PUT /api/agents/{agent_id}
```

**Request Body:**
```json
{
  "description": "Updated description",
  "endpoint": "http://localhost:8001",
  "capabilities": ["research", "analysis", "planning"],
  "status": "ACTIVE",
  "config": {
    "model": "gpt-4-turbo",
    "temperature": 0.5
  }
}
```

**Response:**
```json
{
  "id": 1,
  "name": "ResearchAgent",
  "status": "ACTIVE"
}
```

---

### Check Agent Health

```http
POST /api/agents/{agent_id}/health
```

**Response:**
```json
{
  "agent_id": 1,
  "status": "healthy",
  "endpoint": "http://localhost:8001",
  "response_time_ms": 45,
  "checked_at": "2025-11-02T19:30:00Z"
}
```

---

### Get Agent Statistics

```http
GET /api/agents/stats
```

**Response:**
```json
{
  "total_agents": 2,
  "active_agents": 2,
  "inactive_agents": 0,
  "agents_by_type": {
    "A2A_SERVER": 1,
    "API": 1
  }
}
```

---

## 📋 Task Management

### Create Task

```http
POST /api/tasks
```

**Request Body:**
```json
{
  "description": "Research the latest trends in AI and create a comprehensive summary",
  "session_id": "sess_abc123",
  "user_id": "user_456",
  "metadata": {
    "priority": "high",
    "tags": ["AI", "research"]
  }
}
```

**Response:**
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
        "description": "Research AI trends",
        "capability_required": "research"
      },
      {
        "step_number": 2,
        "agent_id": 2,
        "description": "Analyze and summarize findings",
        "capability_required": "data_analysis"
      }
    ]
  },
  "created_at": "2025-11-02T19:30:00Z"
}
```

**Task Status Values:**
- `PENDING` - Task created, not yet planned
- `PLANNING` - Creating execution plan
- `EXECUTING` - Currently executing
- `COMPLETED` - Successfully completed
- `FAILED` - Execution failed
- `CANCELLED` - Manually cancelled

---

### Get Task Status

```http
GET /api/tasks/{task_id}
```

**Response:**
```json
{
  "id": 1,
  "session_id": "sess_abc123",
  "description": "Research AI trends",
  "status": "completed",
  "plan": {
    "steps": [...]
  },
  "result": {
    "summary": "AI is rapidly evolving...",
    "key_findings": [
      "Large language models dominate",
      "Multimodal AI is emerging"
    ],
    "sources": ["source1", "source2"]
  },
  "steps": [
    {
      "step_number": 1,
      "description": "Research AI trends",
      "status": "completed",
      "agent_id": 1,
      "output_data": {
        "findings": "..."
      }
    }
  ],
  "created_at": "2025-11-02T19:30:00Z",
  "completed_at": "2025-11-02T19:35:00Z"
}
```

---

### Cancel Task

```http
POST /api/tasks/{task_id}/cancel
```

**Response:**
```json
{
  "task_id": 1,
  "status": "cancelled",
  "message": "Task cancelled successfully"
}
```

---

## 💬 Session Management

### Create Session

```http
POST /api/sessions
```

**Query Parameters:**
- `user_id` (required): User identifier
- `metadata` (optional): Additional metadata

**Request Body:**
```json
{
  "user_id": "user_123",
  "metadata": {
    "source": "web_app",
    "user_agent": "Mozilla/5.0..."
  }
}
```

**Response:**
```json
{
  "session_id": "sess_abc123",
  "user_id": "user_123",
  "created_at": "2025-11-02T19:30:00Z"
}
```

---

### Add Message to Session

```http
POST /api/sessions/{session_id}/messages
```

**Request Body:**
```json
{
  "session_id": "sess_abc123",
  "role": "user",
  "content": "Tell me about artificial intelligence",
  "metadata": {
    "source": "text_input",
    "language": "en"
  }
}
```

**Response:**
```json
{
  "id": 1,
  "role": "user",
  "content": "Tell me about artificial intelligence",
  "timestamp": "2025-11-02T19:30:00Z"
}
```

---

### Get Conversation History

```http
GET /api/sessions/{session_id}/messages
```

**Query Parameters:**
- `limit` (optional, default: 50): Maximum number of messages

**Response:**
```json
[
  {
    "id": 1,
    "role": "user",
    "content": "Tell me about AI",
    "agent_id": null,
    "timestamp": "2025-11-02T19:30:00Z",
    "metadata": {}
  },
  {
    "id": 2,
    "role": "assistant",
    "content": "AI is...",
    "agent_id": 1,
    "timestamp": "2025-11-02T19:30:15Z",
    "metadata": {}
  }
]
```

---

### Get Session Summary

```http
GET /api/sessions/{session_id}
```

**Response:**
```json
{
  "session_id": "sess_abc123",
  "user_id": "user_123",
  "message_count": 10,
  "created_at": "2025-11-02T19:00:00Z",
  "last_activity": "2025-11-02T19:30:00Z",
  "metadata": {
    "source": "web_app"
  }
}
```

---

## 🔄 A2A Protocol

### Send A2A Message

```http
POST /a2a/message
```

**Request Body:**
```json
{
  "sender": "MainOrchestrator",
  "receiver": "ResearchAgent",
  "message_type": "request",
  "session_id": "sess_abc123",
  "content": {
    "description": "Research AI trends",
    "context": {
      "previous_findings": "..."
    }
  },
  "metadata": {
    "priority": "high",
    "timeout": 30
  }
}
```

**Response:**
```json
{
  "status": "received",
  "message_id": "sess_abc123",
  "receiver": "ResearchAgent",
  "processed_at": "2025-11-02T19:30:00Z"
}
```

---

## 🤖 A2A Server API (Port 8001)

### Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "agent": "ResearchAgent",
  "service": "a2a-server"
}
```

---

### Get Capabilities

```http
GET /capabilities
```

**Response:**
```json
{
  "agent_name": "ResearchAgent",
  "capabilities": [
    "research",
    "analysis",
    "planning",
    "reasoning",
    "reflection"
  ],
  "protocol": "A2A",
  "graph_type": "LangGraph"
}
```

---

### Process A2A Message

```http
POST /a2a/message
```

**Request Body:**
```json
{
  "sender": "MainOrchestrator",
  "receiver": "ResearchAgent",
  "message_type": "request",
  "session_id": "sess_abc123",
  "content": {
    "description": "Research AI developments in 2024",
    "context": {}
  }
}
```

**Response:**
```json
{
  "sender": "ResearchAgent",
  "receiver": "MainOrchestrator",
  "message_type": "response",
  "session_id": "sess_abc123",
  "content": {
    "status": "success",
    "response": "Based on research...",
    "agent": "ResearchAgent"
  },
  "metadata": {
    "processed_with": "LangGraph",
    "workflow_completed": true
  }
}
```

---

### Direct Processing

```http
POST /process
```

**Request Body:**
```json
{
  "description": "Analyze the impact of AI on healthcare",
  "context": {
    "domain": "healthcare",
    "focus_areas": ["diagnostics", "treatment"]
  },
  "session_id": "sess_abc123"
}
```

**Response:**
```json
{
  "status": "success",
  "session_id": "sess_abc123",
  "result": {
    "agent_name": "ResearchAgent",
    "response": "Analysis of AI in healthcare...",
    "workflow_steps": ["analyze", "plan", "execute", "reflect", "finalize"]
  }
}
```

---

## 🔧 API Agent API (Port 8002)

### Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "agent": "DataAnalyzer",
  "service": "api-agent"
}
```

---

### Get Capabilities

```http
GET /capabilities
```

**Response:**
```json
{
  "agent_name": "DataAnalyzer",
  "capabilities": [
    "data_analysis",
    "summarization",
    "format_conversion"
  ],
  "supported_formats": ["json", "csv", "xml"]
}
```

---

### Process Request

```http
POST /process
```

**Request Body:**
```json
{
  "task_type": "data_analysis",
  "data": {
    "dataset": [1, 2, 3, 4, 5],
    "metrics": ["mean", "median", "std"]
  },
  "instructions": "Calculate statistical metrics",
  "target_format": "json"
}
```

**Response:**
```json
{
  "status": "success",
  "agent": "DataAnalyzer",
  "result": {
    "mean": 3.0,
    "median": 3.0,
    "std": 1.41
  },
  "processing_time_ms": 12
}
```

---

## 📊 Error Responses

All endpoints follow a consistent error response format:

```json
{
  "detail": "Error message describing what went wrong",
  "error_type": "ValidationError",
  "status_code": 400
}
```

### Common Status Codes

- `200 OK` - Successful request
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid request data
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error
- `503 Service Unavailable` - Service temporarily unavailable

---

## 🔄 Rate Limiting

Currently, no rate limiting is implemented. For production:

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1699999999
```

---

## 📝 Examples

### Complete Task Flow

```python
import requests

BASE_URL = "http://localhost:8000"

# 1. Create a session
session_response = requests.post(
    f"{BASE_URL}/api/sessions",
    params={"user_id": "user123"}
)
session_id = session_response.json()["session_id"]

# 2. Create a task
task_response = requests.post(
    f"{BASE_URL}/api/tasks",
    json={
        "description": "Research AI trends and summarize",
        "session_id": session_id,
        "user_id": "user123"
    }
)
task = task_response.json()
task_id = task["task_id"]

# 3. Poll for completion
import time
while True:
    status_response = requests.get(f"{BASE_URL}/api/tasks/{task_id}")
    status = status_response.json()
    
    if status["status"] in ["completed", "failed"]:
        print(f"Task {status['status']}")
        print(f"Result: {status.get('result')}")
        break
    
    time.sleep(2)

# 4. Get conversation history
messages = requests.get(
    f"{BASE_URL}/api/sessions/{session_id}/messages"
).json()
```

---

## 🤝 Contributing

For API changes or additions, please update this guide and submit a pull request.

## 📄 License

MIT License - See LICENSE file for details.

