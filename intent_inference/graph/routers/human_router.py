"""
Router for human review results in the intent inference graph.

This module provides the route_human_review function which determines the next
step in the graph based on the human review decision.
"""
from intent_inference.graph.state import GraphState


def route_human_review(state: GraphState) -> str:
    """
    Route based on human review decision.
    
    Args:
        state: The current graph state
    
    Returns:
        The edge name to follow: "approved", "rejected", or "pending"
    """
    # Check if we're still waiting for human review
    if state.needs_human_review:
        return "pending"
    
    # Check the human approval flag
    if state.human_approval is True:
        return "approved"
    elif state.human_approval is False:
        return "rejected"
    else:
        # Default to pending if human_approval is None or unset
        return "pending"
