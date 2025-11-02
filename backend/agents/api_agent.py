"""
Simple API-based Agent
This agent is accessible through REST API and performs specific tasks
"""
import httpx
from typing import Dict, Any
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from config import get_settings

settings = get_settings()

class APIAgent:
    """
    A simple agent accessible through REST API
    Specialized for data analysis and processing tasks
    """
    
    def __init__(self, agent_name: str = "DataAnalyzer"):
        self.agent_name = agent_name
        self.llm = ChatGroq(
            temperature=0.3,
            model="llama-3.3-70b-versatile",
            groq_api_key=settings.groq_api_key
        )
        self.capabilities = [
            "data_analysis",
            "text_processing",
            "summarization",
            "format_conversion"
        ]
    
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process an incoming API request"""
        
        task_type = request.get("task_type")
        data = request.get("data")
        instructions = request.get("instructions", "")
        
        if task_type == "data_analysis":
            return await self._analyze_data(data, instructions)
        elif task_type == "text_processing":
            return await self._process_text(data, instructions)
        elif task_type == "summarization":
            return await self._summarize(data)
        elif task_type == "format_conversion":
            return await self._convert_format(data, request.get("target_format"))
        else:
            return {
                "status": "error",
                "message": f"Unknown task type: {task_type}"
            }
    
    async def _analyze_data(self, data: Any, instructions: str) -> Dict[str, Any]:
        """Analyze data based on instructions"""
        
        prompt = f"""
        Analyze the following data:
        {data}
        
        Instructions: {instructions}
        
        Provide a detailed analysis with insights and recommendations.
        """
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        
        return {
            "status": "success",
            "agent": self.agent_name,
            "task": "data_analysis",
            "result": response.content
        }
    
    async def _process_text(self, text: str, instructions: str) -> Dict[str, Any]:
        """Process text based on instructions"""
        
        prompt = f"""
        Process the following text:
        {text}
        
        Instructions: {instructions}
        """
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        
        return {
            "status": "success",
            "agent": self.agent_name,
            "task": "text_processing",
            "result": response.content
        }
    
    async def _summarize(self, text: str) -> Dict[str, Any]:
        """Summarize text"""
        
        prompt = f"""
        Provide a concise summary of the following text:
        {text}
        """
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        
        return {
            "status": "success",
            "agent": self.agent_name,
            "task": "summarization",
            "result": response.content
        }
    
    async def _convert_format(self, data: Any, target_format: str) -> Dict[str, Any]:
        """Convert data to target format"""
        
        prompt = f"""
        Convert the following data to {target_format} format:
        {data}
        """
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        
        return {
            "status": "success",
            "agent": self.agent_name,
            "task": "format_conversion",
            "result": response.content
        }
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return agent capabilities"""
        return {
            "agent_name": self.agent_name,
            "capabilities": self.capabilities,
            "status": "active"
        }

