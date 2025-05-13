"""
Feedback processing subgraph for the intent inference workflow.

This module implements the LangGraph subgraph for processing user feedback
to refine existing intent specifications.
"""
import logging
from typing import Dict, Any, TypedDict, Optional, List

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from pydantic import BaseModel

from langgraph.graph import StateGraph, START, END

from ...models.intent_spec import IntentSpec, LLMFeedbackSchema
from ...models.context import ContextStore, GraphState
from ...utils.chain_helpers import get_llm
from ...chains.feedback_chain import apply_feedback_to_spec, parse_feedback_output
from ...prompts.feedback_prompts import feedback_prompt

# Configure module logger
logger = logging.getLogger(__name__)


def feedback_prompt_template(state: GraphState) -> Dict[str, Any]:
    """
    Create a formatted prompt for feedback processing based on context.
    
    Args:
        state: Current graph state containing context and previous spec
        
    Returns:
        Updated state with formatted prompt
    """
    context = state.get("context", ContextStore())
    user_query = context.user_query or ""
    last_spec = context.last_spec
    
    if not last_spec:
        logger.warning("No previous intent spec found for feedback processing")
        return {"feedback_prompt": ""}
        
    # Format the prompt
    formatted_prompt = feedback_prompt.format(
        user_feedback=user_query,
        current_spec=last_spec.model_dump_json(indent=2)
    )
    
    # Return the formatted prompt
    return {"feedback_prompt": formatted_prompt}


def feedback_llm_call(state: GraphState) -> Dict[str, Any]:
    """
    Call the LLM with the feedback processing prompt.
    
    Args:
        state: Current graph state containing formatted prompt
        
    Returns:
        Updated state with LLM response
    """
    prompt = state.get("feedback_prompt", "")
    if not prompt:
        logger.warning("No prompt found in state for feedback LLM call")
        return {"feedback_llm_output": ""}
        
    # Get the LLM
    llm = get_llm()
    
    # Call the LLM
    response = llm.invoke(prompt)
    
    # Extract the content
    content = response.content if hasattr(response, "content") else str(response)
    
    return {"feedback_llm_output": content}


def feedback_output_parser(state: GraphState) -> Dict[str, Any]:
    """
    Parse the LLM output into a structured LLMFeedbackSchema.
    
    Args:
        state: Current graph state containing LLM output
        
    Returns:
        Updated state with parsed feedback
    """
    llm_output = state.get("feedback_llm_output", "")
    if not llm_output:
        logger.warning("No LLM output found in state for feedback parsing")
        return {"feedback_output": {}}

    # Parse the LLM output
    try:
        # Parse into the LLMFeedbackSchema format
        parsed_output = parse_feedback_output(llm_output)
        return {"feedback_output": parsed_output}
    except Exception as e:
        logger.exception(f"Error parsing feedback LLM output: {e}")
        return {"feedback_output": {}, "parsing_error": str(e)}


def create_feedback_processing_subgraph() -> StateGraph:
    """
    Create the feedback processing subgraph for visualization in nested format.
    
    This subgraph contains the nodes required for processing user feedback
    to update existing intent specifications.
    
    Returns:
        Compiled LangGraph StateGraph for feedback processing
    """
    # Create a typed dict for this subgraph's state
    class FeedbackProcessingState(TypedDict):
        context: Optional[ContextStore]
        feedback_prompt: str
        feedback_llm_output: str
        feedback_output: Dict[str, Any]
    
    # Create the subgraph
    subgraph = StateGraph(FeedbackProcessingState)
    
    # Add the nodes to the subgraph in the specific order for visualization
    subgraph.add_node("feedback_prompt_template", feedback_prompt_template)
    subgraph.add_node("feedback_llm_call", feedback_llm_call)
    subgraph.add_node("feedback_output_parser", feedback_output_parser)
    
    # Define the edges to create a linear flow
    subgraph.add_edge("feedback_prompt_template", "feedback_llm_call")
    subgraph.add_edge("feedback_llm_call", "feedback_output_parser")
    
    # Set entry and finish points
    subgraph.set_entry_point("feedback_prompt_template")
    subgraph.set_finish_point("feedback_output_parser")
    
    # Compile the subgraph
    return subgraph.compile()


def process_feedback(state: GraphState) -> Dict[str, Any]:
    """
    Process user input as feedback for an existing intent specification.
    
    This function serves as an entry point for the feedback processing
    subgraph and manages transformation between parent and child states.
    
    Args:
        state: Current graph state
        
    Returns:
        Updated graph state with feedback processing results
    """
    # Create and invoke the feedback processing subgraph
    subgraph = create_feedback_processing_subgraph()
    
    # Initialize the subgraph state from the parent state
    context = state.get("context", ContextStore())
    
    # Create the input state for the subgraph
    subgraph_input = {
        "context": context,
        "feedback_prompt": "",
        "feedback_llm_output": "",
        "feedback_output": {}
    }
    
    # Invoke the subgraph
    try:
        result = subgraph.invoke(subgraph_input)
        
        # Extract the results from the subgraph
        feedback_output = result.get("feedback_output", {})
        
        # Return the updated state
        return {"feedback_output": feedback_output}
    except Exception as e:
        logger.exception(f"Error invoking feedback processing subgraph: {e}")
        return {"feedback_output": {}, "error": str(e)}
