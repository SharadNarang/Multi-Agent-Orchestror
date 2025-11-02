"""
A2A Server Application
Hosts the LangGraph-based agent over A2A protocol
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uvicorn
import asyncio

from agents.langgraph_agent import LangGraphA2AAgent
from agents.a2a_protocol import A2AMessage
from config import get_settings

settings = get_settings()

app = FastAPI(
    title="A2A Agent Server",
    description="LangGraph-based agent accessible via A2A protocol",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the LangGraph agent
langgraph_agent = LangGraphA2AAgent(agent_name="ResearchAgent")

class ProcessRequest(BaseModel):
    description: str
    context: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = "default"

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "agent": langgraph_agent.agent_name,
        "service": "a2a-server"
    }

@app.get("/capabilities")
async def get_capabilities():
    """Get agent capabilities"""
    return {
        "agent_name": langgraph_agent.agent_name,
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

@app.post("/a2a/message")
async def receive_a2a_message(message: A2AMessage):
    """Receive and process A2A protocol message"""
    
    try:
        # Extract the task from message content
        task_description = message.content.get("description", "")
        context = message.content.get("context", {})
        
        if not task_description:
            raise HTTPException(status_code=400, detail="No task description provided")
        
        # Process through LangGraph agent
        result = await langgraph_agent.process_message(
            message=task_description,
            context=context
        )
        
        # Return A2A formatted response
        return {
            "sender": langgraph_agent.agent_name,
            "receiver": message.sender,
            "message_type": "response",
            "session_id": message.session_id,
            "content": {
                "status": "success",
                "response": result["response"],
                "agent": result["agent_name"]
            },
            "metadata": {
                "processed_with": "LangGraph",
                "workflow_completed": True
            }
        }
        
    except Exception as e:
        return {
            "sender": langgraph_agent.agent_name,
            "receiver": message.sender,
            "message_type": "response",
            "session_id": message.session_id,
            "content": {
                "status": "error",
                "error": str(e)
            }
        }

@app.post("/process")
async def process_direct(request: ProcessRequest):
    """Direct processing endpoint (non-A2A)"""
    
    try:
        result = await langgraph_agent.process_message(
            message=request.description,
            context=request.context
        )
        
        return {
            "status": "success",
            "session_id": request.session_id,
            "result": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "a2a_server:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )

