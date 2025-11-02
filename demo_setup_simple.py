import sys
sys.path.insert(0, 'backend')
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.agent import Agent, AgentType, AgentStatus
from models.task import Task, TaskStatus
from database import Base

engine = create_engine('sqlite:///./backend/demo.db')
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

print('=== MULTI-AGENT ORCHESTRATOR DEMO ===\n')
print('Step 1: Registering Agents...\n')

a2a_agent = Agent(
    name='ResearchAgent',
    description='LangGraph agent for complex reasoning',
    agent_type=AgentType.A2A_SERVER,
    endpoint='http://localhost:8001',
    capabilities=['research', 'analysis', 'planning'],
    config={},
    status=AgentStatus.ACTIVE,
    meta_data={}
)
db.add(a2a_agent)
db.commit()
db.refresh(a2a_agent)
print(f'Registered: {a2a_agent.name} (ID: {a2a_agent.id})')

api_agent = Agent(
    name='DataAnalyzer',
    description='API agent for data processing',
    agent_type=AgentType.API,
    endpoint='http://localhost:8002',
    capabilities=['data_analysis', 'summarization'],
    config={},
    status=AgentStatus.ACTIVE,
    meta_data={}
)
db.add(api_agent)
db.commit()
db.refresh(api_agent)
print(f'Registered: {api_agent.name} (ID: {api_agent.id})')

print('\nStep 2: Creating Task...\n')
task = Task(
    session_id='demo-001',
    description='Analyze AI trends and summarize findings',
    plan={'steps': [
        {'step': 1, 'agent_id': a2a_agent.id, 'action': 'Research AI trends'},
        {'step': 2, 'agent_id': api_agent.id, 'action': 'Summarize findings'}
    ]},
    status=TaskStatus.PENDING,
    assigned_agents=[a2a_agent.id, api_agent.id],
    meta_data={}
)
db.add(task)
db.commit()
db.refresh(task)
print(f'Created Task #{task.id}: {task.description}')
print(f'Status: {task.status}')
print(f'Steps: {len(task.plan["steps"])}')

print('\n=== SETUP COMPLETE ===')
print(f'\nAgents registered: 2')
print(f'Tasks created: 1')
print(f'\nDatabase: backend/demo.db')
db.close()
