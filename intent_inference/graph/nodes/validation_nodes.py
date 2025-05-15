"""
Nodes for validating intent specifications.

This module provides the validate_intent node which checks intent specifications
for validity, completeness, and URL health.
"""
from typing import Any, Dict, List
import os
from pathlib import Path

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI

from intent_inference.state import ValidationStatus, ValidationResult, Message
from intent_inference.graph.state import GraphState
from intent_inference.graph.tools.url_health import check_urls_health_sync


def load_prompt_template(file_name: str) -> str:
    """Load a prompt template from the prompts directory."""
    prompt_dir = Path(__file__).parents[2] / "prompts"
    prompt_path = prompt_dir / file_name
    
    if not prompt_path.exists():
        # For development, return a simple template if file doesn't exist yet
        return "You are an AI validator that checks intent specifications for completeness and validity.\n\nIntent specification: {intent_spec}\nURL health results: {url_health_results}\n\n{format_instructions}"
    
    with open(prompt_path, "r") as f:
        return f.read()


def validate_intent(state: GraphState, llm: Any = None) -> GraphState:
    """
    Validate an intent specification for completeness, validity, and URL health.
    
    Args:
        state: The current graph state
        llm: Optional LLM instance (will use OpenAI if not provided)
    
    Returns:
        Updated graph state with validation results
    """
    # Create a copy of the state to avoid mutations
    state = state.model_copy(deep=True)
    
    # Check if there is an intent spec to validate
    if not state.current_intent_spec:
        state.error_message = "No intent specification to validate"
        state.messages.append(Message(
            role="system",
            content="⚠️ Error: No intent specification available for validation"
        ))
        
        # Create a failed validation result
        state.validation_result = ValidationResult(
            is_valid=False,
            status=ValidationStatus.INVALID,
            issues=["No intent specification available for validation"]
        )
        return state
    
    # Add system message for visualization
    state.messages.append(Message(
        role="system",
        content="Validating intent specification..."
    ))
    
    # Check URL health first
    urls = state.current_intent_spec.target_urls_or_sites
    url_health_results = check_urls_health_sync(urls)
    
    # Update the URL health status in the intent spec
    for url, status in url_health_results.items():
        state.current_intent_spec.url_health_status[url] = status
    
    # Count how many URLs are healthy
    healthy_urls = sum(1 for status in url_health_results.values() if status == "healthy")
    
    # If no URLs are healthy, create a failed validation result
    if not urls or (urls and healthy_urls == 0):
        state.validation_result = ValidationResult(
            is_valid=False,
            status=ValidationStatus.INVALID,
            issues=["None of the provided URLs are accessible"]
        )
        
        state.messages.append(Message(
            role="system",
            content="⚠️ Validation failed: None of the provided URLs are accessible"
        ))
        return state
    
    # Initialize the LLM if not provided
    if llm is None:
        model_name = os.getenv("OPENAI_MODEL_NAME", "gpt-4o")
        llm = ChatOpenAI(model_name=model_name, temperature=0.0)
    
    # Create a parser that expects ValidationResult fields
    parser = JsonOutputParser(pydantic_object=dict)
    
    # Load and format the validation prompt
    prompt_template = load_prompt_template("validation_prompt.txt")
    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["intent_spec", "url_health_results"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    
    # Format the intent spec for the prompt
    intent_spec_str = (
        f"User Query: {state.current_intent_spec.original_user_query}\n"
        f"Target URLs/Sites: {', '.join(state.current_intent_spec.target_urls_or_sites)}\n"
        f"Data Fields: {', '.join(f.field_name + ' (' + f.description + ')' for f in state.current_intent_spec.data_to_extract)}\n"
        f"Constraints: {state.current_intent_spec.constraints}"
    )
    
    # Format URL health results for the prompt
    url_health_str = "\n".join([f"- {url}: {status}" for url, status in url_health_results.items()])
    
    # Create the validation chain
    chain = (
        {
            "intent_spec": lambda _: intent_spec_str,
            "url_health_results": lambda _: url_health_str
        }
        | prompt
        | llm
        | parser
    )
    
    try:
        # Run the validation chain
        result = chain.invoke({})
        
        # Process the validation results
        is_valid = result.get("is_valid", False)
        issues = result.get("issues", [])
        
        # Create a validation result
        validation_result = ValidationResult(
            is_valid=is_valid,
            status=ValidationStatus.VALID if is_valid else ValidationStatus.INVALID,
            issues=issues
        )
        
        # Store the validation result in the state
        state.validation_result = validation_result
        
        # Add validation result message for visualization
        if is_valid:
            state.messages.append(Message(
                role="assistant",
                content="✅ Intent specification is valid and ready for human review."
            ))
        else:
            issues_str = "\n".join([f"- {issue}" for issue in issues])
            state.messages.append(Message(
                role="assistant",
                content=f"❌ Intent specification needs revision:\n\n{issues_str}"
            ))
    
    except Exception as e:
        # Handle errors
        state.error_message = f"Error validating intent: {str(e)}"
        state.messages.append(Message(
            role="system",
            content=f"⚠️ Error during validation: {str(e)}"
        ))
        
        # Create a failed validation result
        state.validation_result = ValidationResult(
            is_valid=False,
            status=ValidationStatus.INVALID,
            issues=[f"Validation error: {str(e)}"]
        )
    
    return state
