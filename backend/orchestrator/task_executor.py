"""
Task Execution Module
Executes planned tasks by coordinating with agents
"""
from typing import Dict, Any
from sqlalchemy.orm import Session
from models.task import Task, TaskStep, TaskStatus
from models.agent import Agent, AgentType
from models.memory import Message, ConversationContext
from agents.a2a_protocol import A2AProtocolHandler
import httpx
import asyncio
from datetime import datetime

class TaskExecutor:
    """
    Executes tasks by coordinating with assigned agents
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.a2a_handlers = {}
    
    async def execute_task(self, task_id: int) -> Dict[str, Any]:
        """Execute a complete task"""
        
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return {"error": f"Task {task_id} not found"}
        
        # Update task status
        task.status = TaskStatus.IN_PROGRESS
        self.db.commit()
        
        # Get all task steps
        steps = self.db.query(TaskStep).filter(
            TaskStep.task_id == task_id
        ).order_by(TaskStep.step_number).all()
        
        results = []
        context = {}
        
        for step in steps:
            try:
                step_result = await self.execute_step(step, context)
                results.append(step_result)
                
                # Update context with step results
                context[f"step_{step.step_number}"] = step_result
                
                # Update step status
                step.status = TaskStatus.COMPLETED
                step.output_data = step_result
                step.completed_at = datetime.utcnow()
                self.db.commit()
                
            except Exception as e:
                step.status = TaskStatus.FAILED
                step.output_data = {"error": str(e)}
                self.db.commit()
                
                task.status = TaskStatus.FAILED
                task.result = {"error": f"Failed at step {step.step_number}: {str(e)}"}
                self.db.commit()
                
                return task.result
        
        # Task completed successfully
        task.status = TaskStatus.COMPLETED
        task.result = {
            "status": "completed",
            "steps": results,
            "summary": self._generate_summary(results)
        }
        task.completed_at = datetime.utcnow()
        self.db.commit()
        
        return task.result
    
    async def execute_step(self, step: TaskStep, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single task step"""
        
        agent = self.db.query(Agent).filter(Agent.id == step.agent_id).first()
        if not agent:
            raise ValueError(f"Agent {step.agent_id} not found")
        
        # Prepare input data with context
        input_data = {
            "description": step.description,
            "context": context,
            "step_input": step.input_data
        }
        
        # Execute based on agent type
        if agent.agent_type == AgentType.A2A_SERVER:
            result = await self._execute_a2a_agent(agent, input_data)
        elif agent.agent_type == AgentType.API:
            result = await self._execute_api_agent(agent, input_data)
        else:
            result = {"error": f"Unknown agent type: {agent.agent_type}"}
        
        return result
    
    async def _execute_a2a_agent(self, agent: Agent, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute task through A2A protocol"""
        
        # Get or create A2A handler for this agent
        if agent.id not in self.a2a_handlers:
            self.a2a_handlers[agent.id] = A2AProtocolHandler(
                agent_id=str(agent.id),
                endpoint=agent.endpoint
            )
        
        handler = self.a2a_handlers[agent.id]
        
        # Send message via A2A protocol
        result = await handler.send_message(
            receiver=agent.name,
            content=input_data,
            session_id=input_data.get("session_id", "default")
        )
        
        return result
    
    async def _execute_api_agent(self, agent: Agent, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute task through REST API"""
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(
                    f"{agent.endpoint}/process",
                    json=input_data,
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                return {
                    "error": str(e),
                    "agent": agent.name,
                    "status": "failed"
                }
    
    def _generate_summary(self, results: list) -> str:
        """Generate a summary of task execution"""
        
        successful_steps = len([r for r in results if r.get("status") != "error"])
        total_steps = len(results)
        
        summary = f"Completed {successful_steps}/{total_steps} steps successfully."
        
        return summary
    
    async def cancel_task(self, task_id: int) -> Dict[str, Any]:
        """Cancel a running task"""
        
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return {"error": f"Task {task_id} not found"}
        
        task.status = TaskStatus.CANCELLED
        self.db.commit()
        
        return {
            "status": "cancelled",
            "task_id": task_id
        }
    
    async def cleanup(self):
        """Cleanup resources"""
        for handler in self.a2a_handlers.values():
            await handler.close()

