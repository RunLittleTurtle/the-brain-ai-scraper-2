"""
Intent processing nodes for intent inference graph.

This module provides nodes for processing new intents in the graph.
"""
from typing import Dict, Any, List, Optional, cast

from langchain_core.language_models import BaseChatModel

from intent_inference.graph.state import GraphState, IntentSpec
from intent_inference.graph.chains.intent_chain import IntentChain
from intent_inference.utils.visualization import add_user_message, add_assistant_message, format_intent_spec_for_display


def process_new_intent(state: GraphState, llm: BaseChatModel) -> Dict[str, Any]:
    """
    Process a new intent using the IntentChain.
    
    Args:
        state: Current graph state
        llm: Language model to use for processing
        
    Returns:
        Updated graph state
    """
    # Add user message to visualization
    key_messages = add_user_message(
        state.key_messages, 
        f"🔍 Intent to extract: {state.context.user_query}"
    )
    
    # Initialize the intent chain
    intent_chain = IntentChain(llm)
    
    try:
        # Extract intent from user query
        llm_output = intent_chain.run(state.context.user_query)
        
        # Create intent spec from LLM output
        intent_spec = IntentSpec.create_new(
            user_query=state.context.user_query,
            target_urls_or_sites=llm_output.target_urls_or_sites,
            data_to_extract=llm_output.data_to_extract,
            constraints=llm_output.constraints
        )
        
        # Add assistant message to visualization
        key_messages = add_assistant_message(
            key_messages,
            f"📋 Extracted Intent:\n\n{format_intent_spec_for_display(intent_spec)}",
            metadata={"spec_id": intent_spec.spec_id}
        )
        
        # Update the context with the last spec
        updated_context = state.context.update_last_spec(intent_spec)
        
        # Return updated state
        return {
            "state": GraphState(
                context=updated_context,
                current_intent_spec=intent_spec,
                key_messages=key_messages
            )
        }
    
    except Exception as e:
        # Handle errors
        error_message = f"Error processing intent: {str(e)}"
        key_messages = add_assistant_message(key_messages, f"❌ {error_message}")
        
        return {
            "state": GraphState(
                context=state.context,
                error_message=error_message,
                key_messages=key_messages
            )
        }
