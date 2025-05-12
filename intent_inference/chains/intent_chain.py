"""
Intent extraction chain for the intent inference module.

This module implements the LangChain-based chain for extracting structured intent
specifications from natural language user queries.
"""
from typing import Dict, Any, List, Optional
import json
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from pydantic import BaseModel, Field

from ..models.intent_spec import IntentSpec, ExtractedField
from ..prompts.intent_prompts import intent_extraction_prompt, intent_with_context_prompt
from ..utils.chain_helpers import get_llm


class LLMIntentSpec(BaseModel):
    """Model for the structured output from the intent extraction LLM chain."""
    
    target_urls_or_sites: List[str] = Field(
        ..., 
        description="Target websites or URLs to scrape from"
    )
    data_to_extract: List[Dict[str, str]] = Field(
        ..., 
        description="Data fields to extract with their descriptions"
    )
    constraints: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Additional constraints on the scraping operation"
    )


def parse_llm_output(llm_output: str) -> Dict[str, Any]:
    """
    Parse the raw LLM output string into a structured dictionary.
    
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
        raise ValueError(f"Failed to parse LLM output as JSON: {e}. Output was: {llm_output}")


def create_intent_extraction_chain(use_context: bool = False):
    """
    Create an intent extraction chain that transforms natural language to structured specs.
    
    Args:
        use_context: Whether to use the context-aware prompt with critique hints
        
    Returns:
        A runnable chain that extracts intent from user queries
    """
    # Select the appropriate prompt template
    prompt = intent_with_context_prompt if use_context else intent_extraction_prompt
    
    # Create the chain
    chain = (
        prompt
        | get_llm()
        | StrOutputParser()
        | parse_llm_output
    )
    
    return chain


def convert_to_intent_spec(
    output: Dict[str, Any], 
    user_query: str,
    existing_spec: Optional[IntentSpec] = None
) -> IntentSpec:
    """
    Convert the parsed LLM output into a complete IntentSpec.
    
    Args:
        output: Parsed output from the LLM
        user_query: Original user query
        existing_spec: Optional existing spec for revisions
        
    Returns:
        Complete IntentSpec instance
    """
    # Create ExtractedField objects from the data_to_extract dicts
    extracted_fields = [
        ExtractedField(
            field_name=field["field_name"],
            description=field["description"]
        )
        for field in output["data_to_extract"]
    ]
    
    # Create the IntentSpec with a new ID if it's a new spec, or update the existing one
    if existing_spec:
        spec = existing_spec.model_copy(deep=True)
        
        # Update the fields that may have changed
        spec.target_urls_or_sites = output["target_urls_or_sites"]
        spec.data_to_extract = extracted_fields
        spec.constraints = output["constraints"]
        
        # Add revision indicator to spec_id if not already present
        if "_rev" not in spec.spec_id:
            spec.spec_id = f"{spec.spec_id}_rev1"
    else:
        # Create a brand new spec
        spec = IntentSpec(
            original_user_query=user_query,
            target_urls_or_sites=output["target_urls_or_sites"],
            data_to_extract=extracted_fields,
            constraints=output["constraints"]
        )
    
    return spec
