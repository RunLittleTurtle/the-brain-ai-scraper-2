"""
Feedback processing chain for the intent inference module.

This module implements the LangChain-based chain for processing user feedback
to update and refine an existing intent specification.
"""
from typing import Dict, Any, List, Optional
import json
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from pydantic import BaseModel, Field

from ..models.intent_spec import IntentSpec, ExtractedField
from ..prompts.feedback_prompts import feedback_processing_prompt, feedback_with_context_prompt
from ..utils.chain_helpers import get_llm


class LLMFeedbackChanges(BaseModel):
    """Model for the structured output from the feedback processing LLM chain."""
    
    changes_to_make: List[Dict[str, Any]] = Field(
        ..., 
        description="List of changes to make to the intent specification"
    )
    reasoning: str = Field(
        ..., 
        description="Explanation of the interpreted feedback"
    )


def parse_feedback_output(llm_output: str) -> Dict[str, Any]:
    """
    Parse the raw LLM output string from the feedback chain into a structured dictionary.
    
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
        raise ValueError(f"Failed to parse feedback output as JSON: {e}. Output was: {llm_output}")


def create_feedback_processing_chain(use_context: bool = False):
    """
    Create a feedback processing chain that transforms user feedback to specification changes.
    
    Args:
        use_context: Whether to use the context-aware prompt with critique hints
        
    Returns:
        A runnable chain that processes feedback for intent specs
    """
    # Select the appropriate prompt template
    prompt = feedback_with_context_prompt if use_context else feedback_processing_prompt
    
    # Create the chain
    chain = (
        prompt
        | get_llm()
        | StrOutputParser()
        | parse_feedback_output
    )
    
    return chain


def apply_feedback_to_spec(
    feedback_result: Dict[str, Any], 
    existing_spec: IntentSpec
) -> IntentSpec:
    """
    Apply the changes from the feedback processing chain to an existing IntentSpec.
    
    Args:
        feedback_result: Parsed output from the feedback chain
        existing_spec: Existing intent specification to update
        
    Returns:
        Updated IntentSpec instance
    """
    # Create a deep copy of the existing spec to avoid modifying the original
    updated_spec = existing_spec.model_copy(deep=True)
    
    # Add revision indicator to spec_id if not already present
    if "_rev" not in updated_spec.spec_id:
        updated_spec.spec_id = f"{updated_spec.spec_id}_rev1"
    elif "_rev" in updated_spec.spec_id:
        # Increment revision number
        base, rev = updated_spec.spec_id.split("_rev")
        updated_spec.spec_id = f"{base}_rev{int(rev) + 1}"
    
    # Process each change
    for change in feedback_result["changes_to_make"]:
        change_type = change.get("type", "")
        
        if change_type == "add_url":
            # Add a new URL to the target sites
            new_url = change.get("url", "")
            if new_url and new_url not in updated_spec.target_urls_or_sites:
                updated_spec.target_urls_or_sites.append(new_url)
                
        elif change_type == "remove_url":
            # Remove a URL from the target sites
            url_to_remove = change.get("url", "")
            if url_to_remove and url_to_remove in updated_spec.target_urls_or_sites:
                updated_spec.target_urls_or_sites.remove(url_to_remove)
                
        elif change_type == "replace_urls":
            # Replace all URLs with a new set
            new_urls = change.get("urls", [])
            if new_urls:
                updated_spec.target_urls_or_sites = new_urls
                
        elif change_type == "add_field":
            # Add a new field to extract
            field_name = change.get("field_name", "")
            description = change.get("description", "")
            if field_name and description:
                new_field = ExtractedField(field_name=field_name, description=description)
                
                # Check if field already exists
                existing_fields = [f.field_name for f in updated_spec.data_to_extract]
                if field_name not in existing_fields:
                    updated_spec.data_to_extract.append(new_field)
                    
        elif change_type == "remove_field":
            # Remove a field from extraction
            field_to_remove = change.get("field_name", "")
            if field_to_remove:
                updated_spec.data_to_extract = [
                    field for field in updated_spec.data_to_extract 
                    if field.field_name != field_to_remove
                ]
                
        elif change_type == "update_field":
            # Update an existing field
            field_name = change.get("field_name", "")
            new_description = change.get("description", "")
            new_name = change.get("new_name", "")
            
            if field_name:
                # Find the field to update
                for i, field in enumerate(updated_spec.data_to_extract):
                    if field.field_name == field_name:
                        # Update description if provided
                        if new_description:
                            field.description = new_description
                        
                        # Update field name if provided
                        if new_name:
                            field.field_name = new_name
                        
                        # Update the field in the list
                        updated_spec.data_to_extract[i] = field
                        break
                        
        elif change_type == "add_constraint":
            # Add or update a constraint
            constraint_key = change.get("key", "")
            constraint_value = change.get("value", "")
            
            if constraint_key and constraint_value is not None:
                updated_spec.constraints[constraint_key] = constraint_value
                
        elif change_type == "remove_constraint":
            # Remove a constraint
            constraint_key = change.get("key", "")
            
            if constraint_key and constraint_key in updated_spec.constraints:
                del updated_spec.constraints[constraint_key]
    
    # Store the reasoning in the critique history
    if "reasoning" in feedback_result and feedback_result["reasoning"]:
        if not updated_spec.critique_history:
            updated_spec.critique_history = []
        updated_spec.critique_history.append(f"Feedback applied: {feedback_result['reasoning']}")
    
    return updated_spec
