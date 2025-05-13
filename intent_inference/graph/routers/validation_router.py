"""
Validation router for intent inference graph.

This module provides a router for handling validation results
in the intent inference graph.
"""
from typing import Dict, Literal, Any

from intent_inference.graph.state import GraphState


def route_validation(state: GraphState) -> Literal["valid", "invalid"]:
    """
    Route based on validation result.
    
    Args:
        state: Current graph state
        
    Returns:
        Routing decision: "valid" or "invalid"
    """
    if state.validation_result is None:
        return "invalid"
    
    return "valid" if state.validation_result.is_valid else "invalid"
