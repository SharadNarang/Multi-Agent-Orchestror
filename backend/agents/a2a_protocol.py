"""
A2A (Agent-to-Agent) Protocol Implementation
Handles communication between agents using A2A protocol
"""
import httpx
import asyncio
from typing import Dict, Any, Optional
from pydantic import BaseModel
import json

class A2AMessage(BaseModel):
    """A2A Protocol Message Format"""
    sender: str
    receiver: str
    message_type: str  # request, response, notification
    content: Dict[str, Any]
    session_id: str
    metadata: Optional[Dict[str, Any]] = None

class A2AProtocolHandler:
    """Handles A2A protocol communication"""
    
    def __init__(self, agent_id: str, endpoint: str):
        self.agent_id = agent_id
        self.endpoint = endpoint
        self.client = httpx.AsyncClient(timeout=60.0)
    
    async def send_message(self, 
                          receiver: str, 
                          content: Dict[str, Any],
                          session_id: str,
                          message_type: str = "request") -> Dict[str, Any]:
        """Send a message to another agent via A2A protocol"""
        
        message = A2AMessage(
            sender=self.agent_id,
            receiver=receiver,
            message_type=message_type,
            content=content,
            session_id=session_id
        )
        
        try:
            response = await self.client.post(
                f"{self.endpoint}/a2a/message",
                json=message.dict(),
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            return {
                "error": str(e),
                "status": "failed"
            }
    
    async def receive_message(self, message: A2AMessage) -> Dict[str, Any]:
        """Process an incoming A2A message"""
        # This will be implemented by each agent
        return {
            "status": "received",
            "session_id": message.session_id
        }
    
    async def broadcast_message(self, 
                               receivers: list, 
                               content: Dict[str, Any],
                               session_id: str) -> Dict[str, list]:
        """Broadcast a message to multiple agents"""
        
        tasks = [
            self.send_message(receiver, content, session_id)
            for receiver in receivers
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return {
            "sent_to": receivers,
            "results": results
        }
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

