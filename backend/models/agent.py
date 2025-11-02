from sqlalchemy import Column, Integer, String, JSON, DateTime, Enum, Boolean
from sqlalchemy.sql import func
from database import Base
import enum

class AgentType(str, enum.Enum):
    A2A_SERVER = "a2a_server"
    API = "api"
    LOCAL = "local"

class AgentStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"

class Agent(Base):
    __tablename__ = "agents"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)
    agent_type = Column(Enum(AgentType))
    endpoint = Column(String)  # A2A URL or API endpoint
    capabilities = Column(JSON)  # List of capabilities
    config = Column(JSON)  # Agent-specific configuration
    status = Column(Enum(AgentStatus), default=AgentStatus.ACTIVE)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    meta_data = Column(JSON)

