# Service Flow Documentation

Complete guide to understanding the data flow and service interactions in the Multi-Agent Orchestrator system.

## 📋 Table of Contents

- [System Overview](#system-overview)
- [Service Architecture](#service-architecture)
- [Data Flow](#data-flow)
- [Sequence Diagrams](#sequence-diagrams)
- [Agent Communication](#agent-communication)
- [Task Execution Flow](#task-execution-flow)
- [Error Handling](#error-handling)
- [State Management](#state-management)

## 🏗️ System Overview

The Multi-Agent Orchestrator consists of four main services that work together to process tasks through multiple AI agents.

```
┌─────────────────────────────────────────────────────────────────┐
│                         User/Client                              │
│                    (Browser/API Client)                          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTP/REST
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                     Frontend Service                             │
│                      React + Vite                                │
│                     Port: 3000                                   │
│  • Task creation interface                                       │
│  • Real-time status updates                                      │
│  • Agent management UI                                           │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ REST API
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                  Main Orchestrator Service                       │
│                      FastAPI                                     │
│                     Port: 8000                                   │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │    Agent     │  │     Task     │  │    Memory    │         │
│  │   Registry   │  │   Planner    │  │   Service    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                  │
│  ┌──────────────────────────────────────────────────┐          │
│  │           Task Executor                           │          │
│  │  • Coordinates agent communication                │          │
│  │  • Manages task lifecycle                         │          │
│  │  • Handles failures and retries                   │          │
│  └──────────────────────────────────────────────────┘          │
└────────────┬────────────────────────┬───────────────────────────┘
             │                        │
             │ A2A Protocol           │ REST API
             │                        │
┌────────────▼───────────┐  ┌────────▼──────────────────────────┐
│   A2A Server Service   │  │     API Agent Service             │
│     (LangGraph)        │  │      (Simple API)                 │
│      Port: 8001        │  │       Port: 8002                  │
│                        │  │                                   │
│  ┌──────────────────┐ │  │  ┌─────────────────────────────┐ │
│  │ ResearchAgent    │ │  │  │ DataAnalyzer                │ │
│  │                  │ │  │  │                             │ │
│  │ LangGraph        │ │  │  │ • Data processing           │ │
│  │ Workflow:        │ │  │  │ • Summarization             │ │
│  │ • Analyze        │ │  │  │ • Format conversion         │ │
│  │ • Plan           │ │  │  └─────────────────────────────┘ │
│  │ • Execute        │ │  │                                   │
│  │ • Reflect        │ │  │                                   │
│  │ • Finalize       │ │  │                                   │
│  └──────────────────┘ │  │                                   │
└────────────────────────┘  └───────────────────────────────────┘
             │                        │
             └────────────┬───────────┘
                          │
                          │ LLM API Calls
                          │
             ┌────────────▼───────────┐
             │   External LLM APIs    │
             │                        │
             │  • OpenAI (GPT-4)     │
             │  • Groq (Llama)       │
             └────────────────────────┘
```

## 🔄 Service Architecture

### 1. Frontend Service (Port 3000)

**Responsibilities:**
- User interface rendering
- Form validation and submission
- Real-time status polling
- Display results and errors
- Agent status monitoring

**Technology:**
- React 18
- Vite dev server
- Axios for API calls
- CSS3 for styling

**Key Components:**
```javascript
App.jsx
├── TaskCreation
│   ├── TaskForm
│   └── UserInput
├── TaskMonitoring
│   ├── TaskList
│   ├── TaskStatus
│   └── TaskResults
├── AgentManagement
│   ├── AgentList
│   └── AgentHealth
└── SessionHistory
    └── MessageList
```

### 2. Main Orchestrator Service (Port 8000)

**Responsibilities:**
- Central coordination hub
- API endpoint exposure
- Agent registry management
- Task planning and routing
- Memory/session management
- Background task execution

**Technology:**
- FastAPI framework
- SQLAlchemy ORM
- SQLite/PostgreSQL database
- Pydantic validation
- Uvicorn ASGI server

**Core Modules:**
```
main.py
├── API Routes
│   ├── /api/agents/*
│   ├── /api/tasks/*
│   └── /api/sessions/*
├── services/
│   ├── agent_registry.py    # Agent CRUD operations
│   └── memory_service.py    # Session management
├── orchestrator/
│   ├── task_planner.py      # Task decomposition
│   └── task_executor.py     # Task execution
└── models/
    ├── agent.py             # Agent data model
    ├── task.py              # Task data model
    └── memory.py            # Memory data model
```

### 3. A2A Server Service (Port 8001)

**Responsibilities:**
- LangGraph workflow execution
- Complex reasoning tasks
- Research and analysis
- Multi-step task processing
- A2A protocol handling

**Technology:**
- FastAPI
- LangChain framework
- LangGraph for workflows
- OpenAI/Groq LLM integration

**Workflow Stages:**
```
LangGraph Workflow:
1. Analyze   → Understand task requirements
2. Plan      → Create execution strategy
3. Execute   → Perform the task
4. Reflect   → Evaluate results
5. Finalize  → Prepare final output
```

### 4. API Agent Service (Port 8002)

**Responsibilities:**
- Simple data processing
- Direct API-based tasks
- Data summarization
- Format conversion
- Quick responses

**Technology:**
- FastAPI
- Basic Python processing
- Direct LLM API calls

## 📊 Data Flow

### Complete Request Flow

```
┌─────────┐
│  User   │
│ Action  │
└────┬────┘
     │
     │ 1. HTTP POST /api/tasks
     │    {description, user_id}
     ▼
┌──────────────────────────┐
│   Frontend (3000)        │
│   • Validate input       │
│   • Send API request     │
└────┬─────────────────────┘
     │
     │ 2. POST to Backend
     │
     ▼
┌──────────────────────────────────────────────┐
│   Main Orchestrator (8000)                   │
│                                               │
│   A. Create Session (if needed)              │
│      ├─→ memory_service.create_session()     │
│      └─→ Generate session_id                 │
│                                               │
│   B. Task Planning                           │
│      ├─→ task_planner.create_execution_plan()│
│      ├─→ Decompose task into steps           │
│      ├─→ Match steps to agent capabilities   │
│      └─→ Create TaskStep records             │
│                                               │
│   C. Background Execution                    │
│      └─→ background_tasks.add_task()         │
└────┬─────────────────────────────────────────┘
     │
     │ 3. Return task_id immediately
     │
     ▼
┌──────────────────────────┐
│   Frontend (3000)        │
│   • Show "Processing"    │
│   • Poll for status      │
└────┬─────────────────────┘
     │
     │ 4. Background execution starts
     │
     ▼
┌────────────────────────────────────────────────┐
│   Task Executor (Background)                   │
│                                                 │
│   For each step in plan:                       │
│                                                 │
│   A. Identify target agent                     │
│      └─→ agent_registry.get_agent(agent_id)   │
│                                                 │
│   B. Route to appropriate agent                │
│      ├─→ If A2A_SERVER → POST /a2a/message    │
│      └─→ If API → POST /process               │
└────┬───────────────────────────────────────────┘
     │
     ├─────────────────────┬─────────────────────┐
     │                     │                     │
     │ 5a. A2A Request     │ 5b. API Request    │
     │                     │                     │
     ▼                     ▼                     │
┌──────────────┐    ┌──────────────┐           │
│ A2A Server   │    │  API Agent   │           │
│   (8001)     │    │   (8002)     │           │
│              │    │              │           │
│ • Execute    │    │ • Process    │           │
│   LangGraph  │    │   data       │           │
│   workflow   │    │ • Return     │           │
│ • Return     │    │   result     │           │
│   result     │    │              │           │
└────┬─────────┘    └────┬─────────┘           │
     │                   │                     │
     │ 6a. Result        │ 6b. Result         │
     │                   │                     │
     └─────────┬─────────┘                     │
               │                               │
               ▼                               │
┌──────────────────────────────────────────────┴──┐
│   Task Executor (Process Results)               │
│                                                  │
│   • Store step output                           │
│   • Update step status                          │
│   • Pass output to next step (if needed)        │
│   • Update task progress                        │
└────┬─────────────────────────────────────────── ┘
     │
     │ 7. Repeat for all steps
     │
     ▼
┌───────────────────────────────────────────────┐
│   Task Completion                              │
│   • Aggregate all step results                │
│   • Update task status to "completed"         │
│   • Store final result                        │
│   • Update completion timestamp               │
└────┬──────────────────────────────────────────┘
     │
     │ 8. Status polling catches completion
     │
     ▼
┌──────────────────────────┐
│   Frontend (3000)        │
│   • Display results      │
│   • Show success         │
└──────────────────────────┘
```

## 🔀 Sequence Diagrams

### Task Creation Sequence

```
User         Frontend      Orchestrator    TaskPlanner    Database    Agent
 │               │              │              │             │          │
 │ Create Task   │              │              │             │          │
 ├──────────────►│              │              │             │          │
 │               │ POST /api/tasks             │             │          │
 │               ├─────────────►│              │             │          │
 │               │              │ create_plan()│             │          │
 │               │              ├─────────────►│             │          │
 │               │              │              │ Query       │          │
 │               │              │              │ Agents      │          │
 │               │              │              ├────────────►│          │
 │               │              │              │◄────────────┤          │
 │               │              │              │ Agent List  │          │
 │               │              │◄─────────────┤             │          │
 │               │              │ Task Plan    │             │          │
 │               │              │ Save Task    │             │          │
 │               │              ├──────────────┼────────────►│          │
 │               │◄─────────────┤              │◄────────────┤          │
 │               │ task_id      │              │ Task ID     │          │
 │◄──────────────┤              │              │             │          │
 │ task_id       │              │              │             │          │
 │               │              │ Execute      │             │          │
 │               │              │ Background   │             │          │
 │               │              ├──────────────┼─────────────┼─────────►│
 │               │              │              │             │  Process │
 │               │              │              │             │◄─────────┤
 │               │              │              │             │  Result  │
 │               │              │◄─────────────┼─────────────┼──────────┤
 │               │              │ Update Task  │             │          │
 │               │              ├──────────────┼────────────►│          │
 │               │              │              │◄────────────┤          │
```

### Agent Communication Sequence (A2A Protocol)

```
Orchestrator    A2A Server    LangGraph      LLM API
     │              │             │             │
     │ A2A Request  │             │             │
     ├─────────────►│             │             │
     │              │ Initialize  │             │
     │              │ Workflow    │             │
     │              ├────────────►│             │
     │              │             │ Analyze     │
     │              │             ├────────────►│
     │              │             │◄────────────┤
     │              │             │ Plan        │
     │              │             ├────────────►│
     │              │             │◄────────────┤
     │              │             │ Execute     │
     │              │             ├────────────►│
     │              │             │◄────────────┤
     │              │             │ Reflect     │
     │              │             ├────────────►│
     │              │             │◄────────────┤
     │              │             │ Finalize    │
     │              │             ├────────────►│
     │              │             │◄────────────┤
     │              │◄────────────┤             │
     │◄─────────────┤ A2A Response│             │
     │  Result      │             │             │
```

### Multi-Step Task Execution

```
Orchestrator    Agent1(A2A)   Agent2(API)    Database
     │               │             │             │
     │ Start Task    │             │             │
     ├───────────────┼─────────────┼────────────►│
     │               │             │◄────────────┤
     │ Step 1        │             │  Task Data  │
     ├──────────────►│             │             │
     │               │ Process     │             │
     │               │ (Workflow)  │             │
     │◄──────────────┤             │             │
     │ Result 1      │             │             │
     ├───────────────┼─────────────┼────────────►│
     │               │             │◄────────────┤
     │ Step 2        │             │  Updated    │
     ├───────────────┼────────────►│             │
     │               │             │ Process     │
     │               │             │ (+ Result1) │
     │◄──────────────┼─────────────┤             │
     │ Result 2      │             │             │
     ├───────────────┼─────────────┼────────────►│
     │               │             │◄────────────┤
     │ Complete      │             │  Final Data │
```

## 🤝 Agent Communication

### A2A Protocol Message Structure

```json
{
  "sender": "MainOrchestrator",
  "receiver": "ResearchAgent",
  "message_type": "request",
  "session_id": "sess_abc123",
  "content": {
    "description": "Research AI trends in 2024",
    "context": {
      "previous_results": "...",
      "user_preferences": "..."
    }
  },
  "metadata": {
    "priority": "high",
    "timeout": 30,
    "retry_count": 0
  }
}
```

**Response Structure:**

```json
{
  "sender": "ResearchAgent",
  "receiver": "MainOrchestrator",
  "message_type": "response",
  "session_id": "sess_abc123",
  "content": {
    "status": "success",
    "response": "Based on research...",
    "data": {
      "findings": [...],
      "sources": [...]
    }
  },
  "metadata": {
    "processed_with": "LangGraph",
    "workflow_completed": true,
    "execution_time_ms": 5420
  }
}
```

### API Agent Communication

```json
// Request
{
  "task_type": "data_analysis",
  "data": {
    "dataset": [...],
    "operations": ["summarize", "analyze"]
  },
  "instructions": "Analyze data and provide insights",
  "context": {
    "format": "json",
    "detail_level": "high"
  }
}

// Response
{
  "status": "success",
  "agent": "DataAnalyzer",
  "result": {
    "summary": "...",
    "insights": [...],
    "metrics": {...}
  },
  "processing_time_ms": 150
}
```

## ⚙️ Task Execution Flow

### Phase 1: Task Creation & Planning

```
1. User submits task description
   ↓
2. Create/retrieve session
   ↓
3. Task Planner analyzes description
   ↓
4. Identify required capabilities
   ↓
5. Query Agent Registry for capable agents
   ↓
6. Decompose task into steps
   ↓
7. Assign agents to steps
   ↓
8. Create execution plan
   ↓
9. Save Task record with "planning" status
   ↓
10. Return task_id to user
```

### Phase 2: Background Execution

```
1. Task Executor picks up task
   ↓
2. Load execution plan
   ↓
3. For each step in plan:
   │
   ├─→ Update step status to "executing"
   │   ↓
   ├─→ Get agent details from registry
   │   ↓
   ├─→ Prepare request payload
   │   ↓
   ├─→ Route to agent based on type
   │   │
   │   ├─→ A2A Server: POST /a2a/message
   │   └─→ API Agent: POST /process
   │   ↓
   ├─→ Wait for agent response
   │   ↓
   ├─→ Store step result
   │   ↓
   ├─→ Update step status to "completed"
   │   ↓
   └─→ Pass output to next step (if needed)
   ↓
4. All steps completed
   ↓
5. Aggregate results
   ↓
6. Update task status to "completed"
   ↓
7. Store final result
```

### Phase 3: Result Retrieval

```
1. Frontend polls: GET /api/tasks/{task_id}
   ↓
2. Orchestrator queries database
   ↓
3. Return task with status and results
   ↓
4. Frontend displays to user
```

## 🚨 Error Handling

### Error Flow Diagram

```
Task Execution
     │
     ├─→ Agent Timeout
     │   ├─→ Retry (up to 3 times)
     │   │   ├─→ Success → Continue
     │   │   └─→ Still fails → Mark step as "failed"
     │   └─→ Update task status to "failed"
     │
     ├─→ Agent Returns Error
     │   ├─→ Log error details
     │   ├─→ Mark step as "failed"
     │   └─→ Update task status to "failed"
     │
     ├─→ Agent Unavailable
     │   ├─→ Check health endpoint
     │   ├─→ Find alternative agent (if available)
     │   │   ├─→ Alternative found → Reassign step
     │   │   └─→ No alternative → Mark step as "failed"
     │   └─→ Update task status to "failed"
     │
     └─→ Invalid Response
         ├─→ Validate response format
         ├─→ Log validation error
         ├─→ Mark step as "failed"
         └─→ Update task status to "failed"
```

### Error Response Structure

```json
{
  "task_id": 123,
  "status": "failed",
  "error": {
    "step_number": 2,
    "agent_id": 1,
    "error_type": "AgentTimeoutError",
    "message": "Agent did not respond within 30 seconds",
    "timestamp": "2025-11-02T19:35:00Z",
    "retry_count": 3
  },
  "partial_results": {
    "step_1": {
      "status": "completed",
      "output": "..."
    }
  }
}
```

### Retry Logic

```python
MAX_RETRIES = 3
RETRY_DELAY = [2, 5, 10]  # Exponential backoff

async def execute_step_with_retry(step, agent):
    for attempt in range(MAX_RETRIES):
        try:
            result = await call_agent(agent, step)
            return result
        except TimeoutError:
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(RETRY_DELAY[attempt])
                continue
            else:
                raise
        except AgentError as e:
            # Don't retry on agent errors
            raise
```

## 💾 State Management

### Database Schema Relations

```
┌─────────────────┐
│     Agent       │
│─────────────────│
│ id (PK)         │
│ name            │
│ agent_type      │
│ endpoint        │
│ capabilities[]  │
│ status          │
└────────┬────────┘
         │
         │ 1:N
         │
┌────────▼────────────┐
│     Task            │
│─────────────────────│
│ id (PK)             │
│ session_id (FK)     │
│ description         │
│ status              │
│ plan {}             │
│ result {}           │
└────────┬────────────┘
         │
         │ 1:N
         │
┌────────▼─────────────┐
│     TaskStep         │
│──────────────────────│
│ id (PK)              │
│ task_id (FK)         │
│ agent_id (FK)        │
│ step_number          │
│ description          │
│ status               │
│ output_data {}       │
└──────────────────────┘

┌──────────────────────┐
│ ConversationContext  │
│──────────────────────│
│ id (PK)              │
│ session_id           │
│ user_id              │
│ metadata {}          │
└────────┬─────────────┘
         │
         │ 1:N
         │
┌────────▼─────────────┐
│     Message          │
│──────────────────────│
│ id (PK)              │
│ context_id (FK)      │
│ agent_id (FK)        │
│ role                 │
│ content              │
│ timestamp            │
└──────────────────────┘
```

### Task State Transitions

```
PENDING
   │
   ├─→ create_execution_plan()
   │
   ▼
PLANNING
   │
   ├─→ plan_created()
   │
   ▼
EXECUTING
   │
   ├─→ all_steps_completed()
   │   ↓
   │   COMPLETED
   │
   ├─→ step_failed()
   │   ↓
   │   FAILED
   │
   └─→ user_cancelled()
       ↓
       CANCELLED
```

### Session Lifecycle

```
1. Create Session
   ├─→ Generate unique session_id
   ├─→ Store user_id
   └─→ Initialize empty message list

2. Add Messages
   ├─→ User messages
   ├─→ Assistant messages
   └─→ System messages

3. Maintain Context
   ├─→ Keep last N messages
   ├─→ Summarize older messages
   └─→ Store metadata

4. Session Expiry
   ├─→ After 24 hours of inactivity
   └─→ Archive to long-term storage
```

## 🔍 Monitoring & Observability

### Health Check Flow

```
┌──────────────┐
│  Monitoring  │
│   System     │
└──────┬───────┘
       │
       ├─→ GET /health (Main: 8000)
       │   └─→ {"status": "healthy"}
       │
       ├─→ GET /health (A2A: 8001)
       │   └─→ {"status": "healthy", "agent": "ResearchAgent"}
       │
       └─→ GET /health (API: 8002)
           └─→ {"status": "healthy", "agent": "DataAnalyzer"}
```

### Logging Flow

```
Request
   ↓
[Timestamp] [Level] [Service] [Component] Message
   ↓
2025-11-02 19:30:00 INFO MainOrchestrator TaskPlanner "Creating plan for task 123"
2025-11-02 19:30:01 DEBUG TaskExecutor Executor "Executing step 1 with agent 1"
2025-11-02 19:30:05 INFO A2AServer LangGraph "Workflow completed successfully"
2025-11-02 19:30:06 ERROR TaskExecutor Executor "Agent timeout after 30s"
```

## 🚀 Performance Considerations

### Async Operations

```python
# Parallel agent calls when possible
async def execute_parallel_steps(steps):
    tasks = [
        execute_step(step) 
        for step in steps 
        if can_execute_parallel(step)
    ]
    results = await asyncio.gather(*tasks)
    return results
```

### Caching Strategy

```
1. Agent Registry Cache
   ├─→ Cache agent details for 5 minutes
   └─→ Invalidate on agent update

2. Session Cache
   ├─→ Cache active sessions in memory
   └─→ Expire after 30 minutes

3. LLM Response Cache
   ├─→ Cache identical queries for 1 hour
   └─→ Use semantic similarity for cache hits
```

## 📚 Additional Resources

- [Main README](README.md) - Project overview
- [API Guide](API_GUIDE.md) - Complete API reference
- [Backend README](backend/README.md) - Backend documentation
- [Frontend README](frontend/README.md) - Frontend documentation
- [Contributing](CONTRIBUTING.md) - Contribution guidelines

## 🔄 Version History

- **v1.0.0** (2025-11-02) - Initial service flow documentation

---

For questions or clarifications about the service flow, please open an issue on GitHub.

