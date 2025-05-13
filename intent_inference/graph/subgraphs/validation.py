"""
Validation subgraph for the intent inference workflow.

This module implements the LangGraph subgraph for validating intent specifications
and performing URL health checks.
"""
import logging
import requests
from typing import Dict, Any, TypedDict, Optional, List, Literal

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from pydantic import BaseModel

from langgraph.graph import StateGraph, START, END

from ...models.intent_spec import IntentSpec
from ...models.context import ContextStore, GraphState
from ...utils.chain_helpers import get_llm
from ...chains.validation_chain import validate_intent_spec, process_validation_result
from ...prompts.validation_prompts import intent_validation_prompt

# Configure module logger
logger = logging.getLogger(__name__)


def judge_prompt_creation(state: GraphState) -> Dict[str, Any]:
    """
    Create a prompt for the LLM-as-judge to validate the intent specification.
    
    Args:
        state: Current graph state containing intent spec
        
    Returns:
        Updated state with validation prompt
    """
    # Get the intent spec to validate
    intent_spec = state.get("intent_spec")
    if not intent_spec:
        logger.warning("No intent spec found for validation")
        return {"validation_prompt": ""}
    
    # Format the validation prompt
    formatted_prompt = intent_validation_prompt.format(
        intent_spec=intent_spec.model_dump_json(indent=2)
    )
    
    return {"validation_prompt": formatted_prompt}


def judge_llm_call(state: GraphState) -> Dict[str, Any]:
    """
    Call the LLM with the validation prompt to judge the intent specification.
    
    Args:
        state: Current graph state containing validation prompt
        
    Returns:
        Updated state with LLM validation response
    """
    prompt = state.get("validation_prompt", "")
    if not prompt:
        logger.warning("No prompt found in state for validation LLM call")
        return {"validation_llm_output": ""}
        
    # Get the LLM
    llm = get_llm()
    
    # Call the LLM
    response = llm.invoke(prompt)
    
    # Extract the content
    content = response.content if hasattr(response, "content") else str(response)
    
    return {"validation_llm_output": content}


def judge_output_parser(state: GraphState) -> Dict[str, Any]:
    """
    Parse the LLM validation output to determine if intent spec is valid.
    
    Args:
        state: Current graph state containing LLM validation output
        
    Returns:
        Updated state with parsed validation result
    """
    llm_output = state.get("validation_llm_output", "")
    if not llm_output:
        logger.warning("No LLM output found in state for validation parsing")
        return {"validation_result": {"is_valid": False, "issues": ["No validation response received"]}}

    # Parse the validation result
    try:
        validation_result = process_validation_result(llm_output)
        return {"validation_result": validation_result}
    except Exception as e:
        logger.exception(f"Error parsing validation output: {e}")
        return {"validation_result": {"is_valid": False, "issues": [f"Error: {str(e)}"]}}


def check_url_health(state: GraphState) -> Dict[str, Any]:
    """
    Check the health of URLs in the intent specification.
    
    Args:
        state: Current graph state containing intent specification
        
    Returns:
        Updated state with URL health status
    """
    intent_spec = state.get("intent_spec")
    if not intent_spec:
        logger.warning("No intent spec found for URL health check")
        return {"url_health_status": {"all_urls_healthy": False, "failed_urls": []}}
    
    # Extract target URLs
    urls = getattr(intent_spec, "target_urls", [])
    if not urls:
        logger.info("No URLs found in intent spec for health check")
        return {"url_health_status": {"all_urls_healthy": True, "failed_urls": []}}
    
    # Check each URL
    failed_urls = []
    for url in urls:
        try:
            # Add http if not present
            if not url.startswith("http"):
                check_url = f"https://{url}"
            else:
                check_url = url
                
            # Try to access the URL
            response = requests.head(check_url, timeout=5)
            
            # Check if successful
            if response.status_code >= 400:
                failed_urls.append({"url": url, "status_code": response.status_code})
        except Exception as e:
            failed_urls.append({"url": url, "error": str(e)})
    
    # Return the health status
    health_status = {
        "all_urls_healthy": len(failed_urls) == 0,
        "failed_urls": failed_urls
    }
    
    return {"url_health_status": health_status}


def make_decision(state: GraphState) -> Literal["add_critique", "human_review", "error"]:
    """
    Decide whether to add critique or proceed to human review.
    
    Args:
        state: Current graph state with validation results
        
    Returns:
        Decision on next step: "add_critique" or "human_review"
    """
    validation_result = state.get("validation_result", {})
    url_health_status = state.get("url_health_status", {})
    
    # Check for serious errors
    if not validation_result or not url_health_status:
        logger.error("Missing validation or URL health results for decision making")
        return "error"
    
    # If validation fails or URLs are unhealthy, add critique
    is_valid = validation_result.get("is_valid", False)
    all_urls_healthy = url_health_status.get("all_urls_healthy", False)
    
    if not is_valid or not all_urls_healthy:
        return "add_critique"
    
    # If everything is valid, proceed to human review
    return "human_review"


def create_validation_subgraph() -> StateGraph:
    """
    Create the validation subgraph for visualization in nested format.
    
    This subgraph contains the nodes required for validating intent specifications
    and checking URL health.
    
    Returns:
        Compiled LangGraph StateGraph for validation
    """
    # Create a typed dict for this subgraph's state
    class ValidationState(TypedDict):
        intent_spec: Optional[IntentSpec]
        validation_prompt: str
        validation_llm_output: str
        validation_result: Dict[str, Any]
        url_health_status: Dict[str, Any]
    
    # Create the subgraph
    subgraph = StateGraph(ValidationState)
    
    # Add the nodes to the subgraph in the specific order for visualization
    subgraph.add_node("judge_prompt_creation", judge_prompt_creation)
    subgraph.add_node("judge_llm_call", judge_llm_call)
    subgraph.add_node("judge_output_parser", judge_output_parser)
    subgraph.add_node("check_url_health", check_url_health)
    
    # Define the edges to create a linear flow
    subgraph.add_edge("judge_prompt_creation", "judge_llm_call")
    subgraph.add_edge("judge_llm_call", "judge_output_parser")
    subgraph.add_edge("judge_output_parser", "check_url_health")
    
    # Set entry and finish points
    subgraph.set_entry_point("judge_prompt_creation")
    subgraph.set_finish_point("check_url_health")
    
    # Compile the subgraph
    return subgraph.compile()


def validate_intent(state: GraphState) -> Dict[str, Any]:
    """
    Validate the intent specification and check URL health.
    
    This function serves as an entry point for the validation
    subgraph and manages transformation between parent and child states.
    
    Args:
        state: Current graph state containing intent spec
        
    Returns:
        Updated graph state with validation results
    """
    # Get the intent spec to validate
    intent_spec = state.get("intent_spec")
    if not intent_spec:
        logger.warning("No intent spec found in state for validation")
        return {
            "validation_result": {"is_valid": False, "issues": ["No intent specification found"]},
            "url_health_status": {"all_urls_healthy": False, "failed_urls": []}
        }
    
    # Create and invoke the validation subgraph
    subgraph = create_validation_subgraph()
    
    # Create the input state for the subgraph
    subgraph_input = {
        "intent_spec": intent_spec,
        "validation_prompt": "",
        "validation_llm_output": "",
        "validation_result": {},
        "url_health_status": {}
    }
    
    # Invoke the subgraph
    try:
        result = subgraph.invoke(subgraph_input)
        
        # Extract the results from the subgraph
        validation_result = result.get("validation_result", {})
        url_health_status = result.get("url_health_status", {})
        
        # Return the updated state
        return {
            "validation_result": validation_result,
            "url_health_status": url_health_status
        }
    except Exception as e:
        logger.exception(f"Error invoking validation subgraph: {e}")
        return {
            "validation_result": {"is_valid": False, "issues": [f"Error in validation: {str(e)}"]},
            "url_health_status": {"all_urls_healthy": False, "failed_urls": []}
        }
