"""
Router for validation results in the intent inference graph.

This module provides the route_validation function which determines the next
step in the graph based on the validation result.
"""
from intent_inference.graph.state import GraphState
from intent_inference.state import ValidationStatus


def route_validation(state: GraphState) -> str:
    """
    Route based on validation results.
    
    Args:
        state: The current graph state
    
    Returns:
        The edge name to follow: "valid" or "invalid"
    """
    # Check if there is a validation result
    if not state.validation_result:
        # Default to invalid if no validation result
        return "invalid"
    
    # Route based on the validation status
    if state.validation_result.is_valid:
        return "valid"
    else:
        return "invalid"
