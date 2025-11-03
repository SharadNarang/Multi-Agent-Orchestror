"""
Dummy Databricks Foundation Model Agent Server
Simulates Databricks Foundation Model API responses
"""
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import uvicorn
from datetime import datetime
import uuid

app = FastAPI(
    title="Databricks Foundation Model Server (Dummy)",
    description="Simulates Databricks Foundation Model API",
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

class Message(BaseModel):
    role: str
    content: str

class DatabricksRequest(BaseModel):
    messages: List[Message]
    max_tokens: Optional[int] = 1000
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 0.95
    n: Optional[int] = 1

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "agent_type": "databricks_foundation",
        "service": "databricks-agent-dummy",
        "model": "llama-2-70b-chat"
    }

@app.get("/api/2.0/serving-endpoints")
async def list_endpoints():
    """List available serving endpoints"""
    return {
        "endpoints": [
            {
                "name": "llama-2-70b-chat",
                "creator": "system",
                "creation_timestamp": 1699564800000,
                "last_updated_timestamp": 1699564800000,
                "state": {
                    "ready": "READY",
                    "config_update": "NOT_UPDATING"
                },
                "config": {
                    "served_models": [
                        {
                            "name": "llama-2-70b-chat",
                            "model_name": "llama-2-70b-chat",
                            "model_version": "1",
                            "workload_size": "Small",
                            "scale_to_zero_enabled": False
                        }
                    ]
                },
                "tags": [
                    {"key": "framework", "value": "databricks"},
                    {"key": "model_type", "value": "foundation"}
                ]
            }
        ]
    }

@app.post("/serving-endpoints/llama-2-70b-chat/invocations")
async def invoke_model(
    request: DatabricksRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Databricks Foundation Model invocation endpoint
    Simulates llama-2-70b-chat responses
    """
    
    # Check for authorization (optional in dummy)
    if authorization and not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    try:
        # Extract the last user message
        user_messages = [msg for msg in request.messages if msg.role == "user"]
        if not user_messages:
            raise HTTPException(status_code=400, detail="No user message found")
        
        user_query = user_messages[-1].content
        
        # Simulate model response
        response_text = f"""Based on your query about "{user_query}", here's a comprehensive analysis:

**Key Points:**
1. The topic shows significant relevance in current trends
2. Multiple factors contribute to the observed patterns
3. Data-driven insights suggest positive outcomes
4. Strategic considerations should include risk assessment

**Recommendations:**
- Continue monitoring developments
- Implement best practices
- Leverage available resources
- Maintain adaptive strategies

**Conclusion:**
The analysis indicates favorable conditions with manageable considerations for moving forward.
"""
        
        # Databricks Foundation Model response format
        return {
            "id": f"chatcmpl-{uuid.uuid4().hex[:8]}",
            "object": "chat.completion",
            "created": int(datetime.utcnow().timestamp()),
            "model": "llama-2-70b-chat",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": response_text
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": len(user_query.split()),
                "completion_tokens": len(response_text.split()),
                "total_tokens": len(user_query.split()) + len(response_text.split())
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process")
async def process_generic(request: Dict[str, Any]):
    """
    Generic endpoint for compatibility with orchestrator
    Maps generic requests to Databricks format
    """
    
    # Extract description/query
    query = request.get("description") or request.get("query") or request.get("input", "Hello")
    
    # Call the invocation endpoint
    databricks_request = DatabricksRequest(
        messages=[Message(role="user", content=query)],
        max_tokens=request.get("max_tokens", 1000),
        temperature=request.get("temperature", 0.7)
    )
    
    result = await invoke_model(databricks_request)
    
    # Extract the response text
    response_text = result["choices"][0]["message"]["content"]
    
    return {
        "status": "success",
        "agent": "Databricks_Foundation_Model",
        "result": response_text,
        "metadata": {
            "model": result["model"],
            "usage": result["usage"]
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "databricks_agent_server:app",
        host="0.0.0.0",
        port=8004,
        reload=True
    )

