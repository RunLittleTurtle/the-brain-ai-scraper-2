"""
Validation nodes for intent inference graph.

This module provides nodes for validating intent specifications
and handling validation results.
"""
from typing import Dict, Any, List, Optional

from langchain_core.language_models import BaseChatModel

from intent_inference.graph.state import GraphState, IntentSpec, ValidationResult
from intent_inference.graph.chains.validation_chain import ValidationChain
from intent_inference.graph.tools.url_health import check_urls_health_sync
from intent_inference.utils.visualization import add_assistant_message, add_system_message


def validate_intent(state: GraphState, llm: BaseChatModel) -> Dict[str, Any]:
    """
    Validate an intent specification using LLM-as-judge and URL health checks.
    
    Args:
        state: Current graph state
        llm: Language model to use for validation
        
    Returns:
        Updated graph state
    """
    key_messages = state.key_messages
    
    # Check if we have a spec to validate
    if state.current_intent_spec is None:
        error_message = "Cannot validate without an intent specification"
        key_messages = add_system_message(key_messages, f"❌ {error_message}")
        
        return {
            "state": GraphState(
                context=state.context,
                error_message=error_message,
                key_messages=key_messages
            )
        }
    
    try:
        # Add system message for validation start
        key_messages = add_system_message(
            key_messages, 
            "🔍 Validating intent specification..."
        )
        
        # Check URL health
        urls = state.current_intent_spec.target_urls_or_sites
        url_health_results = check_urls_health_sync(urls)
        
        # Update the intent spec with URL health results
        updated_spec = state.current_intent_spec.model_copy(deep=True)
        updated_spec.url_health_status = url_health_results
        
        # Add URL health results to messages
        url_messages = ["URL Health Check Results:"]
        for url, status in url_health_results.items():
            status_emoji = "✅" if status == "healthy" else "❓" if status == "unknown" else "❌"
            url_messages.append(f"- {url}: {status} {status_emoji}")
        
        key_messages = add_system_message(
            key_messages,
            "\n".join(url_messages)
        )
        
        # Initialize validation chain
        validation_chain = ValidationChain(llm)
        
        # Run validation
        validation_result = validation_chain.run(
            user_query=state.context.user_query,
            intent_spec=updated_spec,
            url_health_results=url_health_results
        )
        
        # Add validation result to messages
        if validation_result.is_valid:
            validation_message = "✅ Intent specification is valid!"
        else:
            validation_message = "❌ Intent specification validation failed with issues:"
            for issue in validation_result.issues:
                validation_message += f"\n- {issue}"
        
        key_messages = add_assistant_message(
            key_messages,
            validation_message,
            metadata={"validation_result": validation_result.model_dump()}
        )
        
        # Return updated state
        return {
            "state": GraphState(
                context=state.context,
                current_intent_spec=updated_spec,
                validation_result=validation_result,
                key_messages=key_messages
            )
        }
    
    except Exception as e:
        # Handle errors
        error_message = f"Error validating intent: {str(e)}"
        key_messages = add_system_message(key_messages, f"❌ {error_message}")
        
        return {
            "state": GraphState(
                context=state.context,
                current_intent_spec=state.current_intent_spec,
                error_message=error_message,
                key_messages=key_messages
            )
        }


def revise_with_critique(state: GraphState) -> Dict[str, Any]:
    """
    Update context with critique information.
    
    Args:
        state: Current graph state
        
    Returns:
        Updated graph state with critique hints
    """
    key_messages = state.key_messages
    
    # Check if we have validation results
    if state.validation_result is None:
        error_message = "Cannot revise without validation results"
        key_messages = add_system_message(key_messages, f"❌ {error_message}")
        
        return {
            "state": GraphState(
                context=state.context,
                current_intent_spec=state.current_intent_spec,
                error_message=error_message,
                key_messages=key_messages
            )
        }
    
    # Extract critique hints from validation issues
    critique_hints = state.validation_result.issues
    
    # Update context with critique hints
    updated_context = state.context.add_critique_hints(critique_hints)
    updated_context = updated_context.increment_iteration()
    
    # Add system message about revision
    key_messages = add_system_message(
        key_messages,
        f"🔄 Revising intent based on {len(critique_hints)} critique points (iteration {updated_context.iteration_count})"
    )
    
    # Return updated state
    return {
        "state": GraphState(
            context=updated_context,
            current_intent_spec=state.current_intent_spec,
            validation_result=state.validation_result,
            key_messages=key_messages
        )
    }
