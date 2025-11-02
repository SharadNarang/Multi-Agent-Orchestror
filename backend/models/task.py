from sqlalchemy import Column, Integer, String, JSON, DateTime, Enum, ForeignKey, Text
from sqlalchemy.sql import func
from database import Base
import enum

class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    description = Column(Text)
    plan = Column(JSON)  # Task execution plan
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    assigned_agents = Column(JSON)  # List of agent IDs
    result = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    meta_data = Column(JSON)

class TaskStep(Base):
    __tablename__ = "task_steps"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    step_number = Column(Integer)
    agent_id = Column(Integer, ForeignKey("agents.id"))
    description = Column(Text)
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    input_data = Column(JSON)
    output_data = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

