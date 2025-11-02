"""
Memory Management Service
Handles conversation context and agent memory
"""
from sqlalchemy.orm import Session
from models.memory import ConversationContext, Message, AgentMemory
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

class MemoryService:
    """
    Manages conversation context and agent memory
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_session(self, user_id: str, metadata: Dict[str, Any] = None) -> ConversationContext:
        """Create a new conversation session"""
        
        import uuid
        session_id = str(uuid.uuid4())
        
        context = ConversationContext(
            session_id=session_id,
            user_id=user_id,
            metadata=metadata or {}
        )
        
        self.db.add(context)
        self.db.commit()
        self.db.refresh(context)
        
        return context
    
    def get_session(self, session_id: str) -> Optional[ConversationContext]:
        """Get a conversation session"""
        
        return self.db.query(ConversationContext).filter(
            ConversationContext.session_id == session_id
        ).first()
    
    def add_message(self, 
                   session_id: str,
                   role: str,
                   content: str,
                   agent_id: Optional[int] = None,
                   metadata: Dict[str, Any] = None) -> Message:
        """Add a message to conversation context"""
        
        context = self.get_session(session_id)
        if not context:
            raise ValueError(f"Session {session_id} not found")
        
        message = Message(
            context_id=context.id,
            agent_id=agent_id,
            role=role,
            content=content,
            metadata=metadata or {}
        )
        
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        
        # Update context timestamp
        context.updated_at = datetime.utcnow()
        self.db.commit()
        
        return message
    
    def get_conversation_history(self, session_id: str, limit: int = 50) -> List[Message]:
        """Get conversation history for a session"""
        
        context = self.get_session(session_id)
        if not context:
            return []
        
        return self.db.query(Message).filter(
            Message.context_id == context.id
        ).order_by(Message.timestamp.desc()).limit(limit).all()
    
    def save_agent_memory(self,
                         agent_id: int,
                         session_id: str,
                         memory_type: str,
                         content: Dict[str, Any],
                         ttl_hours: Optional[int] = None) -> AgentMemory:
        """Save agent-specific memory"""
        
        expires_at = None
        if ttl_hours:
            expires_at = datetime.utcnow() + timedelta(hours=ttl_hours)
        
        memory = AgentMemory(
            agent_id=agent_id,
            session_id=session_id,
            memory_type=memory_type,
            content=content,
            expires_at=expires_at
        )
        
        self.db.add(memory)
        self.db.commit()
        self.db.refresh(memory)
        
        return memory
    
    def get_agent_memory(self, 
                        agent_id: int,
                        session_id: str,
                        memory_type: Optional[str] = None) -> List[AgentMemory]:
        """Retrieve agent memory"""
        
        query = self.db.query(AgentMemory).filter(
            AgentMemory.agent_id == agent_id,
            AgentMemory.session_id == session_id
        )
        
        if memory_type:
            query = query.filter(AgentMemory.memory_type == memory_type)
        
        # Filter out expired memories
        query = query.filter(
            (AgentMemory.expires_at == None) | 
            (AgentMemory.expires_at > datetime.utcnow())
        )
        
        return query.all()
    
    def cleanup_expired_memories(self) -> int:
        """Remove expired memories"""
        
        deleted = self.db.query(AgentMemory).filter(
            AgentMemory.expires_at != None,
            AgentMemory.expires_at <= datetime.utcnow()
        ).delete()
        
        self.db.commit()
        
        return deleted
    
    def get_context_summary(self, session_id: str) -> Dict[str, Any]:
        """Get a summary of conversation context"""
        
        context = self.get_session(session_id)
        if not context:
            return {}
        
        messages = self.get_conversation_history(session_id)
        
        return {
            "session_id": session_id,
            "user_id": context.user_id,
            "created_at": context.created_at.isoformat(),
            "message_count": len(messages),
            "last_activity": context.updated_at.isoformat() if context.updated_at else None,
            "metadata": context.metadata
        }

