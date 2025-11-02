"""
API Agent Server
Hosts the simple API-based agent
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uvicorn

from agents.api_agent import APIAgent
from config import get_settings

settings = get_settings()

app = FastAPI(
    title="API Agent Server",
    description="Simple API-based agent for data processing",
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

# Initialize the API agent
api_agent = APIAgent(agent_name="DataAnalyzer")

class ProcessRequest(BaseModel):
    task_type: str
    data: Any
    instructions: Optional[str] = ""
    target_format: Optional[str] = None

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "agent": api_agent.agent_name,
        "service": "api-agent"
    }

@app.get("/capabilities")
async def get_capabilities():
    """Get agent capabilities"""
    return api_agent.get_capabilities()

@app.post("/process")
async def process_request(request: ProcessRequest):
    """Process a request"""
    
    try:
        result = await api_agent.process_request(request.dict())
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "api_agent_server:app",
        host="0.0.0.0",
        port=8002,
        reload=True
    )

