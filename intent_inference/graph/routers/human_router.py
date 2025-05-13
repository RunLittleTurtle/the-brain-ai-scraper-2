"""
Human review router for intent inference graph.

This module provides a router for handling human review decisions
in the intent inference graph.
"""
from typing import Dict, Literal, Any

from intent_inference.graph.state import GraphState


def route_human_review(state: GraphState) -> Literal["approved", "rejected", "pending"]:
    """
    Route based on human approval status.
    
    Args:
        state: Current graph state
        
    Returns:
        Routing decision: "approved", "rejected", or "pending"
    """
    if state.human_approval is None:
        return "pending"
    
    return "approved" if state.human_approval else "rejected"
