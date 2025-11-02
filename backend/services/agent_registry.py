"""
Agent Registry Service
Manages agent registration, discovery, and status
"""
from sqlalchemy.orm import Session
from models.agent import Agent, AgentType, AgentStatus
from typing import List, Dict, Any, Optional
import httpx

class AgentRegistry:
    """
    Central registry for managing agents
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def register_agent(self,
                      name: str,
                      description: str,
                      agent_type: AgentType,
                      endpoint: str,
                      capabilities: List[str],
                      config: Dict[str, Any] = None,
                      metadata: Dict[str, Any] = None) -> Agent:
        """Register a new agent"""
        
        # Check if agent already exists
        existing = self.db.query(Agent).filter(Agent.name == name).first()
        if existing:
            raise ValueError(f"Agent with name '{name}' already exists")
        
        agent = Agent(
            name=name,
            description=description,
            agent_type=agent_type,
            endpoint=endpoint,
            capabilities=capabilities,
            config=config or {},
            status=AgentStatus.ACTIVE,
            metadata=metadata or {}
        )
        
        self.db.add(agent)
        self.db.commit()
        self.db.refresh(agent)
        
        return agent
    
    def get_agent(self, agent_id: int) -> Optional[Agent]:
        """Get agent by ID"""
        
        return self.db.query(Agent).filter(Agent.id == agent_id).first()
    
    def get_agent_by_name(self, name: str) -> Optional[Agent]:
        """Get agent by name"""
        
        return self.db.query(Agent).filter(Agent.name == name).first()
    
    def list_agents(self, 
                   agent_type: Optional[AgentType] = None,
                   status: Optional[AgentStatus] = None) -> List[Agent]:
        """List all agents with optional filters"""
        
        query = self.db.query(Agent)
        
        if agent_type:
            query = query.filter(Agent.agent_type == agent_type)
        
        if status:
            query = query.filter(Agent.status == status)
        
        return query.all()
    
    def update_agent(self, agent_id: int, updates: Dict[str, Any]) -> Agent:
        """Update agent information"""
        
        agent = self.get_agent(agent_id)
        if not agent:
            raise ValueError(f"Agent {agent_id} not found")
        
        for key, value in updates.items():
            if hasattr(agent, key) and key not in ['id', 'created_at']:
                setattr(agent, key, value)
        
        self.db.commit()
        self.db.refresh(agent)
        
        return agent
    
    def deactivate_agent(self, agent_id: int) -> Agent:
        """Deactivate an agent"""
        
        return self.update_agent(agent_id, {"status": AgentStatus.INACTIVE})
    
    def activate_agent(self, agent_id: int) -> Agent:
        """Activate an agent"""
        
        return self.update_agent(agent_id, {"status": AgentStatus.ACTIVE})
    
    async def check_agent_health(self, agent_id: int) -> Dict[str, Any]:
        """Check if an agent is healthy and responsive"""
        
        agent = self.get_agent(agent_id)
        if not agent:
            return {"error": f"Agent {agent_id} not found"}
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{agent.endpoint}/health")
                
                if response.status_code == 200:
                    agent.status = AgentStatus.ACTIVE
                    self.db.commit()
                    return {
                        "agent_id": agent_id,
                        "status": "healthy",
                        "response": response.json()
                    }
                else:
                    agent.status = AgentStatus.ERROR
                    self.db.commit()
                    return {
                        "agent_id": agent_id,
                        "status": "unhealthy",
                        "error": f"Status code: {response.status_code}"
                    }
        except Exception as e:
            agent.status = AgentStatus.ERROR
            self.db.commit()
            return {
                "agent_id": agent_id,
                "status": "error",
                "error": str(e)
            }
    
    def find_agents_by_capability(self, capability: str) -> List[Agent]:
        """Find agents with a specific capability"""
        
        agents = self.db.query(Agent).filter(
            Agent.status == AgentStatus.ACTIVE
        ).all()
        
        return [
            agent for agent in agents 
            if capability in agent.capabilities
        ]
    
    def get_agent_stats(self) -> Dict[str, Any]:
        """Get statistics about registered agents"""
        
        total = self.db.query(Agent).count()
        active = self.db.query(Agent).filter(Agent.status == AgentStatus.ACTIVE).count()
        inactive = self.db.query(Agent).filter(Agent.status == AgentStatus.INACTIVE).count()
        error = self.db.query(Agent).filter(Agent.status == AgentStatus.ERROR).count()
        
        by_type = {}
        for agent_type in AgentType:
            count = self.db.query(Agent).filter(Agent.agent_type == agent_type).count()
            by_type[agent_type.value] = count
        
        return {
            "total": total,
            "active": active,
            "inactive": inactive,
            "error": error,
            "by_type": by_type
        }

