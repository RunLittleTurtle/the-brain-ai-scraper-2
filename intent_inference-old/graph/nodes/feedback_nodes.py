"""
Feedback processing nodes for intent inference graph.

This module provides nodes for processing feedback on existing intents.
"""
from typing import Dict, Any, List, Optional, cast

from langchain_core.language_models import BaseChatModel

from intent_inference.graph.state import GraphState, IntentSpec
from intent_inference.graph.chains.feedback_chain import FeedbackChain
from intent_inference.utils.visualization import add_user_message, add_assistant_message, format_intent_spec_for_display


def process_feedback(state: GraphState, llm: BaseChatModel) -> Dict[str, Any]:
    """
    Process feedback on an existing intent using the FeedbackChain.
    
    Args:
        state: Current graph state
        llm: Language model to use for processing
        
    Returns:
        Updated graph state
    """
    # Add user message to visualization
    messages = add_user_message(
        state.messages, 
        f"💬 Feedback received: {state.context.user_query}"
    )
    
    # Check if we have a last spec in context
    if state.context.last_spec is None:
        error_message = "Cannot process feedback without previous intent specification"
        messages = add_assistant_message(messages, f"❌ {error_message}")
        
        return {
            "state": GraphState(
                context=state.context,
                error_message=error_message,
                messages=messages
            )
        }
    
    # Initialize the feedback chain
    feedback_chain = FeedbackChain(llm)
    
    try:
        # Process feedback
        llm_output = feedback_chain.run(
            original_query=state.context.last_spec.original_user_query,
            current_spec=state.context.last_spec,
            user_feedback=state.context.user_query
        )
        
        # Create updated intent spec
        updates: Dict[str, Any] = {}
        
        if llm_output.updated_target_urls is not None:
            updates["target_urls_or_sites"] = llm_output.updated_target_urls
            
        if llm_output.updated_data_fields is not None:
            updates["data_to_extract"] = llm_output.updated_data_fields
            
        if llm_output.updated_constraints is not None:
            updates["constraints"] = llm_output.updated_constraints
        
        # Create a revision of the current spec
        updated_spec = state.context.last_spec.create_revision(**updates)
        
        # Add assistant message to visualization
        messages = add_assistant_message(
            messages,
            f"📝 Updated Intent Based on Feedback:\n\n{format_intent_spec_for_display(updated_spec)}",
            metadata={"spec_id": updated_spec.spec_id, "reasoning": llm_output.reasoning}
        )
        
        # Update the context with the last spec
        updated_context = state.context.update_last_spec(updated_spec)
        
        # Return updated state
        return {
            "state": GraphState(
                context=updated_context,
                current_intent_spec=updated_spec,
                messages=messages
            )
        }
    
    except Exception as e:
        # Handle errors
        error_message = f"Error processing feedback: {str(e)}"
        messages = add_assistant_message(messages, f"❌ {error_message}")
        
        return {
            "state": GraphState(
                context=state.context,
                error_message=error_message,
                messages=messages
            )
        }
