# REST API Agent Service Flow with Adapter Pattern

## 🎯 Overview

This document explains the complete service flow for connecting to REST API agents using the adapter pattern in the Multi-Agent Orchestrator.

---

## 📐 Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                         Frontend (React)                         │
│                      http://localhost:3000                       │
└────────────────────────────┬─────────────────────────────────────┘
                             │ HTTP POST /api/tasks
                             │ { description: "Analyze data X" }
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│                   Main Orchestrator (FastAPI)                    │
│                      http://localhost:8000                       │
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐     │
│  │ Agent        │    │ Task         │    │ Task         │     │
│  │ Registry     │◄───┤ Planner      │◄───┤ Executor     │     │
│  │              │    │              │    │ (Adapter)    │     │
│  └──────────────┘    └──────────────┘    └──────┬───────┘     │
│         │                                         │              │
└─────────┼─────────────────────────────────────────┼─────────────┘
          │                                         │
          │ 1. Lookup agent by ID/capability       │
          │                                         │ 2. HTTP POST
          │                                         │    /process
          ▼                                         ▼
┌──────────────────────────────────────────────────────────────────┐
│                  REST API Agent Server (FastAPI)                 │
│                      http://localhost:8002                       │
│                                                                  │
│  ┌────────────────┐         ┌──────────────────────┐           │
│  │ APIAgent       │◄────────┤ FastAPI Endpoints    │           │
│  │ (DataAnalyzer) │         │                      │           │
│  │                │         │ GET  /health         │           │
│  │ - process()    │         │ GET  /capabilities   │           │
│  │ - analyze()    │         │ POST /process        │           │
│  │ - summarize()  │         └──────────────────────┘           │
│  └────────┬───────┘                                             │
│           │                                                      │
│           ▼                                                      │
│  ┌────────────────┐                                             │
│  │ LLM (Groq)     │                                             │
│  │ Llama 3.3 70B  │                                             │
│  └────────────────┘                                             │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Complete Service Flow (Step-by-Step)

### **Phase 1: Agent Registration**

#### Step 1: Agent Server Startup
```python
# File: backend/api_agent_server.py
api_agent = APIAgent(agent_name="DataAnalyzer")
app = FastAPI()
# Runs on http://localhost:8002
```

#### Step 2: Agent Self-Registration
```http
POST http://localhost:8000/api/agents/register
Content-Type: application/json

{
  "name": "DataAnalyzer",
  "description": "API agent for data analysis",
  "agent_type": "api",
  "endpoint": "http://localhost:8002",
  "capabilities": [
    "data_analysis",
    "text_processing",
    "summarization",
    "calculation",
    "simple_queries"
  ]
}
```

#### Step 3: Registry Storage
```python
# File: backend/services/agent_registry.py
class AgentRegistry:
    def register_agent(self, name, description, agent_type, endpoint, capabilities):
        agent = Agent(
            name=name,
            agent_type=AgentType.API,  # ← Identifies as REST API agent
            endpoint=endpoint,          # ← HTTP endpoint URL
            capabilities=capabilities
        )
        self.db.add(agent)
        self.db.commit()
```

**Database Entry:**
```
agents table:
┌────┬──────────────┬──────────┬────────────────────────┬────────────────────────┐
│ id │ name         │ type     │ endpoint               │ capabilities           │
├────┼──────────────┼──────────┼────────────────────────┼────────────────────────┤
│ 2  │ DataAnalyzer │ api      │ http://localhost:8002  │ ["data_analysis",...]  │
└────┴──────────────┴──────────┴────────────────────────┴────────────────────────┘
```

---

### **Phase 2: Task Creation & Planning**

#### Step 4: User Request from Frontend
```javascript
// Frontend sends task
const response = await axios.post('http://localhost:8000/api/tasks', {
  description: 'Analyze quarterly sales data',
  user_id: 'demo-user',
  session_id: 'session-123'
});
```

#### Step 5: Task Planning (Agent Selection)
```python
# File: backend/orchestrator/task_planner.py
class TaskPlanner:
    async def create_execution_plan(self, task_description, session_id):
        # 1. Get all available agents from registry
        agents = registry.list_agents(status=AgentStatus.ACTIVE)
        
        # 2. Use LLM to create plan
        plan = await self._generate_plan(task_description, agents)
        
        # 3. Create task in database
        task = Task(
            description=task_description,
            session_id=session_id,
            status=TaskStatus.PENDING,
            plan=plan
        )
        
        # 4. Create task steps
        for step_info in plan['steps']:
            step = TaskStep(
                task_id=task.id,
                step_number=step_info['step_number'],
                description=step_info['description'],
                agent_id=step_info['agent_id'],  # ← DataAnalyzer ID
                status=TaskStatus.PENDING
            )
```

**LLM Planning Prompt:**
```
Available Agents:
- DataAnalyzer (API): data_analysis, calculation, simple_queries
- ResearchAgent (A2A): research, complex_analysis

Task: "Analyze quarterly sales data"

→ LLM selects DataAnalyzer because it has "data_analysis" capability
```

**Plan Output:**
```json
{
  "steps": [
    {
      "step_number": 1,
      "description": "Analyze quarterly sales data",
      "agent_id": 2,
      "agent_name": "DataAnalyzer",
      "expected_output": "Sales analysis with trends"
    }
  ],
  "complexity": "low"
}
```

---

### **Phase 3: Task Execution (Adapter Pattern)**

#### Step 6: Task Executor Initialization
```python
# File: backend/orchestrator/task_executor.py
class TaskExecutor:
    """
    TaskExecutor acts as an ADAPTER between the orchestrator
    and different agent types (API, A2A, etc.)
    """
    
    async def execute_task(self, task_id):
        # Get task steps
        steps = db.query(TaskStep).filter(TaskStep.task_id == task_id).all()
        
        for step in steps:
            # Execute each step through appropriate adapter
            result = await self.execute_step(step, context)
```

#### Step 7: Agent Type Detection (Adapter Routing)
```python
async def execute_step(self, step: TaskStep, context: Dict):
    # 1. Get agent info from registry
    agent = db.query(Agent).filter(Agent.id == step.agent_id).first()
    
    # 2. Prepare input data
    input_data = {
        "description": step.description,
        "context": context,
        "step_input": step.input_data
    }
    
    # 3. Route to appropriate adapter based on agent type
    if agent.agent_type == AgentType.API:
        result = await self._execute_api_agent(agent, input_data)  # ← REST API Adapter
    elif agent.agent_type == AgentType.A2A_SERVER:
        result = await self._execute_a2a_agent(agent, input_data)  # ← A2A Adapter
    
    return result
```

#### Step 8: REST API Adapter Execution
```python
async def _execute_api_agent(self, agent: Agent, input_data: Dict) -> Dict:
    """
    REST API ADAPTER: Translates orchestrator requests to HTTP calls
    """
    
    # 1. Create HTTP client
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            # 2. Convert input_data to API agent's expected format
            payload = {
                "task_type": "data_analysis",  # ← Adapter determines task type
                "data": input_data.get("description"),
                "instructions": input_data.get("context", "")
            }
            
            # 3. Make HTTP POST request to agent endpoint
            response = await client.post(
                f"{agent.endpoint}/process",  # ← http://localhost:8002/process
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            # 4. Handle response
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPError as e:
            return {
                "error": str(e),
                "agent": agent.name,
                "status": "failed"
            }
```

**HTTP Request sent by Adapter:**
```http
POST http://localhost:8002/process HTTP/1.1
Content-Type: application/json

{
  "task_type": "data_analysis",
  "data": "Analyze quarterly sales data",
  "instructions": ""
}
```

---

### **Phase 4: REST API Agent Processing**

#### Step 9: API Agent Server Receives Request
```python
# File: backend/api_agent_server.py
@app.post("/process")
async def process_request(request: ProcessRequest):
    """FastAPI endpoint receives the HTTP request"""
    
    # 1. Request is validated by Pydantic model
    # 2. Forward to APIAgent instance
    result = await api_agent.process_request(request.dict())
    return result
```

#### Step 10: APIAgent Processes Request
```python
# File: backend/agents/api_agent.py
class APIAgent:
    async def process_request(self, request: Dict) -> Dict:
        """Main request router"""
        
        task_type = request.get("task_type")  # "data_analysis"
        data = request.get("data")
        instructions = request.get("instructions")
        
        # Route to specific handler
        if task_type == "data_analysis":
            return await self._analyze_data(data, instructions)
        elif task_type == "calculation":
            return await self._handle_simple_query(data)
        # ... more handlers
```

#### Step 11: Data Analysis Execution
```python
async def _analyze_data(self, data: Any, instructions: str) -> Dict:
    """Execute data analysis using LLM"""
    
    # 1. Construct prompt
    prompt = f"""
    Analyze the following data:
    {data}
    
    Instructions: {instructions}
    
    Provide detailed analysis with insights and recommendations.
    """
    
    # 2. Call LLM (Groq)
    response = self.llm.invoke([HumanMessage(content=prompt)])
    
    # 3. Return structured response
    return {
        "status": "success",
        "agent": self.agent_name,
        "task": "data_analysis",
        "result": response.content  # ← LLM analysis result
    }
```

**LLM Call:**
```
User → APIAgent → ChatGroq (Llama 3.3 70B) → Analysis Result
```

---

### **Phase 5: Response Flow Back**

#### Step 12: API Agent Returns HTTP Response
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "status": "success",
  "agent": "DataAnalyzer",
  "task": "data_analysis",
  "result": "Based on the quarterly sales data analysis:\n\n1. Revenue increased 15%..."
}
```

#### Step 13: Adapter Processes Response
```python
# Back in TaskExecutor._execute_api_agent()
response = await client.post(...)
result = response.json()  # ← Receives response from API agent

# Adapter returns result to execute_step()
return result
```

#### Step 14: Task Executor Updates Database
```python
# File: backend/orchestrator/task_executor.py
async def execute_task(self, task_id):
    for step in steps:
        step_result = await self.execute_step(step, context)  # ← Got result
        
        # Update step in database
        step.status = TaskStatus.COMPLETED
        step.output_data = step_result
        step.completed_at = datetime.utcnow()
        db.commit()
        
        # Add to context for next steps
        context[f"step_{step.step_number}"] = step_result
    
    # Mark task as completed
    task.status = TaskStatus.COMPLETED
    task.result = {
        "status": "completed",
        "steps": results,
        "summary": "Analysis completed successfully"
    }
    task.completed_at = datetime.utcnow()
    db.commit()
```

#### Step 15: Frontend Polls for Result
```javascript
// Frontend polling (every 2 seconds)
const pollInterval = setInterval(async () => {
  const statusResponse = await axios.get(`/api/tasks/${taskId}`);
  
  if (statusResponse.data.status === 'completed') {
    clearInterval(pollInterval);
    
    // Extract result
    const result = statusResponse.data.result.steps[0].result;
    
    // Display to user
    displayMessage(result);
  }
}, 2000);
```

---

## 🔌 Adapter Pattern Explained

### What is the Adapter?

The **TaskExecutor** class acts as an **Adapter** between the orchestrator and different agent types:

```
┌─────────────────────────────────────────────────────────────┐
│                    ADAPTER PATTERN                          │
│                                                             │
│  Orchestrator          TaskExecutor           Agents       │
│  (Client)              (Adapter)              (Services)    │
│                                                             │
│      ┌──────┐         ┌──────────┐           ┌──────────┐ │
│      │ Task │────────►│ execute_ │──────────►│ API      │ │
│      │ Plan │         │ api_agent│  HTTP     │ Agent    │ │
│      └──────┘         └──────────┘           └──────────┘ │
│                            │                               │
│                            │                  ┌──────────┐ │
│                            └─────────────────►│ A2A      │ │
│                               A2A Protocol    │ Agent    │ │
│                                               └──────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Why Use an Adapter?

1. **Abstraction**: Orchestrator doesn't need to know how each agent communicates
2. **Flexibility**: Easy to add new agent types (WebSocket, gRPC, etc.)
3. **Consistency**: All agents return results in the same format
4. **Maintainability**: Agent communication logic is centralized

### Adapter Methods

| Method | Purpose | Protocol |
|--------|---------|----------|
| `_execute_api_agent()` | REST API agents | HTTP POST |
| `_execute_a2a_agent()` | A2A protocol agents | A2A Messages |
| `_execute_websocket_agent()` | (Future) WebSocket agents | WebSocket |

---

## 📊 Sequence Diagram

```
Frontend    Orchestrator    TaskExecutor    Registry    API Agent    LLM
   │              │              │            │            │          │
   ├──POST /tasks─►              │            │            │          │
   │              │              │            │            │          │
   │              ├──plan task───┼──get agents►            │          │
   │              │              │            │            │          │
   │              ├──create task─►            │            │          │
   │              │              │            │            │          │
   │              ├──execute─────►            │            │          │
   │              │              │            │            │          │
   │              │              ├─get agent──►            │          │
   │              │              │            │            │          │
   │              │              ├─HTTP POST──────────────►│          │
   │              │              │    /process             │          │
   │              │              │            │            │          │
   │              │              │            │            ├─invoke──►│
   │              │              │            │            │          │
   │              │              │            │            ◄──response┤
   │              │              │            │            │          │
   │              │              ◄───JSON response─────────┤          │
   │              │              │            │            │          │
   │              ◄──update task─┤            │            │          │
   │              │              │            │            │          │
   ◄──GET result──┤              │            │            │          │
   │              │              │            │            │          │
```

---

## 🛠️ Key Components

### 1. **Agent Registry** (Service Discovery)
```python
# Stores agent metadata
- Agent ID, name, type
- HTTP endpoint URL
- Capabilities list
- Status (active/inactive)
```

### 2. **Task Planner** (Orchestration Logic)
```python
# Decides which agent handles which task
- Analyzes task requirements
- Matches capabilities to agents
- Creates execution plan
```

### 3. **Task Executor** (Adapter)
```python
# Executes tasks through appropriate protocols
- Routes to correct agent type
- Handles HTTP communication
- Manages errors and retries
```

### 4. **API Agent Server** (REST Service)
```python
# Exposes REST API endpoints
- GET  /health - Health check
- GET  /capabilities - Agent capabilities
- POST /process - Process requests
```

### 5. **API Agent** (Business Logic)
```python
# Processes tasks using LLM
- Data analysis
- Text processing
- Calculations
- Summarization
```

---

## 📡 Communication Protocol

### Request Format (Orchestrator → API Agent)
```json
{
  "task_type": "data_analysis",
  "data": "Raw data or task description",
  "instructions": "Additional context",
  "target_format": "Optional output format"
}
```

### Response Format (API Agent → Orchestrator)
```json
{
  "status": "success",
  "agent": "DataAnalyzer",
  "task": "data_analysis",
  "result": "Analysis result or output"
}
```

### Error Format
```json
{
  "error": "Error message",
  "agent": "DataAnalyzer",
  "status": "failed"
}
```

---

## 🔍 Example: End-to-End Flow

### User Request: "Calculate 1+1"

1. **Frontend** sends: `POST /api/tasks { description: "1+1" }`
2. **Task Planner** analyzes: "Simple calculation" → assigns to DataAnalyzer
3. **Task Executor** calls: `_execute_api_agent()`
4. **Adapter** sends HTTP: `POST http://localhost:8002/process`
5. **API Agent** receives: `{ task_type: "calculation", data: "1+1" }`
6. **APIAgent** processes: `_handle_simple_query("1+1")`
7. **LLM** responds: "The answer is 2"
8. **API Agent** returns: `{ status: "success", result: "2" }`
9. **Adapter** receives HTTP response
10. **Task Executor** updates database
11. **Frontend** polls and displays: "2"

**Total Time**: ~2-3 seconds

---

## ⚡ Performance Considerations

### HTTP Connection Pooling
```python
# Uses httpx.AsyncClient for efficient connections
async with httpx.AsyncClient(timeout=60.0) as client:
    # Reuses connections automatically
```

### Timeout Configuration
```python
timeout=60.0  # 60 seconds for long-running tasks
```

### Concurrent Execution
```python
# Multiple steps can execute in parallel if no dependencies
tasks = [execute_step(step) for step in parallel_steps]
results = await asyncio.gather(*tasks)
```

---

## 🔒 Security Features

1. **CORS Configuration**: Restricts frontend origins
2. **Input Validation**: Pydantic models validate requests
3. **Error Handling**: Graceful failure with error messages
4. **Timeout Protection**: Prevents hanging requests
5. **Health Checks**: Monitors agent availability

---

## 🧪 Testing the Flow

### Test API Agent Health
```bash
curl http://localhost:8002/health
```

### Test Direct API Call
```bash
curl -X POST http://localhost:8002/process \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "calculation",
    "data": "5 * 10"
  }'
```

### Test Through Orchestrator
```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Calculate 5 * 10",
    "user_id": "test-user"
  }'
```

---

## 📚 Related Documentation

- [SERVICE_FLOW.md](SERVICE_FLOW.md) - Overall system architecture
- [API_GUIDE.md](API_GUIDE.md) - API endpoint documentation
- [Backend README](backend/README.md) - Backend setup guide

---

**Last Updated**: November 2025  
**Version**: 1.0.0

