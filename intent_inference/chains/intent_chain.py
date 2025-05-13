"""
Intent extraction chain for the intent inference module.

This module implements the LangChain-based chain for extracting structured intent
specifications from natural language user queries.
"""
import logging
from typing import Dict, Any, List, Optional
from langchain_core.output_parsers import StrOutputParser, PydanticOutputParser
from langchain_core.runnables import RunnablePassthrough
from pydantic import BaseModel, Field

from models.intent.intent_spec import IntentSpec, FieldToExtract
from ..prompts.intent_prompts import intent_extraction_prompt, intent_with_context_prompt
from ..utils.chain_helpers import get_llm, call_llm_with_retry
from ..utils.parsing import parse_json_from_llm_output

# Configure module logger
logger = logging.getLogger(__name__)


class LLMIntentSpec(BaseModel):
    """Model for the structured output from the intent extraction LLM chain."""
    
    target_urls: List[str] = Field(
        ..., 
        description="Target websites or URLs to scrape from"
    )
    data_to_extract: List[Dict[str, str]] = Field(
        ..., 
        description="Data fields to extract with names and optional descriptions"
    )
    technical_requirements: List[str] = Field(
        default_factory=lambda: ["html_parsing"],
        description="Technical requirements for scraping (e.g., 'javascript_rendering')"
    )


def parse_llm_output(llm_output: str) -> Dict[str, Any]:
    """
    Parse the raw LLM output string into a structured dictionary.
    This function is kept for backward compatibility and now uses the centralized parser.
    
    Args:
        llm_output: Raw string output from the LLM
        
    Returns:
        Parsed dictionary from the JSON output
        
    Raises:
        ValueError: If parsing fails
    """
    return parse_json_from_llm_output(llm_output, "intent output")


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
    
    # Create a Pydantic parser for the output
    parser = PydanticOutputParser(pydantic_object=LLMIntentSpec)
    
    # Use string parser as fallback if structured parsing fails
    def parse_with_fallback(llm_output: str) -> Dict[str, Any]:
        try:
            # Try to parse as Pydantic model first
            return parser.parse(llm_output).model_dump()
        except Exception as e:
            logger.warning(f"Pydantic parsing failed: {e}. Falling back to raw JSON parsing.")
            # Fall back to manual JSON parsing
            return parse_json_from_llm_output(llm_output, "intent output")
    
    # Create the chain
    chain = (
        prompt
        | get_llm()
        | StrOutputParser()
        | parse_with_fallback
    )
    
    return chain


async def extract_intent_with_retry(
    query: str, 
    context_hints: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Extract intent from user query with retry logic.
    
    Args:
        query: User's natural language query
        context_hints: Optional list of critique hints for context
        
    Returns:
        Extracted intent as a dictionary
    """
    use_context = context_hints is not None and len(context_hints) > 0
    prompt = intent_with_context_prompt if use_context else intent_extraction_prompt
    
    inputs = {"user_query": query}
    
    if use_context:
        inputs["critique_hints"] = "\n".join(context_hints)
    
    logger.info(f"Extracting intent with{'out' if not use_context else ''} context hints")
    
    # Call LLM with retry
    llm_output = await call_llm_with_retry(get_llm(), prompt, inputs)
    
    # Parse the output
    return parse_json_from_llm_output(llm_output, "intent output")


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
    # Create FieldToExtract objects from the data_to_extract dicts
    extracted_fields = [
        FieldToExtract(
            name=field.get("field_name", field.get("name", "unknown")),
            description=field.get("description")
        )
        for field in output["data_to_extract"]
    ]
    
    # Get the target URLs - handle both old and new field names
    target_urls = output.get("target_urls_or_sites", output.get("target_urls", []))
    
    # Create the IntentSpec with a new ID if it's a new spec, or update the existing one
    if existing_spec:
        spec = existing_spec.model_copy(deep=True)
        
        # Update the fields that may have changed
        spec.target_urls = target_urls
        spec.fields_to_extract = extracted_fields
        
        # Add technical requirements if needed
        if "javascript" in str(output).lower():
            if "javascript_rendering" not in spec.technical_requirements:
                spec.technical_requirements.append("javascript_rendering")
        
        # Add revision indicator to spec_id if not already present
        if "_rev" not in spec.spec_id:
            spec.spec_id = f"{spec.spec_id}_rev1"
    else:
        # Create a brand new spec
        tech_requirements = ["html_parsing"]
        if "javascript" in str(output).lower():
            tech_requirements.append("javascript_rendering")
            
        spec = IntentSpec(
            original_query=user_query,
            target_urls=target_urls,
            fields_to_extract=extracted_fields,
            technical_requirements=tech_requirements
        )
    
    return spec

def get_intent_chain():
    """
    Get the intent extraction chain for the MVP implementation.
    
    This simplified function returns the standard intent extraction chain
    optimized for the MVP workflow.
    
    Returns:
        A runnable chain that extracts intent from user queries
    """
    return create_intent_extraction_chain(use_context=False)
