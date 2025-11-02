"""
Main FastAPI Application
Multi-Agent Orchestrator with A2A Protocol Support
"""
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import uvicorn

from database import get_db, engine, Base
from models.agent import Agent, AgentType, AgentStatus
from models.task import Task, TaskStep, TaskStatus
from models.memory import ConversationContext, Message
from services.agent_registry import AgentRegistry
from services.memory_service import MemoryService
from orchestrator.task_planner import TaskPlanner
from orchestrator.task_executor import TaskExecutor
from agents.a2a_protocol import A2AMessage
from config import get_settings

# Create database tables
Base.metadata.create_all(bind=engine)

settings = get_settings()

app = FastAPI(
    title="Multi-Agent Orchestrator",
    description="Orchestrate multiple AI agents with A2A protocol support",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class AgentRegistration(BaseModel):
    name: str
    description: str
    agent_type: AgentType
    endpoint: str
    capabilities: List[str]
    config: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

class TaskRequest(BaseModel):
    description: str
    session_id: Optional[str] = None
    user_id: str
    metadata: Optional[Dict[str, Any]] = None

class MessageRequest(BaseModel):
    session_id: str
    content: str
    role: str = "user"
    metadata: Optional[Dict[str, Any]] = None

class AgentUpdateRequest(BaseModel):
    description: Optional[str] = None
    endpoint: Optional[str] = None
    capabilities: Optional[List[str]] = None
    status: Optional[AgentStatus] = None
    config: Optional[Dict[str, Any]] = None

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "multi-agent-orchestrator"}

# Agent Registry Endpoints
@app.post("/api/agents/register", response_model=Dict[str, Any])
async def register_agent(agent: AgentRegistration, db: Session = Depends(get_db)):
    """Register a new agent"""
    try:
        registry = AgentRegistry(db)
        new_agent = registry.register_agent(
            name=agent.name,
            description=agent.description,
            agent_type=agent.agent_type,
            endpoint=agent.endpoint,
            capabilities=agent.capabilities,
            config=agent.config,
            metadata=agent.metadata
        )
        return {
            "id": new_agent.id,
            "name": new_agent.name,
            "status": new_agent.status,
            "agent_type": new_agent.agent_type
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/agents", response_model=List[Dict[str, Any]])
async def list_agents(
    agent_type: Optional[AgentType] = None,
    status: Optional[AgentStatus] = None,
    db: Session = Depends(get_db)
):
    """List all registered agents"""
    registry = AgentRegistry(db)
    agents = registry.list_agents(agent_type=agent_type, status=status)
    
    return [
        {
            "id": agent.id,
            "name": agent.name,
            "description": agent.description,
            "agent_type": agent.agent_type,
            "endpoint": agent.endpoint,
            "capabilities": agent.capabilities,
            "status": agent.status,
            "created_at": agent.created_at.isoformat()
        }
        for agent in agents
    ]

@app.get("/api/agents/{agent_id}", response_model=Dict[str, Any])
async def get_agent(agent_id: int, db: Session = Depends(get_db)):
    """Get agent details"""
    registry = AgentRegistry(db)
    agent = registry.get_agent(agent_id)
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return {
        "id": agent.id,
        "name": agent.name,
        "description": agent.description,
        "agent_type": agent.agent_type,
        "endpoint": agent.endpoint,
        "capabilities": agent.capabilities,
        "status": agent.status,
        "config": agent.config,
        "metadata": agent.metadata,
        "created_at": agent.created_at.isoformat()
    }

@app.put("/api/agents/{agent_id}", response_model=Dict[str, Any])
async def update_agent(
    agent_id: int,
    updates: AgentUpdateRequest,
    db: Session = Depends(get_db)
):
    """Update agent information"""
    registry = AgentRegistry(db)
    
    update_dict = {k: v for k, v in updates.dict().items() if v is not None}
    
    try:
        updated_agent = registry.update_agent(agent_id, update_dict)
        return {
            "id": updated_agent.id,
            "name": updated_agent.name,
            "status": updated_agent.status
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/api/agents/{agent_id}/health", response_model=Dict[str, Any])
async def check_agent_health(agent_id: int, db: Session = Depends(get_db)):
    """Check agent health"""
    registry = AgentRegistry(db)
    result = await registry.check_agent_health(agent_id)
    
    if "error" in result and result.get("status") != "healthy":
        raise HTTPException(status_code=503, detail=result)
    
    return result

@app.get("/api/agents/stats", response_model=Dict[str, Any])
async def get_agent_stats(db: Session = Depends(get_db)):
    """Get agent statistics"""
    registry = AgentRegistry(db)
    return registry.get_agent_stats()

# Task Management Endpoints
@app.post("/api/tasks", response_model=Dict[str, Any])
async def create_task(
    task_request: TaskRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Create and plan a new task"""
    try:
        # Create or get session
        memory_service = MemoryService(db)
        session_id = task_request.session_id
        
        if not session_id:
            context = memory_service.create_session(
                user_id=task_request.user_id,
                metadata=task_request.metadata
            )
            session_id = context.session_id
        
        # Create task plan
        planner = TaskPlanner(db)
        task = await planner.create_execution_plan(
            task_description=task_request.description,
            session_id=session_id
        )
        
        # Execute task in background
        background_tasks.add_task(execute_task_background, task.id, db)
        
        return {
            "task_id": task.id,
            "session_id": session_id,
            "status": task.status,
            "plan": task.plan,
            "created_at": task.created_at.isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tasks/{task_id}", response_model=Dict[str, Any])
async def get_task(task_id: int, db: Session = Depends(get_db)):
    """Get task details and status"""
    task = db.query(Task).filter(Task.id == task_id).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Get task steps
    steps = db.query(TaskStep).filter(TaskStep.task_id == task_id).all()
    
    return {
        "id": task.id,
        "session_id": task.session_id,
        "description": task.description,
        "status": task.status,
        "plan": task.plan,
        "result": task.result,
        "steps": [
            {
                "step_number": step.step_number,
                "description": step.description,
                "status": step.status,
                "agent_id": step.agent_id,
                "output_data": step.output_data
            }
            for step in steps
        ],
        "created_at": task.created_at.isoformat(),
        "completed_at": task.completed_at.isoformat() if task.completed_at else None
    }

@app.post("/api/tasks/{task_id}/cancel", response_model=Dict[str, Any])
async def cancel_task(task_id: int, db: Session = Depends(get_db)):
    """Cancel a running task"""
    executor = TaskExecutor(db)
    result = await executor.cancel_task(task_id)
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result

# Memory/Context Management Endpoints
@app.post("/api/sessions", response_model=Dict[str, Any])
async def create_session(
    user_id: str,
    metadata: Optional[Dict[str, Any]] = None,
    db: Session = Depends(get_db)
):
    """Create a new conversation session"""
    memory_service = MemoryService(db)
    context = memory_service.create_session(user_id, metadata)
    
    return {
        "session_id": context.session_id,
        "user_id": context.user_id,
        "created_at": context.created_at.isoformat()
    }

@app.post("/api/sessions/{session_id}/messages", response_model=Dict[str, Any])
async def add_message(
    session_id: str,
    message: MessageRequest,
    db: Session = Depends(get_db)
):
    """Add a message to a session"""
    try:
        memory_service = MemoryService(db)
        new_message = memory_service.add_message(
            session_id=session_id,
            role=message.role,
            content=message.content,
            metadata=message.metadata
        )
        
        return {
            "id": new_message.id,
            "role": new_message.role,
            "content": new_message.content,
            "timestamp": new_message.timestamp.isoformat()
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/api/sessions/{session_id}/messages", response_model=List[Dict[str, Any]])
async def get_messages(
    session_id: str,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get conversation history"""
    memory_service = MemoryService(db)
    messages = memory_service.get_conversation_history(session_id, limit)
    
    return [
        {
            "id": msg.id,
            "role": msg.role,
            "content": msg.content,
            "agent_id": msg.agent_id,
            "timestamp": msg.timestamp.isoformat(),
            "metadata": msg.metadata
        }
        for msg in reversed(messages)
    ]

@app.get("/api/sessions/{session_id}", response_model=Dict[str, Any])
async def get_session_summary(session_id: str, db: Session = Depends(get_db)):
    """Get session summary"""
    memory_service = MemoryService(db)
    summary = memory_service.get_context_summary(session_id)
    
    if not summary:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return summary

# A2A Protocol Endpoints
@app.post("/a2a/message", response_model=Dict[str, Any])
async def receive_a2a_message(message: A2AMessage, db: Session = Depends(get_db)):
    """Receive A2A protocol message"""
    
    # Find the receiver agent
    registry = AgentRegistry(db)
    agent = registry.get_agent_by_name(message.receiver)
    
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{message.receiver}' not found")
    
    # Process the message
    # This is a simplified implementation
    # In production, you would route this to the actual agent
    
    return {
        "status": "received",
        "message_id": message.session_id,
        "receiver": message.receiver,
        "processed_at": "now"
    }

# Helper functions
async def execute_task_background(task_id: int, db: Session):
    """Execute task in background"""
    executor = TaskExecutor(db)
    try:
        await executor.execute_task(task_id)
    finally:
        await executor.cleanup()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

