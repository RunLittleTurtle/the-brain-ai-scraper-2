#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LangGraph application for the intent inference workflow.

This module implements the LangGraph-based workflow for intent inference,
providing a structured approach to extracting intent specifications from
natural language user queries.
"""
import logging
import asyncio
from typing import Dict, Any, Optional, List, TypedDict, cast
from typing_extensions import Literal

from langchain_core.messages import HumanMessage

from langgraph.graph import START, END, StateGraph

# Import from our project
from intent_inference.models.context import ContextStore
from intent_inference.models.intent_spec import IntentSpec

# Import node functions
from intent_inference.graph.nodes_simple import (
    branch_logic,
    process_new_intent, 
    process_feedback,
    post_process_intent,
    post_process_feedback,
    validate_intent,
    check_url_health,
    make_decision,
    add_critique, 
    mark_for_human_review
)


# Configure module logger
logger = logging.getLogger(__name__)


# Define GraphState as TypedDict for type hinting
class GraphState(TypedDict, total=False):
    context: ContextStore
    intent_output: Optional[Dict[str, Any]]
    feedback_output: Optional[Dict[str, Any]]
    intent_spec: Optional[IntentSpec]
    validation_result: Optional[Dict[str, Any]]
    url_health_status: Optional[Dict[str, str]]


def initialize_memory(state: GraphState) -> Dict[str, Any]:
    """
    Initialize or update the memory state with context information.
    
    Args:
        state: Current graph state
        
    Returns:
        Updated graph state with initialized memory
    """
    context = state.get("context", ContextStore())
    
    # Add initial human message to memory
    messages = [HumanMessage(content=context.user_query or "")]
    
    return {"context": context, "memory": messages}


def update_context_with_intent(state: GraphState) -> Dict[str, Any]:
    """
    Update the context with the latest intent specification.
    
    Args:
        state: Current graph state with intent spec
        
    Returns:
        Updated state with context containing latest spec
    """
    intent_spec = state.get("intent_spec")
    context = state.get("context", ContextStore())
    
    if intent_spec:
        # Update the context with the latest spec
        context.update_last_spec(intent_spec)
    
    return {"context": context}


def branch_router(state: GraphState) -> str:
    """
    Determine whether to process the input as new intent or feedback.
    
    Args:
        state: Current graph state
        
    Returns:
        Next node name as string: "process_new_intent" or "process_feedback"
    """
    result = branch_logic(state)
    return result  # Returns "process_new_intent" or "process_feedback"


def decision_router(state: GraphState) -> str:
    """
    Route based on validation decision.
    
    Args:
        state: Current graph state
        
    Returns:
        Next node name as string: "add_critique" or "human_review"
    """
    result = make_decision(state)
    if result == "error":
        return "human_review"  # Fall back to human review on error
    return result  # Returns "add_critique" or "human_review"


def get_intent_graph(config: Optional[Dict[str, Any]] = None) -> StateGraph:
    """
    Create and configure the intent inference LangGraph workflow.
    
    Args:
        config: Optional configuration parameters for the graph
        
    Returns:
        Compiled LangGraph StateGraph ready for execution
    """
    # Create the state graph
    workflow = StateGraph(GraphState)
    
    # Add nodes for memory management and branching
    workflow.add_node("initialize_memory", initialize_memory)
    workflow.add_node("branch_logic", branch_logic)
    workflow.add_node("update_context", update_context_with_intent)
    
    # Add process nodes for new intent and feedback
    workflow.add_node("process_new_intent", process_new_intent)
    workflow.add_node("process_feedback", process_feedback)
    
    # Add post-processing nodes
    workflow.add_node("post_process_intent", post_process_intent)
    workflow.add_node("post_process_feedback", post_process_feedback)
    
    # Add validation node
    workflow.add_node("validate_intent", validate_intent)
    
    # Add decision nodes
    workflow.add_node("add_critique", add_critique)
    workflow.add_node("human_review", mark_for_human_review)
    
    # Main flow structure
    
    # Set entry point
    workflow.set_entry_point("initialize_memory")
    
    # From memory initialization to branch logic
    workflow.add_edge("initialize_memory", "branch_logic")
    
    # Conditional branching based on whether input is new intent or feedback
    workflow.add_conditional_edges(
        "branch_logic",
        branch_router,
        {
            "process_new_intent": "process_new_intent",
            "process_feedback": "process_feedback"
        }
    )
    
    # Connect process nodes to post-process nodes
    workflow.add_edge("process_new_intent", "post_process_intent")
    workflow.add_edge("process_feedback", "post_process_feedback")
    
    # Connect post-process nodes to context update
    workflow.add_edge("post_process_intent", "update_context")
    workflow.add_edge("post_process_feedback", "update_context")
    
    # Connect context update to validation
    workflow.add_edge("update_context", "validate_intent")
    
    # Connect validation to conditional decision
    workflow.add_conditional_edges(
        "validate_intent",
        decision_router,
        {
            "add_critique": "add_critique",
            "human_review": "human_review"
        }
    )
    
    # Connect add_critique back to branch_logic for another iteration
    workflow.add_edge("add_critique", "branch_logic")
    
    # Connect human_review to the end
    workflow.add_edge("human_review", END)
    
    # Compile the graph
    return workflow.compile()


async def process_input(
    user_input: str, 
    previous_spec: Optional[IntentSpec] = None,
    is_feedback: bool = False,
    config: Optional[Dict[str, Any]] = None
) -> tuple[IntentSpec, bool]:
    """
    Process user input through the intent inference graph.
    
    Args:
        user_input: The user's query or feedback text
        previous_spec: Optional previous IntentSpec if this is feedback
        is_feedback: Whether this input should be treated as feedback
        config: Optional configuration for the graph execution
        
    Returns:
        Tuple of (intent_spec, needs_human_input) where:
        - intent_spec is the resulting specification
        - needs_human_input is True if human input/review is required
    """
    # Initialize context
    context = ContextStore(user_query=user_input, is_feedback=is_feedback)
    if previous_spec:
        context.update_last_spec(previous_spec)
    
    # Get the graph
    graph = get_intent_graph(config)
    
    # Initialize state
    state = {
        "context": context,
        "memory": [],
        "intent_output": None,
        "feedback_output": None,
        "intent_spec": None,
        "validation_result": None,
        "url_health_status": None,
    }
    
    try:
        # Execute the graph
        logger.info(f"Executing intent inference graph for input: {user_input[:50]}...")
        result = await graph.ainvoke(state)
        
        # Get the final intent spec
        intent_spec = result.get("intent_spec")
        
        # Determine if human input is needed
        needs_human_input = False
        if intent_spec:
            validation_status = getattr(intent_spec, "validation_status", None)
            needs_human_input = (
                validation_status in [
                    "needs_clarification", 
                    "needs_human_review",
                    "needs_human_approval"
                ] or
                len(getattr(intent_spec, "clarification_questions", [])) > 0
            )
        
        return intent_spec, needs_human_input
    except Exception as e:
        logger.error(f"Error executing intent inference graph: {str(e)}")
        
        # Create fallback spec in case of error
        if previous_spec:
            return previous_spec, True
        else:
            # Extract potential URL from query if possible
            import re
            url_match = re.search(r'https?://[^\s]+', user_input)
            url = url_match.group(0) if url_match else "https://example.com"
            
            # Create a fallback spec with the extracted URL
            fallback_spec = IntentSpec(
                id="error_fallback",
                user_query=user_input,
                target_urls=[url],
                fields_to_extract=[],
                validation_status="error",
                critique_history=["Graph execution failed"]
            )
            return fallback_spec, True


def process_input_sync(
    user_input: str,
    previous_spec: Optional[IntentSpec] = None,
    is_feedback: bool = False,
    config: Optional[Dict[str, Any]] = None
) -> tuple[IntentSpec, bool]:
    """
    Synchronous wrapper for the process_input function.
    
    Args:
        user_input: The user's query or feedback text
        previous_spec: Optional previous IntentSpec if this is feedback
        is_feedback: Whether this input should be treated as feedback
        config: Optional configuration for the graph execution
        
    Returns:
        Tuple of (intent_spec, needs_human_input)
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(
            process_input(
                user_input=user_input,
                previous_spec=previous_spec,
                is_feedback=is_feedback,
                config=config
            )
        )
    finally:
        loop.close()
