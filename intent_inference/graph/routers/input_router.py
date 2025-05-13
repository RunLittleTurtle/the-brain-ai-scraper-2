"""
Input router for intent inference graph.

This module provides a router for handling different input types
(new intent vs feedback) in the intent inference graph.
"""
from typing import Dict, Literal, Any

from intent_inference.graph.state import GraphState, InputType


def route_input(state: GraphState) -> Literal["new_intent", "feedback"]:
    """
    Route based on input type (new intent vs feedback).
    
    Args:
        state: Current graph state
        
    Returns:
        Routing decision: "new_intent" or "feedback"
    """
    return state.context.input_type.value
