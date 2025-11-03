"""
Dummy CrewAI Agent Server
Simulates a CrewAI agent deployed on Databricks
Returns CrewAI-style responses
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uvicorn
from datetime import datetime

app = FastAPI(
    title="CrewAI Agent Server (Dummy)",
    description="Simulates a CrewAI agent with multi-agent workflow",
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

class CrewAIRequest(BaseModel):
    inputs: Dict[str, Any]
    config: Optional[Dict[str, Any]] = None

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "agent_type": "crewai",
        "service": "crewai-agent-dummy",
        "agents": ["researcher", "analyst", "writer"]
    }

@app.get("/capabilities")
async def get_capabilities():
    """Get agent capabilities"""
    return {
        "agent_name": "CrewAI_Research_Team",
        "framework": "CrewAI",
        "capabilities": [
            "research",
            "analysis",
            "writing",
            "multi_agent_collaboration"
        ],
        "agents": [
            {
                "role": "Researcher",
                "goal": "Research topics thoroughly",
                "backstory": "Expert at finding and synthesizing information"
            },
            {
                "role": "Analyst",
                "goal": "Analyze data and provide insights",
                "backstory": "Data analysis expert with strategic thinking"
            },
            {
                "role": "Writer",
                "goal": "Create compelling content",
                "backstory": "Professional content creator"
            }
        ],
        "status": "active"
    }

@app.post("/kickoff")
async def kickoff_crew(request: CrewAIRequest):
    """
    CrewAI-style endpoint for starting a crew workflow
    Simulates multi-agent collaboration
    """
    
    try:
        inputs = request.inputs
        topic = inputs.get("topic", inputs.get("query", "general query"))
        
        # Simulate CrewAI workflow
        workflow_results = []
        
        # Step 1: Researcher
        workflow_results.append({
            "agent": "Researcher",
            "task": "Research",
            "output": f"Research findings on '{topic}':\n\n" +
                     "• Found 15+ relevant sources\n" +
                     "• Key trends identified\n" +
                     "• Latest developments documented\n" +
                     "• Expert opinions collected"
        })
        
        # Step 2: Analyst
        workflow_results.append({
            "agent": "Analyst",
            "task": "Analysis",
            "output": f"Analysis of '{topic}':\n\n" +
                     "• Data shows strong growth patterns\n" +
                     "• Market indicators are positive\n" +
                     "• Risk factors identified and assessed\n" +
                     "• Strategic recommendations prepared"
        })
        
        # Step 3: Writer
        workflow_results.append({
            "agent": "Writer",
            "task": "Writing",
            "output": f"Final Report on '{topic}':\n\n" +
                     "Based on comprehensive research and analysis, " +
                     f"{topic} demonstrates significant potential. " +
                     "The research team identified key growth drivers, " +
                     "while analysts confirmed positive market indicators. " +
                     "Strategic recommendations include continued monitoring " +
                     "and proactive engagement with emerging opportunities."
        })
        
        # CrewAI-style response format
        return {
            "result": workflow_results[-1]["output"],  # Final output
            "workflow": workflow_results,
            "metadata": {
                "crew_name": "Research_Analysis_Team",
                "agents_used": ["Researcher", "Analyst", "Writer"],
                "execution_time": "3.2s",
                "timestamp": datetime.utcnow().isoformat()
            },
            "success": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process")
async def process_generic(request: Dict[str, Any]):
    """
    Generic endpoint for compatibility with orchestrator
    Maps generic requests to CrewAI format
    """
    
    # Extract description/query
    topic = request.get("description") or request.get("query") or request.get("topic", "general query")
    
    # Call the kickoff endpoint
    crewai_request = CrewAIRequest(
        inputs={"topic": topic}
    )
    
    result = await kickoff_crew(crewai_request)
    
    return result

if __name__ == "__main__":
    uvicorn.run(
        "crewai_agent_server:app",
        host="0.0.0.0",
        port=8003,
        reload=True
    )

