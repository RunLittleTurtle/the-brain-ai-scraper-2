"""
Validation chain for the intent inference module.

This module implements the LangChain-based chain for validating intent specifications
using an LLM as a judge.
"""
from typing import Dict, Any, List, Tuple, Optional
import json
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from pydantic import BaseModel, Field

from ..models.intent_spec import IntentSpec
from ..prompts.validation_prompts import validation_prompt
from ..utils.chain_helpers import get_llm
from ..utils.url_validator import validate_urls


class ValidationResult(BaseModel):
    """Model for the structured output from the validation LLM chain."""
    
    is_valid: bool = Field(
        ..., 
        description="Whether the specification is valid"
    )
    issues: List[str] = Field(
        default_factory=list, 
        description="Specific issues found with the specification"
    )
    clarification_needed: bool = Field(
        default=False, 
        description="Whether clarification is needed from the user"
    )
    clarification_questions: List[str] = Field(
        default_factory=list, 
        description="Specific questions to ask the user"
    )
    reasoning: str = Field(
        ..., 
        description="Explanation of the validation result"
    )


def parse_validation_output(llm_output: str) -> Dict[str, Any]:
    """
    Parse the raw LLM output string from the validation chain into a structured dictionary.
    
    Args:
        llm_output: Raw string output from the LLM
        
    Returns:
        Parsed dictionary from the JSON output
        
    Raises:
        ValueError: If parsing fails
    """
    try:
        # Remove any markdown code block indicators if present
        cleaned_output = llm_output.strip()
        if cleaned_output.startswith("```json"):
            cleaned_output = cleaned_output[7:]
        if cleaned_output.startswith("```"):
            cleaned_output = cleaned_output[3:]
        if cleaned_output.endswith("```"):
            cleaned_output = cleaned_output[:-3]
            
        # Parse the JSON
        return json.loads(cleaned_output.strip())
    except (json.JSONDecodeError, ValueError) as e:
        raise ValueError(f"Failed to parse validation output as JSON: {e}. Output was: {llm_output}")


async def check_and_update_urls(spec: IntentSpec) -> Tuple[IntentSpec, Dict[str, str]]:
    """
    Check the health of URLs in the intent specification and update the spec.
    
    Args:
        spec: Intent specification to validate
        
    Returns:
        Tuple of (updated spec, health status dict)
    """
    # Validate URLs concurrently
    url_health = await validate_urls(spec.target_urls_or_sites)
    
    # Update the spec with the health status
    updated_spec = spec.model_copy(deep=True)
    updated_spec.url_health_status = url_health
    
    return updated_spec, url_health


def create_validation_chain():
    """
    Create a validation chain using LLM-as-Judge to validate intent specifications.
    
    Returns:
        A runnable chain that validates intent specifications
    """
    # Format the input for the validation prompt
    def _format_input_for_validation(inputs: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "original_query": inputs["spec"].original_user_query,
            "intent_spec": inputs["spec"].model_dump_json(indent=2)
        }
    
    # Create the LLM validation chain
    llm_validation_chain = (
        RunnableLambda(_format_input_for_validation)
        | validation_prompt
        | get_llm()
        | StrOutputParser()
        | parse_validation_output
    )
    
    return llm_validation_chain


async def validate_intent_spec(
    spec: IntentSpec, 
    check_urls: bool = True
) -> Tuple[IntentSpec, bool, List[str], Optional[List[str]]]:
    """
    Validate an intent specification using LLM-as-Judge and URL health checks.
    
    Args:
        spec: Intent specification to validate
        check_urls: Whether to perform URL health checks
        
    Returns:
        Tuple of (updated spec, is_valid, issues, clarification_questions)
    """
    # Create a deep copy of the spec to avoid modifying the original
    updated_spec = spec.model_copy(deep=True)
    
    # First, perform URL health checks if requested
    url_issues = []
    if check_urls:
        updated_spec, url_health = await check_and_update_urls(updated_spec)
        
        # Check for URL health issues
        for url, status in url_health.items():
            if status != "healthy":
                url_issues.append(f"URL issue: {url} is {status}")
    
    # Run the LLM validation chain
    validation_chain = create_validation_chain()
    validation_result = await validation_chain.ainvoke({"spec": updated_spec})
    
    # Process the validation result
    validation_obj = ValidationResult(**validation_result)
    
    # Combine LLM validation issues with URL issues
    all_issues = validation_obj.issues + url_issues
    
    # Update the spec with validation results
    updated_spec.validation_status = "validated_by_llm_judge" if validation_obj.is_valid and not url_issues else "needs_revision"
    
    # Add any critique points to the history
    if not validation_obj.is_valid or url_issues:
        if not updated_spec.critique_history:
            updated_spec.critique_history = []
        
        for issue in all_issues:
            updated_spec.critique_history.append(issue)
    
    # Add clarification questions if needed
    if validation_obj.clarification_needed and validation_obj.clarification_questions:
        updated_spec.clarification_questions_for_user = validation_obj.clarification_questions
    
    return (
        updated_spec, 
        validation_obj.is_valid and not url_issues, 
        all_issues,
        validation_obj.clarification_questions if validation_obj.clarification_needed else None
    )
