"""Test script to debug task creation"""
import sys
import os
import traceback

# Set Groq API key from environment
# os.environ['GROQ_API_KEY'] = 'your-groq-api-key-here'

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.agent import Agent
from orchestrator.task_planner import TaskPlanner
import asyncio

# Setup database
engine = create_engine('sqlite:///./demo.db')
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

async def test_task_creation():
    try:
        print("Testing task creation...")
        
        # Check agents
        agents = db.query(Agent).all()
        print(f"Found {len(agents)} agents")
        for agent in agents:
            print(f"  - {agent.name} ({agent.agent_type})")
        
        # Create task planner
        planner = TaskPlanner(db)
        
        # Try to create a task
        print("\nCreating task...")
        task = await planner.create_execution_plan(
            task_description="Summarize the benefits of AI",
            session_id="test-session"
        )
        
        print(f"\nSUCCESS! Task created successfully!")
        print(f"Task ID: {task.id}")
        print(f"Status: {task.status}")
        print(f"Plan: {task.plan}")
        
    except Exception as e:
        print(f"\nError occurred:")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print("\nFull traceback:")
        traceback.print_exc()

# Run the test
asyncio.run(test_task_creation())

db.close()

