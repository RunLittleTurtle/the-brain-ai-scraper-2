"""
Validation router for intent inference graph.

This module provides a router for handling validation results
in the intent inference graph.
"""
from typing import Dict, Literal, Any

from intent_inference.graph.state import GraphState, ValidationStatus


def route_validation(state: GraphState) -> Literal["valid", "invalid", "needs_clarification", "url_issue", "missing_data"]:
    """
    Enhanced router based on the detailed validation status.
    
    Args:
        state: Current graph state
        
    Returns:
        Routing decision with more nuanced options based on validation status
    """
    # Handle case with no validation result
    if state.validation_result is None:
        return "invalid"
    
    # If valid, easy path
    if state.validation_result.is_valid:
        return "valid"
    
    # Use the enhanced status for more nuanced routing
    status_mapping = {
        ValidationStatus.NEEDS_CLARIFICATION: "needs_clarification",
        ValidationStatus.URL_ISSUE: "url_issue",
        ValidationStatus.MISSING_DATA: "missing_data",
        # Default fallback
        ValidationStatus.INVALID: "invalid"
    }
    
    return status_mapping.get(state.validation_result.status, "invalid")
