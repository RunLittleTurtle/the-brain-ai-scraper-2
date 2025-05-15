"""
Nodes for human review and approval of intent specifications.

This module provides the human_review node which handles the human review
step in the intent inference workflow.
"""
from typing import Any, Optional

from intent_inference.state import Message
from intent_inference.graph.state import GraphState


def human_review(state: GraphState) -> GraphState:
    """
    Prepare the intent specification for human review.
    
    Args:
        state: The current graph state
    
    Returns:
        Updated graph state with human review request
    """
    # Create a copy of the state to avoid mutations
    state = state.model_copy(deep=True)
    
    # Check if there is an intent spec to review
    if not state.current_intent_spec:
        state.error_message = "No intent specification to review"
        state.messages.append(Message(
            role="system",
            content="⚠️ Error: No intent specification available for review"
        ))
        return state
    
    # Check if validation has been performed
    if not state.validation_result:
        state.error_message = "Intent specification has not been validated"
        state.messages.append(Message(
            role="system",
            content="⚠️ Error: Intent specification has not been validated"
        ))
        return state
    
    # Check if the intent spec is valid
    if not state.validation_result.is_valid:
        state.error_message = "Cannot review an invalid intent specification"
        state.messages.append(Message(
            role="system",
            content="⚠️ Error: Cannot review an invalid intent specification"
        ))
        return state
    
    # Get the intent spec for formatting
    intent_spec = state.current_intent_spec
    
    # Format a summary of the intent spec for review
    summary = (
        f"## Intent Specification Review\n\n"
        f"**Original Query**: {intent_spec.original_user_query}\n\n"
        f"**Target URLs/Sites**:\n"
    )
    
    # Add URL list with health status
    for url in intent_spec.target_urls_or_sites:
        health = intent_spec.url_health_status.get(url, "unknown")
        health_icon = "✅" if health == "healthy" else "⚠️"
        summary += f"- {health_icon} {url}\n"
    
    # Add data fields
    summary += "\n**Data to Extract**:\n"
    for field in intent_spec.data_to_extract:
        summary += f"- **{field.field_name}**: {field.description}\n"
    
    # Add constraints if any
    if intent_spec.constraints:
        summary += "\n**Constraints**:\n"
        for key, value in intent_spec.constraints.items():
            summary += f"- **{key}**: {value}\n"
    
    # Add review instructions
    instructions = (
        "\n## Review Instructions\n\n"
        "Please review this intent specification and either approve it to proceed "
        "with web scraping, or reject it for further refinement."
    )
    
    # Set the state for human review
    state.needs_human_review = True
    state.human_approval = None
    
    # Add messages for visualization
    state.messages.append(Message(
        role="assistant",
        content=summary + instructions
    ))
    
    return state


def process_human_approval(state: GraphState, approved: bool, feedback: Optional[str] = None) -> GraphState:
    """
    Process human approval decision.
    
    Args:
        state: The current graph state
        approved: Whether the human approved the intent specification
        feedback: Optional feedback from the human
    
    Returns:
        Updated graph state with human approval decision
    """
    # Create a copy of the state to avoid mutations
    state = state.model_copy(deep=True)
    
    # Set the human approval flag
    state.human_approval = approved
    
    # Store the feedback if provided
    if feedback:
        state.user_feedback = feedback
    
    # Add message for visualization
    if approved:
        state.messages.append(Message(
            role="human",
            content="✅ Intent specification approved."
        ))
        state.messages.append(Message(
            role="assistant",
            content="Thank you! The intent specification has been approved and is ready for use."
        ))
    else:
        feedback_msg = f"with feedback: {feedback}" if feedback else "without specific feedback"
        state.messages.append(Message(
            role="human",
            content=f"❌ Intent specification rejected {feedback_msg}."
        ))
        state.messages.append(Message(
            role="assistant",
            content="I'll refine the intent specification based on your feedback."
        ))
    
    # Reset the human review flag since we've processed the decision
    state.needs_human_review = False
    
    return state
