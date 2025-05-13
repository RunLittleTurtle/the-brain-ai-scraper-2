"""
Intent processing subgraph for the intent inference workflow.

This module implements the LangGraph subgraph for processing user input
as a new intent using LLM-based processing.
"""
import logging
from typing import Dict, Any, TypedDict, Optional, List

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from pydantic import BaseModel

from langgraph.graph import StateGraph, START, END

from ...models.intent_spec import IntentSpec, LLMIntentSpecSchema
from ...models.context import ContextStore, GraphState
from ...utils.chain_helpers import get_llm
from ...chains.intent_chain import convert_to_intent_spec, parse_llm_output
from ...prompts.intent_prompts import intent_extraction_prompt, intent_with_context_prompt

# Configure module logger
logger = logging.getLogger(__name__)


def intent_prompt_template(state: GraphState) -> Dict[str, Any]:
    """
    Create a formatted prompt for intent extraction based on context.
    
    Args:
        state: Current graph state containing context
        
    Returns:
        Updated state with formatted prompt
    """
    context = state.get("context", ContextStore())
    user_query = context.user_query or ""
    critique_hints = context.critique_hints or []
    
    # Choose which prompt to use based on whether we have critique hints
    if critique_hints:
        prompt = intent_with_context_prompt
        formatted_prompt = prompt.format(
            user_query=user_query,
            critique_hints="\n".join([f"- {hint}" for hint in critique_hints])
        )
    else:
        prompt = intent_extraction_prompt
        formatted_prompt = prompt.format(user_query=user_query)
    
    # Return the formatted prompt
    return {"intent_prompt": formatted_prompt}


def intent_llm_call(state: GraphState) -> Dict[str, Any]:
    """
    Call the LLM with the intent extraction prompt.
    
    Args:
        state: Current graph state containing formatted prompt
        
    Returns:
        Updated state with LLM response
    """
    prompt = state.get("intent_prompt", "")
    if not prompt:
        logger.warning("No prompt found in state for LLM call")
        return {"intent_llm_output": ""}
        
    # Get the LLM
    llm = get_llm()
    
    # Call the LLM
    response = llm.invoke(prompt)
    
    # Extract the content
    content = response.content if hasattr(response, "content") else str(response)
    
    return {"intent_llm_output": content}


def intent_output_parser(state: GraphState) -> Dict[str, Any]:
    """
    Parse the LLM output into a structured LLMIntentSpecSchema.
    
    Args:
        state: Current graph state containing LLM output
        
    Returns:
        Updated state with parsed intent spec
    """
    llm_output = state.get("intent_llm_output", "")
    if not llm_output:
        logger.warning("No LLM output found in state for parsing")
        return {"intent_output": {}}

    # Parse the LLM output
    try:
        # Parse into the LLMIntentSpecSchema format
        parsed_output = parse_llm_output(llm_output)
        return {"intent_output": parsed_output}
    except Exception as e:
        logger.exception(f"Error parsing LLM output: {e}")
        return {"intent_output": {}, "parsing_error": str(e)}


def create_intent_processing_subgraph() -> StateGraph:
    """
    Create the intent processing subgraph for visualization in nested format.
    
    This subgraph contains the nodes required for intent extraction from
    user queries using LLM-based processing.
    
    Returns:
        Compiled LangGraph StateGraph for intent processing
    """
    # Create a typed dict for this subgraph's state
    class IntentProcessingState(TypedDict):
        context: Optional[ContextStore]
        intent_prompt: str
        intent_llm_output: str
        intent_output: Dict[str, Any]
    
    # Create the subgraph
    subgraph = StateGraph(IntentProcessingState)
    
    # Add the nodes to the subgraph in the specific order for visualization
    subgraph.add_node("intent_prompt_template", intent_prompt_template)
    subgraph.add_node("intent_llm_call", intent_llm_call)
    subgraph.add_node("intent_output_parser", intent_output_parser)
    
    # Define the edges to create a linear flow
    subgraph.add_edge("intent_prompt_template", "intent_llm_call")
    subgraph.add_edge("intent_llm_call", "intent_output_parser")
    
    # Set entry and finish points
    subgraph.set_entry_point("intent_prompt_template")
    subgraph.set_finish_point("intent_output_parser")
    
    # Compile the subgraph
    return subgraph.compile()


def process_new_intent(state: GraphState) -> Dict[str, Any]:
    """
    Process user input as a new intent request.
    
    This function serves as an entry point for the intent processing
    subgraph and manages transformation between parent and child states.
    
    Args:
        state: Current graph state
        
    Returns:
        Updated graph state with intent processing results
    """
    # Create and invoke the intent processing subgraph
    subgraph = create_intent_processing_subgraph()
    
    # Initialize the subgraph state from the parent state
    context = state.get("context", ContextStore())
    
    # Create the input state for the subgraph
    subgraph_input = {
        "context": context,
        "intent_prompt": "",
        "intent_llm_output": "",
        "intent_output": {}
    }
    
    # Invoke the subgraph
    try:
        result = subgraph.invoke(subgraph_input)
        
        # Extract the results from the subgraph
        intent_output = result.get("intent_output", {})
        
        # Return the updated state
        return {"intent_output": intent_output}
    except Exception as e:
        logger.exception(f"Error invoking intent processing subgraph: {e}")
        return {"intent_output": {}, "error": str(e)}
