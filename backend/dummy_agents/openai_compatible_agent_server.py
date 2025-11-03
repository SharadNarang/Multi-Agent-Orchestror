"""
Dummy OpenAI-Compatible Agent Server
Simulates OpenAI API responses
Compatible with any client expecting OpenAI format
"""
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import uvicorn
from datetime import datetime
import uuid

app = FastAPI(
    title="OpenAI-Compatible Agent Server (Dummy)",
    description="Simulates OpenAI API responses",
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

class CompletionRequest(BaseModel):
    model: Optional[str] = "gpt-3.5-turbo"
    messages: List[Message]
    max_tokens: Optional[int] = 1000
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 1.0
    n: Optional[int] = 1
    stream: Optional[bool] = False
    stop: Optional[List[str]] = None
    presence_penalty: Optional[float] = 0.0
    frequency_penalty: Optional[float] = 0.0

class LegacyCompletionRequest(BaseModel):
    model: Optional[str] = "text-davinci-003"
    prompt: str
    max_tokens: Optional[int] = 1000
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 1.0
    n: Optional[int] = 1
    stream: Optional[bool] = False
    stop: Optional[List[str]] = None

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "agent_type": "openai_compatible",
        "service": "openai-agent-dummy",
        "models": ["gpt-3.5-turbo", "gpt-4", "text-davinci-003"]
    }

@app.get("/v1/models")
async def list_models():
    """List available models (OpenAI format)"""
    return {
        "object": "list",
        "data": [
            {
                "id": "gpt-3.5-turbo",
                "object": "model",
                "created": 1677610602,
                "owned_by": "openai",
                "permission": [],
                "root": "gpt-3.5-turbo",
                "parent": None
            },
            {
                "id": "gpt-4",
                "object": "model",
                "created": 1687882411,
                "owned_by": "openai",
                "permission": [],
                "root": "gpt-4",
                "parent": None
            },
            {
                "id": "text-davinci-003",
                "object": "model",
                "created": 1669599635,
                "owned_by": "openai-internal",
                "permission": [],
                "root": "text-davinci-003",
                "parent": None
            }
        ]
    }

@app.post("/v1/chat/completions")
async def create_chat_completion(
    request: CompletionRequest,
    authorization: Optional[str] = Header(None)
):
    """
    OpenAI Chat Completions endpoint
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
        
        # Simulate GPT response
        response_text = f"""I understand you're asking about: "{user_query}"

Here's a comprehensive response:

**Analysis:**
This is an interesting query that touches on several important aspects. Let me break it down:

1. **Primary Considerations**: The main factors to consider include context, scope, and objectives.

2. **Key Insights**: Based on current understanding, the most relevant points are:
   - Strategic alignment with goals
   - Resource availability and constraints
   - Timeline and milestones
   - Risk mitigation strategies

3. **Recommendations**: 
   - Prioritize clear communication
   - Establish measurable metrics
   - Implement iterative improvements
   - Monitor progress regularly

**Summary:**
The approach should be methodical, data-driven, and adaptable to changing conditions. Success depends on careful planning and execution.

Is there a specific aspect you'd like me to elaborate on?
"""
        
        # OpenAI response format
        return {
            "id": f"chatcmpl-{uuid.uuid4().hex[:29]}",
            "object": "chat.completion",
            "created": int(datetime.utcnow().timestamp()),
            "model": request.model,
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
                "prompt_tokens": sum(len(msg.content.split()) for msg in request.messages),
                "completion_tokens": len(response_text.split()),
                "total_tokens": sum(len(msg.content.split()) for msg in request.messages) + len(response_text.split())
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/completions")
async def create_completion(
    request: LegacyCompletionRequest,
    authorization: Optional[str] = Header(None)
):
    """
    OpenAI legacy Completions endpoint (text-davinci-003 style)
    """
    
    try:
        prompt = request.prompt
        
        # Simulate completion
        completion_text = f"""Based on the prompt: "{prompt}"

Here's the generated completion:

The analysis reveals several key factors worth considering. First, the context suggests a need for strategic thinking and careful planning. Second, the available data points to opportunities for optimization and improvement. Third, implementation should follow best practices and industry standards.

In conclusion, success requires a balanced approach that considers both immediate needs and long-term objectives."""
        
        # OpenAI legacy response format
        return {
            "id": f"cmpl-{uuid.uuid4().hex[:29]}",
            "object": "text_completion",
            "created": int(datetime.utcnow().timestamp()),
            "model": request.model,
            "choices": [
                {
                    "text": completion_text,
                    "index": 0,
                    "logprobs": None,
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": len(prompt.split()),
                "completion_tokens": len(completion_text.split()),
                "total_tokens": len(prompt.split()) + len(completion_text.split())
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process")
async def process_generic(request: Dict[str, Any]):
    """
    Generic endpoint for compatibility with orchestrator
    Maps generic requests to OpenAI format
    """
    
    # Extract description/query
    query = request.get("description") or request.get("query") or request.get("prompt", "Hello")
    
    # Call the chat completion endpoint
    openai_request = CompletionRequest(
        model="gpt-3.5-turbo",
        messages=[Message(role="user", content=query)],
        max_tokens=request.get("max_tokens", 1000),
        temperature=request.get("temperature", 0.7)
    )
    
    result = await create_chat_completion(openai_request)
    
    # Extract the response text
    response_text = result["choices"][0]["message"]["content"]
    
    return {
        "status": "success",
        "agent": "OpenAI_Compatible_Agent",
        "result": response_text,
        "metadata": {
            "model": result["model"],
            "usage": result["usage"]
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "openai_compatible_agent_server:app",
        host="0.0.0.0",
        port=8005,
        reload=True
    )

