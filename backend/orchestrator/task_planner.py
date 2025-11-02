"""
Task Planning Module
Breaks down complex tasks into executable steps and assigns them to appropriate agents
"""
from typing import Dict, Any, List
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from sqlalchemy.orm import Session
from models.agent import Agent, AgentType
from models.task import Task, TaskStep, TaskStatus
from config import get_settings
import json

settings = get_settings()

class TaskPlanner:
    """
    Plans task execution and assigns work to agents
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.llm = ChatGroq(
            temperature=0.2,
            model="llama-3.3-70b-versatile",
            groq_api_key=settings.groq_api_key
        )
    
    async def create_execution_plan(self, task_description: str, session_id: str) -> Task:
        """Create an execution plan for a task"""
        
        # Get available agents
        agents = self.db.query(Agent).filter(Agent.status == "active").all()
        
        agent_info = [
            {
                "id": agent.id,
                "name": agent.name,
                "type": agent.agent_type,
                "capabilities": agent.capabilities
            }
            for agent in agents
        ]
        
        # Create planning prompt
        planning_prompt = f"""
        You are a task planning AI. Given a task description and available agents,
        create a detailed execution plan.
        
        Task: {task_description}
        
        Available Agents:
        {json.dumps(agent_info, indent=2)}
        
        CRITICAL ROUTING GUIDELINES:
        
        1. ALWAYS prefer the SIMPLEST agent that can complete the task
        
        2. Use DataAnalyzer (API agent) for:
           - Simple calculations (1+1, 5*10, math operations)
           - Quick facts and definitions (What is X?, Define Y)
           - Short text processing and summarization
           - Data analysis tasks
           - Any task completable in under 5 seconds
           - Single-step queries
        
        3. Use ResearchAgent (A2A/LangGraph) for:
           - Multi-step reasoning and research
           - Complex analysis requiring multiple sources
           - Strategic planning and recommendations
           - Tasks requiring deep investigation
           - Workflows with multiple stages
        
        4. Task Complexity Assessment:
           - Simple (1 step, < 5 sec) → DataAnalyzer
           - Medium (2-3 steps, < 15 sec) → DataAnalyzer or light planning
           - Complex (4+ steps, > 15 sec) → ResearchAgent with full workflow
        
        EXAMPLES:
        - "1+1" → DataAnalyzer (simple calculation)
        - "What is AI?" → DataAnalyzer (simple definition)
        - "Summarize this text" → DataAnalyzer (simple processing)
        - "Research AI impact on healthcare and create strategic recommendations" → ResearchAgent (complex research)
        - "Analyze quarterly sales data and identify trends" → DataAnalyzer (data analysis)
        
        Create a plan with these elements:
        1. Assess task complexity first
        2. Break down the task into sequential steps (keep it simple if possible)
        3. Assign each step to the MOST APPROPRIATE agent (prefer simpler agents)
        4. Define inputs and expected outputs for each step
        5. Identify dependencies between steps
        
        Return your response as JSON with this structure:
        {{
            "steps": [
                {{
                    "step_number": 1,
                    "description": "...",
                    "agent_id": 1,
                    "agent_name": "...",
                    "dependencies": [],
                    "expected_output": "..."
                }}
            ],
            "estimated_duration": "...",
            "complexity": "low|medium|high"
        }}
        """
        
        system_message = SystemMessage(content="You are an expert task planning AI. Always respond with valid JSON.")
        response = self.llm.invoke([system_message, HumanMessage(content=planning_prompt)])
        
        # Parse the plan
        try:
            plan_data = json.loads(response.content)
        except json.JSONDecodeError:
            # Fallback if LLM doesn't return valid JSON
            plan_data = {
                "steps": [{
                    "step_number": 1,
                    "description": task_description,
                    "agent_id": agents[0].id if agents else None,
                    "agent_name": agents[0].name if agents else "unknown",
                    "dependencies": [],
                    "expected_output": "Task completion"
                }],
                "estimated_duration": "unknown",
                "complexity": "medium"
            }
        
        # Create task in database
        task = Task(
            session_id=session_id,
            description=task_description,
            plan=plan_data,
            status=TaskStatus.PLANNING,
            assigned_agents=[step["agent_id"] for step in plan_data["steps"]],
            metadata={"complexity": plan_data.get("complexity", "medium")}
        )
        
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        
        # Create task steps
        for step_data in plan_data["steps"]:
            task_step = TaskStep(
                task_id=task.id,
                step_number=step_data["step_number"],
                agent_id=step_data.get("agent_id"),
                description=step_data["description"],
                status=TaskStatus.PENDING,
                input_data={"dependencies": step_data.get("dependencies", [])}
            )
            self.db.add(task_step)
        
        self.db.commit()
        
        return task
    
    async def update_plan(self, task_id: int, updates: Dict[str, Any]) -> Task:
        """Update an existing task plan"""
        
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        # Update task fields
        for key, value in updates.items():
            if hasattr(task, key):
                setattr(task, key, value)
        
        self.db.commit()
        self.db.refresh(task)
        
        return task
    
    def get_next_steps(self, task_id: int) -> List[TaskStep]:
        """Get the next executable steps for a task"""
        
        return self.db.query(TaskStep).filter(
            TaskStep.task_id == task_id,
            TaskStep.status == TaskStatus.PENDING
        ).order_by(TaskStep.step_number).all()

