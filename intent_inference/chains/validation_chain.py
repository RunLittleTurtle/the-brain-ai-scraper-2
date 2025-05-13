"""
Validation chain for the intent inference module.

This module implements the LangChain-based chain for validating intent specifications
using an LLM as a judge.
"""
import logging
from typing import Dict, Any, List, Tuple, Optional
from langchain_core.output_parsers import StrOutputParser, PydanticOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from pydantic import BaseModel, Field

from ..models.intent_spec import IntentSpec
from ..prompts.validation_prompts import validation_prompt
from ..utils.chain_helpers import get_llm, call_llm_with_retry
from ..utils.url_validator import validate_urls
from ..utils.parsing import parse_json_from_llm_output

# Configure module logger
logger = logging.getLogger(__name__)


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
    This function is kept for backward compatibility and now uses the centralized parser.
    
    Args:
        llm_output: Raw string output from the LLM
        
    Returns:
        Parsed dictionary from the JSON output
        
    Raises:
        ValueError: If parsing fails
    """
    return parse_json_from_llm_output(llm_output, "validation output")


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
    
    # Create a Pydantic parser for the output
    parser = PydanticOutputParser(pydantic_object=ValidationResult)
    
    # Use string parser as fallback if structured parsing fails
    def parse_with_fallback(llm_output: str) -> Dict[str, Any]:
        try:
            # Try to parse as Pydantic model first
            return parser.parse(llm_output).model_dump()
        except Exception as e:
            logger.warning(f"Pydantic parsing failed: {e}. Falling back to raw JSON parsing.")
            # Fall back to manual JSON parsing
            return parse_json_from_llm_output(llm_output, "validation output")
    
    # Create the LLM validation chain
    llm_validation_chain = (
        RunnableLambda(_format_input_for_validation)
        | validation_prompt
        | get_llm()
        | StrOutputParser()
        | parse_with_fallback
    )
    
    return llm_validation_chain


async def validate_intent_with_retry(spec: IntentSpec) -> Dict[str, Any]:
    """
    Validate an intent specification using LLM-as-Judge with retry logic.
    
    Args:
        spec: Intent specification to validate
        
    Returns:
        Validation result as a dictionary
    """
    logger.info(f"Validating intent spec {spec.spec_id} with LLM-as-Judge")
    
    # Format the input for the validation prompt
    formatted_input = {
        "original_query": spec.original_user_query,
        "intent_spec": spec.model_dump_json(indent=2)
    }
    
    # Call LLM with retry
    llm_output = await call_llm_with_retry(get_llm(), validation_prompt, formatted_input)
    
    # Parse the output
    return parse_json_from_llm_output(llm_output, "validation output")


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
    logger.info(f"Validating spec {spec.spec_id}")
    
    # Create a deep copy of the spec to avoid modifying the original
    updated_spec = spec.model_copy(deep=True)
    
    # First, perform URL health checks if requested
    url_issues = []
    if check_urls:
        try:
            updated_spec, url_health = await check_and_update_urls(updated_spec)
            
            # Check for URL health issues
            for url, status in url_health.items():
                if status != "healthy":
                    issue = f"URL issue: {url} is {status}"
                    url_issues.append(issue)
                    logger.warning(issue)
        except Exception as e:
            logger.error(f"Error checking URL health: {e}")
            url_issues.append(f"URL checking error: {str(e)}")
    
    # Run the LLM validation with retry
    try:
        validation_result = await validate_intent_with_retry(updated_spec)
        validation_obj = ValidationResult(**validation_result)
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        # Create a default validation result for error case
        validation_obj = ValidationResult(
            is_valid=False,
            issues=[f"Validation error: {str(e)}"],
            clarification_needed=True,
            clarification_questions=["Could you provide more details? The system encountered an error."],
            reasoning="Error during validation process"
        )
    
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
    
    logger.info(f"Validation complete: valid={validation_obj.is_valid and not url_issues}, issues={len(all_issues)}")
    
    return (
        updated_spec, 
        validation_obj.is_valid and not url_issues, 
        all_issues,
        validation_obj.clarification_questions if validation_obj.clarification_needed else None
    )
