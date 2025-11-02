"""
LangGraph-based Agent for A2A Server
This agent uses LangGraph to create a stateful, multi-step reasoning agent
"""
from typing import TypedDict, Annotated, Sequence
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
import operator
from config import get_settings

settings = get_settings()

# Define the agent state
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next_step: str
    task_context: dict
    intermediate_results: list

class LangGraphA2AAgent:
    """
    A sophisticated agent built with LangGraph for A2A protocol
    """
    
    def __init__(self, agent_name: str = "ResearchAgent"):
        self.agent_name = agent_name
        self.llm = ChatGroq(
            temperature=0.7,
            model="llama-3.3-70b-versatile",
            groq_api_key=settings.groq_api_key
        )
        self.graph = self._build_graph()
        
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        
        # Create the graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("analyze", self._analyze_task)
        workflow.add_node("plan", self._plan_execution)
        workflow.add_node("execute", self._execute_task)
        workflow.add_node("reflect", self._reflect_on_results)
        workflow.add_node("finalize", self._finalize_response)
        
        # Add edges
        workflow.set_entry_point("analyze")
        
        workflow.add_edge("analyze", "plan")
        workflow.add_edge("plan", "execute")
        workflow.add_conditional_edges(
            "execute",
            self._should_continue,
            {
                "continue": "execute",
                "reflect": "reflect"
            }
        )
        workflow.add_edge("reflect", "finalize")
        workflow.add_edge("finalize", END)
        
        return workflow.compile()
    
    def _analyze_task(self, state: AgentState) -> AgentState:
        """Analyze the incoming task"""
        messages = state["messages"]
        last_message = messages[-1]
        
        analysis_prompt = f"""
        Analyze the following task and determine:
        1. What type of task is this?
        2. What capabilities are needed?
        3. What are the key requirements?
        
        Task: {last_message.content}
        """
        
        response = self.llm.invoke([HumanMessage(content=analysis_prompt)])
        
        return {
            "messages": [AIMessage(content=f"Analysis: {response.content}")],
            "task_context": {"analysis": response.content},
            "next_step": "plan"
        }
    
    def _plan_execution(self, state: AgentState) -> AgentState:
        """Create an execution plan"""
        task_context = state.get("task_context", {})
        analysis = task_context.get("analysis", "")
        
        planning_prompt = f"""
        Based on this analysis:
        {analysis}
        
        Create a step-by-step execution plan with:
        1. Clear action items
        2. Expected outcomes for each step
        3. Dependencies between steps
        """
        
        response = self.llm.invoke([HumanMessage(content=planning_prompt)])
        
        task_context["plan"] = response.content
        
        return {
            "messages": [AIMessage(content=f"Plan: {response.content}")],
            "task_context": task_context,
            "next_step": "execute"
        }
    
    def _execute_task(self, state: AgentState) -> AgentState:
        """Execute the planned task"""
        task_context = state.get("task_context", {})
        plan = task_context.get("plan", "")
        messages = state["messages"]
        original_task = messages[0].content
        
        execution_prompt = f"""
        Original Task: {original_task}
        Plan: {plan}
        
        Now execute this task and provide detailed results.
        """
        
        response = self.llm.invoke([HumanMessage(content=execution_prompt)])
        
        intermediate_results = state.get("intermediate_results", [])
        intermediate_results.append(response.content)
        
        return {
            "messages": [AIMessage(content=f"Execution: {response.content}")],
            "intermediate_results": intermediate_results,
            "next_step": "reflect"
        }
    
    def _should_continue(self, state: AgentState) -> str:
        """Decide if we need more execution or can move to reflection"""
        intermediate_results = state.get("intermediate_results", [])
        
        # Simple logic: if we have results, move to reflection
        if len(intermediate_results) > 0:
            return "reflect"
        return "continue"
    
    def _reflect_on_results(self, state: AgentState) -> AgentState:
        """Reflect on the execution results"""
        intermediate_results = state.get("intermediate_results", [])
        
        reflection_prompt = f"""
        Review these execution results:
        {intermediate_results}
        
        Provide:
        1. Quality assessment
        2. Completeness check
        3. Any issues or improvements needed
        """
        
        response = self.llm.invoke([HumanMessage(content=reflection_prompt)])
        
        return {
            "messages": [AIMessage(content=f"Reflection: {response.content}")],
            "task_context": state.get("task_context", {}),
            "next_step": "finalize"
        }
    
    def _finalize_response(self, state: AgentState) -> AgentState:
        """Create the final response"""
        messages = state["messages"]
        intermediate_results = state.get("intermediate_results", [])
        
        final_prompt = f"""
        Based on all the work done, create a final comprehensive response.
        
        Results: {intermediate_results}
        """
        
        response = self.llm.invoke([HumanMessage(content=final_prompt)])
        
        return {
            "messages": [AIMessage(content=response.content)],
            "task_context": state.get("task_context", {}),
            "next_step": "end"
        }
    
    async def process_message(self, message: str, context: dict = None) -> dict:
        """Process an incoming message through the LangGraph"""
        
        initial_state = {
            "messages": [HumanMessage(content=message)],
            "next_step": "analyze",
            "task_context": context or {},
            "intermediate_results": []
        }
        
        # Run the graph
        final_state = self.graph.invoke(initial_state)
        
        # Extract the final response
        final_message = final_state["messages"][-1].content
        
        return {
            "response": final_message,
            "agent_name": self.agent_name,
            "state": final_state
        }

