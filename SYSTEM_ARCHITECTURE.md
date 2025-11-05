# Multi-Agent Orchestrator - System Architecture

Comprehensive documentation of the system architecture, modules, and design patterns.

## 📋 Table of Contents

- [System Overview](#system-overview)
- [Architecture Layers](#architecture-layers)
- [Core Modules](#core-modules)
- [Service Components](#service-components)
- [Data Models](#data-models)
- [Agent System](#agent-system)
- [Communication Protocols](#communication-protocols)
- [Database Schema](#database-schema)
- [Design Patterns](#design-patterns)
- [Deployment Architecture](#deployment-architecture)

## 🏗️ System Overview

The Multi-Agent Orchestrator is a sophisticated multi-agent coordination system built with a microservices architecture. It enables seamless integration and orchestration of heterogeneous AI agents with different capabilities, frameworks, and communication protocols.

### High-Level Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                         Presentation Layer                            │
│  ┌────────────────────────────────────────────────────────────┐     │
│  │            Frontend Service (React + Vite)                  │     │
│  │                      Port 3000                              │     │
│  │  • User Interface  • Task Management  • Agent Dashboard    │     │
│  └────────────────────────────────────────────────────────────┘     │
└────────────────────────────┬─────────────────────────────────────────┘
                             │ REST API
                             │
┌────────────────────────────▼─────────────────────────────────────────┐
│                       Application Layer                               │
│  ┌────────────────────────────────────────────────────────────┐     │
│  │        Main Orchestrator Service (FastAPI)                  │     │
│  │                      Port 8000                              │     │
│  │                                                             │     │
│  │  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐ │     │
│  │  │  Agent       │  │   Task       │  │    Memory       │ │     │
│  │  │  Registry    │  │   Planner    │  │    Service      │ │     │
│  │  └──────────────┘  └──────────────┘  └─────────────────┘ │     │
│  │                                                             │     │
│  │  ┌──────────────────────────────────────────────────────┐ │     │
│  │  │         Agent Registration Service                    │ │     │
│  │  │  • Template Management  • Connection Testing         │ │     │
│  │  └──────────────────────────────────────────────────────┘ │     │
│  │                                                             │     │
│  │  ┌──────────────────────────────────────────────────────┐ │     │
│  │  │             Task Executor                             │ │     │
│  │  │  • Background Processing  • Multi-Step Coordination  │ │     │
│  │  └──────────────────────────────────────────────────────┘ │     │
│  └─────────────────────────────────────────────────────────────┘     │
└────────────┬────────────────────────┬──────────────────────────────┘
             │                        │
             │ A2A Protocol           │ REST API
             │                        │
┌────────────▼───────────┐  ┌────────▼──────────────────────────────┐
│   Agent Services        │  │     Agent Services                     │
│                         │  │                                        │
│  ┌──────────────────┐  │  │  ┌──────────────────────────────┐    │
│  │ A2A Server       │  │  │  │ API Agent Server              │    │
│  │ (LangGraph)      │  │  │  │ (Simple REST)                 │    │
│  │ Port: 8001       │  │  │  │ Port: 8002                    │    │
│  └──────────────────┘  │  │  └──────────────────────────────┘    │
│                         │  │                                        │
│  ┌──────────────────┐  │  │  ┌──────────────────────────────┐    │
│  │ CrewAI Agent     │  │  │  │ Databricks Agent              │    │
│  │ Port: 8003       │  │  │  │ Port: 8004                    │    │
│  └──────────────────┘  │  │  └──────────────────────────────┘    │
│                         │  │                                        │
│  ┌──────────────────┐  │  │  ┌──────────────────────────────┐    │
│  │ OpenAI Compatible│  │  │  │ Custom Agents                 │    │
│  │ Port: 8005       │  │  │  │ Ports: 8006+                  │    │
│  └──────────────────┘  │  │  └──────────────────────────────┘    │
└─────────────────────────┘  └────────────────────────────────────────┘
             │                        │
             └────────────┬───────────┘
                          │ LLM API Calls
                          │
             ┌────────────▼───────────┐
             │   External Services    │
             │  • OpenAI API          │
             │  • Groq API            │
             │  • Custom LLMs         │
             └────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│                           Data Layer                                  │
│  ┌────────────────────────────────────────────────────────────┐     │
│  │               SQLite/PostgreSQL Database                    │     │
│  │  • Agent Registry  • Tasks  • Sessions  • Templates        │     │
│  └────────────────────────────────────────────────────────────┘     │
└──────────────────────────────────────────────────────────────────────┘
```

## 🎯 Architecture Layers

### 1. Presentation Layer

**Frontend Service** (`frontend/`)
- **Technology**: React 18, Vite, Axios
- **Port**: 3000
- **Purpose**: User interface for task management and agent monitoring
- **Key Features**:
  - Task creation and monitoring
  - Agent registration with templates
  - Real-time status updates
  - Session history
  - Power User mode for advanced features

### 2. Application Layer

**Main Orchestrator Service** (`backend/main.py`)
- **Technology**: FastAPI, Python 3.9+
- **Port**: 8000
- **Purpose**: Central coordination and API gateway
- **Key Features**:
  - RESTful API endpoints
  - Background task processing
  - Agent lifecycle management
  - Session and context management
  - Template-based agent registration

### 3. Agent Services Layer

Multiple agent services that can be registered dynamically:
- **A2A Server** (Port 8001): LangGraph-based agents
- **API Agent** (Port 8002): Simple REST agents
- **Dummy Agents** (Ports 8003-8005): Testing and examples
- **Custom Agents** (Ports 8006+): User-defined agents

### 4. Data Layer

**Database** (`agent_orchestrator.db`)
- **Technology**: SQLite (dev), PostgreSQL (prod)
- **Purpose**: Persistent storage for all system data
- **Schema**: Agents, Tasks, Sessions, Messages, Templates

## 🧩 Core Modules

### 1. Agent Registry Module

**Location**: `backend/services/agent_registry.py`

**Purpose**: Central registry for managing all agents in the system.

**Key Functions**:
```python
class AgentRegistry:
    - register_agent()        # Register new agent
    - get_agent()             # Retrieve agent by ID
    - list_agents()           # List all agents
    - update_agent()          # Update agent config
    - delete_agent()          # Remove agent
    - get_agents_by_capability()  # Find agents by capability
    - check_agent_health()    # Health check
```

**Features**:
- Dynamic agent registration
- Capability-based discovery
- Health monitoring
- Status tracking (active, inactive, error)
- Metadata management

### 2. Agent Registration Service Module

**Location**: `backend/services/agent_registration_service.py`

**Purpose**: Handle agent registration with configuration templates and testing.

**Key Functions**:
```python
class AgentRegistrationService:
    - initialize_templates()          # Load built-in templates
    - list_templates()                # Get available templates
    - get_template()                  # Get specific template
    - test_agent_connection()         # Test agent endpoint
    - register_agent_with_template()  # Register using template
    - validate_agent_response()       # Validate response format
```

**Supported Templates**:
1. **CrewAI**: Multi-agent collaboration framework
2. **Databricks Foundation Models**: Databricks LLM endpoints
3. **OpenAI Compatible**: OpenAI API format
4. **Custom**: User-defined mappings

**Template Structure**:
```yaml
request_mapping:
  method: POST
  path: /endpoint
  headers: {...}
  body_mapping: {...}

response_mapping:
  status_path: $.status
  result_path: $.result
  error_path: $.error

auth_config:
  type: bearer_token
  env_var: API_KEY
```

### 3. Task Planner Module

**Location**: `backend/orchestrator/task_planner.py`

**Purpose**: Decompose tasks and create execution plans.

**Key Functions**:
```python
class TaskPlanner:
    - create_execution_plan()     # Create task plan
    - decompose_task()            # Break into steps
    - match_agents_to_steps()     # Agent assignment
    - optimize_execution_order()  # Optimize sequence
```

**Planning Process**:
1. Analyze task description
2. Identify required capabilities
3. Query agent registry
4. Decompose into steps
5. Assign agents to steps
6. Create execution plan
7. Return task with plan

### 4. Task Executor Module

**Location**: `backend/orchestrator/task_executor.py`

**Purpose**: Execute task plans and coordinate agents.

**Key Functions**:
```python
class TaskExecutor:
    - execute_task()              # Execute entire task
    - execute_step()              # Execute single step
    - route_to_agent()            # Route request to agent
    - handle_agent_response()     # Process agent response
    - aggregate_results()         # Combine step results
```

**Execution Flow**:
1. Load task plan
2. For each step:
   - Get agent from registry
   - Prepare request payload
   - Route based on agent type
   - Wait for response
   - Store step result
   - Update status
3. Aggregate all results
4. Update task completion

### 5. Memory Service Module

**Location**: `backend/services/memory_service.py`

**Purpose**: Manage conversation sessions and context.

**Key Functions**:
```python
class MemoryService:
    - create_session()            # Create new session
    - get_session()               # Retrieve session
    - add_message()               # Add message to session
    - get_conversation_history()  # Get message history
    - update_session_metadata()   # Update metadata
    - expire_old_sessions()       # Cleanup old sessions
```

**Session Management**:
- Session lifecycle management
- Conversation history
- Context windowing
- Metadata storage
- Automatic expiry (24 hours)

### 6. A2A Protocol Module

**Location**: `backend/agents/a2a_protocol.py`

**Purpose**: Agent-to-Agent communication protocol.

**Message Structure**:
```python
class A2AMessage:
    sender: str                   # Sender agent ID
    receiver: str                 # Receiver agent ID
    message_type: str             # request/response
    session_id: str               # Session identifier
    content: Dict[str, Any]       # Message payload
    metadata: Dict[str, Any]      # Additional metadata
```

**Protocol Features**:
- Structured messaging
- Session tracking
- Metadata support
- Type safety
- Error handling

### 7. LangGraph Agent Module

**Location**: `backend/agents/langgraph_agent.py`

**Purpose**: Complex agent workflows using LangGraph.

**Workflow Stages**:
```python
1. Analyze   → Understand task requirements
2. Plan      → Create execution strategy  
3. Execute   → Perform the task
4. Reflect   → Evaluate results
5. Finalize  → Prepare final output
```

**Features**:
- State management
- Multi-step reasoning
- Self-reflection
- Context preservation
- LLM integration (OpenAI, Groq)

### 8. API Agent Module

**Location**: `backend/agents/api_agent.py`

**Purpose**: Simple REST-based agent implementation.

**Features**:
- Direct HTTP communication
- Simple request/response
- Fast processing
- Stateless operations
- Easy integration

## 📦 Service Components

### Main Orchestrator Components

```
backend/
├── main.py                          # FastAPI app, API routes
├── database.py                      # Database connection
├── config.py                        # Configuration management
│
├── models/                          # Data Models
│   ├── agent.py                     # Agent model
│   ├── task.py                      # Task model
│   ├── memory.py                    # Session/Message models
│   └── agent_config_template.py     # Template model
│
├── services/                        # Business Logic
│   ├── agent_registry.py            # Agent CRUD operations
│   ├── agent_registration_service.py # Template-based registration
│   └── memory_service.py            # Session management
│
├── orchestrator/                    # Task Orchestration
│   ├── task_planner.py              # Task planning logic
│   └── task_executor.py             # Task execution
│
├── agents/                          # Agent Implementations
│   ├── a2a_protocol.py              # A2A protocol definitions
│   ├── langgraph_agent.py           # LangGraph agent
│   └── api_agent.py                 # Simple API agent
│
├── config/                          # Configuration Files
│   └── agent_templates.yaml         # Agent templates
│
└── dummy_agents/                    # Example Agents
    ├── crewai_agent_server.py       # CrewAI example
    ├── databricks_agent_server.py   # Databricks example
    └── openai_compatible_agent_server.py # OpenAI example
```

### API Endpoints

**Agent Management**:
```
POST   /api/agents/register                    # Register agent
POST   /api/agents/register-with-template      # Register with template
POST   /api/agents/test-connection             # Test agent connection
GET    /api/agents                             # List all agents
GET    /api/agents/{agent_id}                  # Get agent details
PUT    /api/agents/{agent_id}                  # Update agent
POST   /api/agents/{agent_id}/health           # Health check
GET    /api/agents/stats                       # Get statistics
```

**Template Management**:
```
GET    /api/agent-templates                    # List templates
GET    /api/agent-templates/{template_id}      # Get template details
```

**Task Management**:
```
POST   /api/tasks                              # Create task
GET    /api/tasks/{task_id}                    # Get task status
POST   /api/tasks/{task_id}/cancel             # Cancel task
```

**Session Management**:
```
POST   /api/sessions                           # Create session
POST   /api/sessions/{session_id}/messages     # Add message
GET    /api/sessions/{session_id}/messages     # Get messages
GET    /api/sessions/{session_id}              # Get session details
```

**A2A Communication**:
```
POST   /a2a/message                            # A2A message endpoint
```

**Health & Monitoring**:
```
GET    /health                                 # Service health
```

## 💾 Data Models

### Agent Model

```python
class Agent(Base):
    id: int                         # Primary key
    name: str                       # Unique agent name
    description: str                # Agent description
    agent_type: AgentType           # a2a_server, api, langgraph
    endpoint: str                   # Agent URL
    capabilities: List[str]         # Agent capabilities
    status: AgentStatus             # active, inactive, error
    config: Dict[str, Any]          # Configuration
    metadata: Dict[str, Any]        # Additional metadata
    created_at: datetime
    updated_at: datetime

class AgentType(Enum):
    A2A_SERVER = "a2a_server"
    API = "api"
    LANGGRAPH = "langgraph"
    CREWAI = "crewai"
    DATABRICKS = "databricks"
    CUSTOM = "custom"

class AgentStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
```

### Task Model

```python
class Task(Base):
    id: int                         # Primary key
    session_id: str                 # Session reference
    user_id: str                    # User identifier
    description: str                # Task description
    status: TaskStatus              # Task status
    plan: Dict[str, Any]            # Execution plan
    result: Dict[str, Any]          # Task result
    error: str                      # Error message
    created_at: datetime
    completed_at: datetime
    
class TaskStatus(Enum):
    PENDING = "pending"
    PLANNING = "planning"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
```

### Session & Memory Models

```python
class ConversationContext(Base):
    id: int                         # Primary key
    session_id: str                 # Unique session ID
    user_id: str                    # User identifier
    metadata: Dict[str, Any]        # Session metadata
    created_at: datetime
    last_activity: datetime

class Message(Base):
    id: int                         # Primary key
    context_id: int                 # Foreign key to Context
    agent_id: int                   # Foreign key to Agent
    role: str                       # user, assistant, system
    content: str                    # Message content
    metadata: Dict[str, Any]        # Message metadata
    created_at: datetime
```

### Template Model

```python
class AgentConfigTemplate(Base):
    id: int                         # Primary key
    name: str                       # Unique template name
    display_name: str               # Display name
    description: str                # Template description
    framework: str                  # Framework type
    request_mapping: Dict           # Request structure
    response_mapping: Dict          # Response parsing
    auth_config: Dict               # Authentication config
    example_request: Dict           # Example request
    example_response: Dict          # Example response
    is_builtin: bool                # Built-in template
    is_active: bool                 # Active status
    created_at: datetime
    updated_at: datetime
```

## 🤝 Agent System

### Agent Types

1. **A2A Server Agents**
   - Complex LangGraph workflows
   - Multi-step reasoning
   - State management
   - Use A2A protocol

2. **API Agents**
   - Simple REST API
   - Direct processing
   - Stateless
   - Fast responses

3. **Template-Based Agents**
   - CrewAI agents
   - Databricks models
   - OpenAI compatible
   - Custom formats

### Agent Lifecycle

```
┌─────────────┐
│ Registration│
│   Phase     │
└──────┬──────┘
       │
       ├─→ Validate endpoint
       ├─→ Test connection
       ├─→ Verify response format
       ├─→ Store in registry
       │
       ▼
┌─────────────┐
│   Active    │
│   Phase     │
└──────┬──────┘
       │
       ├─→ Receive tasks
       ├─→ Process requests
       ├─→ Return results
       ├─→ Health monitoring
       │
       ▼
┌─────────────┐
│  Inactive/  │
│   Error     │
└──────┬──────┘
       │
       ├─→ Automatic retry
       ├─→ Alert admin
       └─→ Re-registration
```

### Agent Discovery

Agents are discovered based on:
1. **Capabilities**: Text list of skills
2. **Type**: Framework/protocol type
3. **Status**: Only active agents
4. **Health**: Recent health check passed

### Agent Communication

**A2A Protocol Flow**:
```
Orchestrator → Agent:
{
  "sender": "MainOrchestrator",
  "receiver": "ResearchAgent",
  "message_type": "request",
  "session_id": "sess_123",
  "content": {
    "description": "Task description",
    "context": {...}
  }
}

Agent → Orchestrator:
{
  "sender": "ResearchAgent",
  "receiver": "MainOrchestrator",
  "message_type": "response",
  "session_id": "sess_123",
  "content": {
    "status": "success",
    "response": "Result...",
    "data": {...}
  }
}
```

**API Protocol Flow**:
```
POST /process
{
  "task_type": "analysis",
  "data": {...},
  "instructions": "...",
  "context": {...}
}

Response:
{
  "status": "success",
  "result": {...},
  "processing_time_ms": 150
}
```

## 🗄️ Database Schema

```sql
-- Agents Table
CREATE TABLE agents (
    id INTEGER PRIMARY KEY,
    name VARCHAR UNIQUE NOT NULL,
    description TEXT,
    agent_type VARCHAR NOT NULL,
    endpoint VARCHAR NOT NULL,
    capabilities JSON,
    status VARCHAR DEFAULT 'active',
    config JSON,
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tasks Table
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY,
    session_id VARCHAR,
    user_id VARCHAR,
    description TEXT,
    status VARCHAR DEFAULT 'pending',
    plan JSON,
    result JSON,
    error TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Conversation Contexts Table
CREATE TABLE conversation_contexts (
    id INTEGER PRIMARY KEY,
    session_id VARCHAR UNIQUE NOT NULL,
    user_id VARCHAR,
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Messages Table
CREATE TABLE messages (
    id INTEGER PRIMARY KEY,
    context_id INTEGER REFERENCES conversation_contexts(id),
    agent_id INTEGER REFERENCES agents(id),
    role VARCHAR NOT NULL,
    content TEXT NOT NULL,
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Agent Config Templates Table
CREATE TABLE agent_config_templates (
    id INTEGER PRIMARY KEY,
    name VARCHAR UNIQUE NOT NULL,
    display_name VARCHAR,
    description TEXT,
    framework VARCHAR,
    request_mapping JSON,
    response_mapping JSON,
    auth_config JSON,
    example_request JSON,
    example_response JSON,
    is_builtin BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🎨 Design Patterns

### 1. Registry Pattern
- **Agent Registry**: Central registration and discovery
- **Template Registry**: Reusable configuration templates

### 2. Strategy Pattern
- **Agent Types**: Different communication strategies
- **Task Execution**: Multiple execution strategies

### 3. Observer Pattern
- **Task Status**: Background task monitoring
- **Health Checks**: Agent health monitoring

### 4. Factory Pattern
- **Agent Creation**: Template-based agent instantiation
- **Message Creation**: Protocol-specific message factories

### 5. Adapter Pattern
- **Agent Adapters**: Adapt different agent APIs
- **Protocol Adapters**: A2A, REST, custom protocols

### 6. Command Pattern
- **Task Steps**: Encapsulated task operations
- **Agent Operations**: Discrete agent commands

## 🚀 Deployment Architecture

### Development Environment

```
Local Machine:
├── Frontend (Port 3000)     → Vite Dev Server
├── Main Orchestrator (8000) → Python/FastAPI
├── A2A Server (8001)        → Python/FastAPI
├── API Agent (8002)         → Python/FastAPI
├── Dummy Agents (8003-8005) → Python/FastAPI
└── SQLite Database          → Local file
```

### Production Environment

```
Cloud Infrastructure:
├── Load Balancer
│   └── SSL Termination
│
├── Frontend Tier
│   ├── Nginx/Static Hosting
│   └── CDN Distribution
│
├── Application Tier
│   ├── Main Orchestrator (Scaled)
│   ├── A2A Servers (Scaled)
│   └── API Agents (Scaled)
│
├── Data Tier
│   ├── PostgreSQL (Primary)
│   ├── PostgreSQL (Replica)
│   └── Redis (Caching)
│
└── Monitoring
    ├── Prometheus
    ├── Grafana
    └── ELK Stack
```

### Docker Deployment

```yaml
services:
  frontend:
    build: ./frontend
    ports: ["3000:3000"]
  
  orchestrator:
    build: ./backend
    ports: ["8000:8000"]
    environment:
      - DATABASE_URL=postgresql://...
  
  a2a_server:
    build: ./backend
    command: python a2a_server.py
    ports: ["8001:8001"]
  
  api_agent:
    build: ./backend
    command: python api_agent_server.py
    ports: ["8002:8002"]
  
  database:
    image: postgres:15
    volumes: ["pgdata:/var/lib/postgresql/data"]
```

## 📊 System Metrics

### Performance Targets

- **Task Creation**: < 100ms
- **Agent Registration**: < 500ms
- **Simple Task Execution**: < 2s
- **Complex Task Execution**: < 30s
- **API Response Time**: < 200ms (p95)

### Scalability

- **Concurrent Tasks**: 100+
- **Registered Agents**: 1000+
- **Sessions**: 10,000+
- **Messages/Second**: 1000+

### Reliability

- **System Uptime**: 99.9%
- **Agent Health Check**: Every 60s
- **Automatic Retry**: 3 attempts
- **Session Expiry**: 24 hours

## 📚 Additional Documentation

- [README](README.md) - Project overview and quick start
- [SERVICE_FLOW](SERVICE_FLOW.md) - Detailed service interactions
- [API_GUIDE](API_GUIDE.md) - Complete API reference
- [AGENT_REGISTRATION_IMPLEMENTATION](AGENT_REGISTRATION_IMPLEMENTATION.md) - Agent registration details
- [YAML_CONFIGURATION_GUIDE](YAML_CONFIGURATION_GUIDE.md) - Template configuration

## 🔄 Version History

- **v1.0.0** (2025-11-05) - Initial system architecture documentation
  - Complete module documentation
  - Agent registry system
  - Template-based registration
  - Multi-protocol support

---

**Last Updated**: November 5, 2025  
**Maintained By**: Sharad Narang  
**Repository**: https://github.com/SharadNarang/Multi-Agent-Orchestror

