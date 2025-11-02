from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class ConversationContext(Base):
    __tablename__ = "conversation_contexts"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)
    user_id = Column(String, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    meta_data = Column(JSON)
    
    messages = relationship("Message", back_populates="context")

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    context_id = Column(Integer, ForeignKey("conversation_contexts.id"))
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True)
    role = Column(String)  # user, assistant, system
    content = Column(Text)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    meta_data = Column(JSON)
    
    context = relationship("ConversationContext", back_populates="messages")

class AgentMemory(Base):
    __tablename__ = "agent_memories"
    
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"))
    session_id = Column(String, index=True)
    memory_type = Column(String)  # short_term, long_term, working
    content = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)

