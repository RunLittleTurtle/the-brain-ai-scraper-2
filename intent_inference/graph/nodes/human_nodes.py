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
    key_messages = state.key_messages
    
    # Check if we have a spec to review
    if state.current_intent_spec is None:
        error_message = "Cannot prepare for human review without an intent specification"
        key_messages = add_system_message(key_messages, f"❌ {error_message}")
        
        return {
            "state": GraphState(
                context=state.context,
                error_message=error_message,
                key_messages=key_messages,
                needs_human_review=False
            )
        }
    
    # Add system message about human review
    key_messages = add_system_message(
        key_messages,
        "👤 Waiting for human review and approval..."
    )
    
    # Add the intent specification for review
    key_messages = add_assistant_message(
        key_messages,
        f"📋 Please review this intent specification:\n\n{format_intent_spec_for_display(state.current_intent_spec)}",
        metadata={"spec_id": state.current_intent_spec.spec_id, "for_review": True}
    )
    
    # Return updated state with needs_human_review flag
    return {
        "state": GraphState(
            context=state.context,
            current_intent_spec=state.current_intent_spec,
            validation_result=state.validation_result,
            key_messages=key_messages,
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
    key_messages = state.key_messages
    
    # Add rejection message
    key_messages = add_system_message(
        key_messages,
        f"👤 Human rejected the intent specification."
    )
    
    if state.user_feedback:
        key_messages = add_user_message(
            key_messages,
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
            key_messages=key_messages,
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
    key_messages = state.key_messages
    
    if state.current_intent_spec is None:
        error_message = "Cannot finalize without an intent specification"
        key_messages = add_system_message(key_messages, f"❌ {error_message}")
        
        return {
            "state": GraphState(
                context=state.context,
                error_message=error_message,
                key_messages=key_messages
            )
        }
    
    # Update status of intent spec
    final_spec = state.current_intent_spec.model_copy(deep=True)
    final_spec.validation_status = "user_approved"
    
    # Add system message about approval
    key_messages = add_system_message(
        key_messages,
        f"✅ Intent specification approved by human reviewer!"
    )
    
    key_messages = add_assistant_message(
        key_messages,
        f"📦 Final Intent Specification ({final_spec.spec_id}):\n\n{format_intent_spec_for_display(final_spec)}",
        metadata={"final": True, "spec_id": final_spec.spec_id}
    )
    
    # Return updated state
    return {
        "state": GraphState(
            context=state.context,
            current_intent_spec=final_spec,
            validation_result=state.validation_result,
            key_messages=key_messages,
            needs_human_review=False
        )
    }
