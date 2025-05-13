"""
Parsing utilities for LLM outputs.

This module provides helper functions for parsing structured outputs from LLMs,
with robust error handling and consistent formatting.
"""
from typing import Dict, Any
import json
import logging

# Configure module logger
logger = logging.getLogger(__name__)


def parse_json_from_llm_output(llm_output: str, error_context: str = "output") -> Dict[str, Any]:
    """
    Parse the raw LLM output string into a structured dictionary.
    
    Args:
        llm_output: Raw string output from the LLM
        error_context: Context for error messages (e.g., "validation output")
        
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
        logger.debug(f"Parsing JSON from LLM {error_context}")
        return json.loads(cleaned_output.strip())
    except (json.JSONDecodeError, ValueError) as e:
        error_msg = f"Failed to parse {error_context} as JSON: {e}. Output was: {llm_output}"
        logger.error(error_msg)
        raise ValueError(error_msg)

from typing import TypeVar, Callable, Optional, Type, Generic, Dict, Any
from pydantic import BaseModel, ValidationError

T = TypeVar('T', bound=BaseModel)

def parse_llm_json_response(
    response: str, 
    model_class: Type[T], 
    fallback_func: Optional[Callable[[str], T]] = None
) -> Optional[T]:
    """
    Parse LLM response into a Pydantic model with robust error handling.
    
    Args:
        response: Raw string response from the LLM
        model_class: The Pydantic model class to parse into
        fallback_func: Optional function to call if parsing fails
        
    Returns:
        Instance of the specified model class, or None if parsing fails and no fallback is provided
    """
    try:
        # First parse the JSON
        parsed_json = parse_json_from_llm_output(response)
        
        # Then convert to the model
        return model_class.model_validate(parsed_json)
    except (ValueError, ValidationError) as e:
        logger.warning(f"Failed to parse LLM response into {model_class.__name__}: {e}")
        
        # Try fallback if provided
        if fallback_func:
            logger.info(f"Using fallback function for {model_class.__name__}")
            try:
                return fallback_func(response)
            except Exception as fallback_error:
                logger.error(f"Fallback function also failed: {fallback_error}")
        
        # No fallback or fallback failed
        return None
