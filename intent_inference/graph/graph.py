"""
LangGraph graph definition for intent inference.

This module defines the full intent inference graph structure,
connecting nodes, routers, and edges into a complete graph.
"""
from typing import Any, Dict, Optional
import os

from langchain_openai import ChatOpenAI
from langchain_core.runnables.config import RunnableConfig
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langsmith.run_helpers import traceable

# Import graph state
from intent_inference.graph.state import GraphState

# Import nodes
from intent_inference.graph.nodes.intent_nodes import process_new_intent
from intent_inference.graph.nodes.validation_nodes import validate_intent
from intent_inference.graph.nodes.human_nodes import human_review, process_human_approval

# Import routers
from intent_inference.graph.routers.validation_router import route_validation
from intent_inference.graph.routers.human_router import route_human_review


@traceable(run_type="chain")
def create_intent_inference_graph(config: RunnableConfig = None) -> StateGraph:
    """
    Factory for the intent inference graph.
    
    Args:
        config: Optional RunnableConfig for LangChain tracing
    
    Returns:
        Compiled StateGraph
    """
    # Create the basic graph with the graph state
    graph = StateGraph(GraphState)
    
    # Set up the LLM
    model_name = os.getenv("OPENAI_MODEL_NAME", "gpt-4o")
    llm = ChatOpenAI(model_name=model_name, temperature=0.2)
    
    # Define node configurations
    def new_intent_node(state): return process_new_intent(state, llm)
    def validate_node(state): return validate_intent(state, llm)
    
    # Add nodes to the graph
    graph.add_node("process_new_intent", new_intent_node)
    graph.add_node("validate_intent", validate_node)
    graph.add_node("human_review", human_review)
    
    # Connect the nodes as per our flowchart
    # START --> process_new_intent
    graph.add_edge(START, "process_new_intent")
    
    # process_new_intent --> validate_intent
    graph.add_edge("process_new_intent", "validate_intent")
    
    # validate_intent --> route_validation --> human_review or process_new_intent
    graph.add_conditional_edges(
        "validate_intent",
        route_validation,
        {
            "valid": "human_review",
            "invalid": "process_new_intent"
        }
    )
    
    # human_review --> route_human_review --> END or process_new_intent
    graph.add_conditional_edges(
        "human_review",
        route_human_review,
        {
            "approved": END,
            "rejected": "process_new_intent",
            "pending": END  # Pause and wait for human input
        }
    )
    
    # Compile the graph with a memory saver for checkpointing
    checkpointer = MemorySaver()
    return graph.compile(checkpointer=checkpointer)


def create_initial_state(user_query: str) -> GraphState:
    """
    Create the initial state for the graph with a user query.
    
    Args:
        user_query: The user query to process
    
    Returns:
        Initial GraphState
    """
    # Initialize with the user query in context
    return GraphState(
        context={"user_query": user_query},
        messages=[
            {
                "role": "system",
                "content": "Intent inference system initialized."
            },
            {
                "role": "human", 
                "content": user_query
            }
        ]
    )


def process_human_input(state: GraphState, approved: bool, feedback: Optional[str] = None) -> GraphState:
    """
    Process human input for a paused graph.
    
    Args:
        state: The current graph state
        approved: Whether the human approved the intent
        feedback: Optional feedback from the human
    
    Returns:
        Updated graph state
    """
    return process_human_approval(state, approved, feedback)
