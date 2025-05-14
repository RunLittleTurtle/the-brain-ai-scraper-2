"""
Human review nodes for intent inference graph.

This module provides nodes for handling human review of intent specifications.
"""
from typing import Dict, Any, List, Optional

from intent_inference.graph.state import GraphState
from intent_inference.utils.visualization import add_system_message, add_assistant_message, format_intent_spec_for_display


def prepare_for_human_review(state: GraphState) -> Dict[str, Any]:
    """
    Prepare intent for human review.
    
    This node sets the needs_human_review flag to pause the graph
    execution until human input is received.
    
    Args:
        state: Current graph state
        
    Returns:
        Updated graph state
    """
    messages = state.messages
    
    # Check if we have a spec to review
    if state.current_intent_spec is None:
        error_message = "Cannot prepare for human review without an intent specification"
        messages = add_system_message(messages, f"❌ {error_message}")
        
        return {
            "state": GraphState(
                context=state.context,
                error_message=error_message,
                messages=messages,
                needs_human_review=False
            )
        }
    
    # Add system message about human review
    messages = add_system_message(
        messages,
        "👤 Waiting for human review and approval..."
    )
    
    # Add the intent specification for review
    messages = add_assistant_message(
        messages,
        f"📋 Please review this intent specification:\n\n{format_intent_spec_for_display(state.current_intent_spec)}",
        metadata={"spec_id": state.current_intent_spec.spec_id, "for_review": True}
    )
    
    # Return updated state with needs_human_review flag
    return {
        "state": GraphState(
            context=state.context,
            current_intent_spec=state.current_intent_spec,
            validation_result=state.validation_result,
            messages=messages,
            needs_human_review=True
        )
    }


def process_rejection(state: GraphState) -> Dict[str, Any]:
    """
    Process human rejection and prepare for revision.
    
    Args:
        state: Current graph state
        
    Returns:
        Updated graph state
    """
    messages = state.messages
    
    # Add rejection message
    messages = add_system_message(
        messages,
        f"👤 Human rejected the intent specification."
    )
    
    if state.user_feedback:
        messages = add_user_message(
            messages,
            f"💬 Rejection feedback: {state.user_feedback}"
        )
        
        # Add feedback as critique hint
        updated_context = state.context.add_critique_hints([state.user_feedback])
        updated_context = updated_context.increment_iteration()
    else:
        updated_context = state.context.increment_iteration()
    
    # Return updated state
    return {
        "state": GraphState(
            context=updated_context,
            current_intent_spec=state.current_intent_spec,
            validation_result=None,  # Clear validation result
            messages=messages,
            needs_human_review=False,
            human_approval=None  # Reset human approval
        )
    }


def finalize_intent(state: GraphState) -> Dict[str, Any]:
    """
    Finalize approved intent.
    
    Args:
        state: Current graph state
        
    Returns:
        Updated graph state
    """
    messages = state.messages
    
    if state.current_intent_spec is None:
        error_message = "Cannot finalize without an intent specification"
        messages = add_system_message(messages, f"❌ {error_message}")
        
        return {
            "state": GraphState(
                context=state.context,
                error_message=error_message,
                messages=messages
            )
        }
    
    # Update status of intent spec
    final_spec = state.current_intent_spec.model_copy(deep=True)
    final_spec.validation_status = "user_approved"
    
    # Add system message about approval
    messages = add_system_message(
        messages,
        f"✅ Intent specification approved by human reviewer!"
    )
    
    messages = add_assistant_message(
        messages,
        f"📦 Final Intent Specification ({final_spec.spec_id}):\n\n{format_intent_spec_for_display(final_spec)}",
        metadata={"final": True, "spec_id": final_spec.spec_id}
    )
    
    # Return updated state
    return {
        "state": GraphState(
            context=state.context,
            current_intent_spec=final_spec,
            validation_result=state.validation_result,
            messages=messages,
            needs_human_review=False
        )
    }
