"""
Feedback processing chain for the intent inference module.

This module implements the LangChain-based chain for processing user feedback
to update and refine an existing intent specification.
"""
import logging
from typing import Dict, Any, List, Optional
from langchain_core.output_parsers import StrOutputParser, PydanticOutputParser
from langchain_core.runnables import RunnablePassthrough
from pydantic import BaseModel, Field

from ..models.intent_spec import IntentSpec, ExtractedField
from ..prompts.feedback_prompts import feedback_processing_prompt, feedback_with_context_prompt
from ..utils.chain_helpers import get_llm, call_llm_with_retry
from ..utils.parsing import parse_json_from_llm_output

# Configure module logger
logger = logging.getLogger(__name__)


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
    This function is kept for backward compatibility and now uses the centralized parser.
    
    Args:
        llm_output: Raw string output from the LLM
        
    Returns:
        Parsed dictionary from the JSON output
        
    Raises:
        ValueError: If parsing fails
    """
    return parse_json_from_llm_output(llm_output, "feedback output")


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
    
    # Create a Pydantic parser for the output
    parser = PydanticOutputParser(pydantic_object=LLMFeedbackChanges)
    
    # Use string parser as fallback if structured parsing fails
    def parse_with_fallback(llm_output: str) -> Dict[str, Any]:
        try:
            # Try to parse as Pydantic model first
            return parser.parse(llm_output).model_dump()
        except Exception as e:
            logger.warning(f"Pydantic parsing failed: {e}. Falling back to raw JSON parsing.")
            # Fall back to manual JSON parsing
            return parse_json_from_llm_output(llm_output, "feedback output")
    
    # Create the chain
    chain = (
        prompt
        | get_llm()
        | StrOutputParser()
        | parse_with_fallback
    )
    
    return chain


async def process_feedback_with_retry(
    feedback: str, 
    intent_spec: IntentSpec, 
    context_hints: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Process user feedback with retry logic.
    
    Args:
        feedback: User feedback text
        intent_spec: Current intent specification
        context_hints: Optional list of critique hints for context
        
    Returns:
        Processed feedback result as a dictionary
    """
    use_context = context_hints is not None and len(context_hints) > 0
    prompt = feedback_with_context_prompt if use_context else feedback_processing_prompt
    
    inputs = {
        "user_feedback": feedback,
        "current_spec": intent_spec.model_dump_json(indent=2)
    }
    
    if use_context:
        inputs["critique_hints"] = "\n".join(context_hints)
    
    logger.info(f"Processing feedback with{'out' if not use_context else ''} context hints")
    
    # Call LLM with retry
    llm_output = await call_llm_with_retry(get_llm(), prompt, inputs)
    
    # Parse the output
    return parse_json_from_llm_output(llm_output, "feedback output")


def _update_spec_revision(spec: IntentSpec) -> IntentSpec:
    """Update the spec ID to include revision information.
    
    Args:
        spec: The intent specification to update
        
    Returns:
        Updated specification with incremented revision number
    """
    updated_spec = spec.model_copy(deep=True)
    
    # Add revision indicator to spec_id if not already present
    if "_rev" not in updated_spec.spec_id:
        updated_spec.spec_id = f"{updated_spec.spec_id}_rev1"
    elif "_rev" in updated_spec.spec_id:
        # Increment revision number
        base, rev = updated_spec.spec_id.split("_rev")
        updated_spec.spec_id = f"{base}_rev{int(rev) + 1}"
    
    return updated_spec


def _apply_url_changes(spec: IntentSpec, change: Dict[str, Any]) -> IntentSpec:
    """Apply URL-related changes to the specification.
    
    Args:
        spec: The intent specification to update
        change: The change to apply
        
    Returns:
        Updated specification with URL changes applied
    """
    updated_spec = spec.model_copy(deep=True)
    change_type = change.get("type", "")
    
    if change_type == "add_url":
        new_url = change.get("url", "")
        if new_url and new_url not in updated_spec.target_urls_or_sites:
            logger.info(f"Adding URL: {new_url}")
            updated_spec.target_urls_or_sites.append(new_url)
            
    elif change_type == "remove_url":
        url_to_remove = change.get("url", "")
        if url_to_remove and url_to_remove in updated_spec.target_urls_or_sites:
            logger.info(f"Removing URL: {url_to_remove}")
            updated_spec.target_urls_or_sites.remove(url_to_remove)
            
    elif change_type == "replace_urls":
        new_urls = change.get("urls", [])
        if new_urls:
            logger.info(f"Replacing URLs with: {new_urls}")
            updated_spec.target_urls_or_sites = new_urls
    
    return updated_spec


def _apply_field_changes(spec: IntentSpec, change: Dict[str, Any]) -> IntentSpec:
    """Apply field-related changes to the specification.
    
    Args:
        spec: The intent specification to update
        change: The change to apply
        
    Returns:
        Updated specification with field changes applied
    """
    updated_spec = spec.model_copy(deep=True)
    change_type = change.get("type", "")
    
    if change_type == "add_field":
        field_name = change.get("field_name", "")
        description = change.get("description", "")
        if field_name and description:
            new_field = ExtractedField(field_name=field_name, description=description)
            
            existing_fields = [f.field_name for f in updated_spec.data_to_extract]
            if field_name not in existing_fields:
                logger.info(f"Adding field: {field_name}")
                updated_spec.data_to_extract.append(new_field)
                
    elif change_type == "remove_field":
        field_to_remove = change.get("field_name", "")
        if field_to_remove:
            logger.info(f"Removing field: {field_to_remove}")
            updated_spec.data_to_extract = [
                field for field in updated_spec.data_to_extract 
                if field.field_name != field_to_remove
            ]
            
    elif change_type == "update_field":
        field_name = change.get("field_name", "")
        new_description = change.get("description", "")
        new_name = change.get("new_name", "")
        
        if field_name:
            # Find the field to update
            for i, field in enumerate(updated_spec.data_to_extract):
                if field.field_name == field_name:
                    changes_made = []
                    
                    # Update description if provided
                    if new_description:
                        field.description = new_description
                        changes_made.append("description")
                    
                    # Update field name if provided
                    if new_name:
                        field.field_name = new_name
                        changes_made.append("name")
                    
                    # Update the field in the list
                    updated_spec.data_to_extract[i] = field
                    logger.info(f"Updated field {field_name}: changed {', '.join(changes_made)}")
                    break
    
    return updated_spec


def _apply_constraint_changes(spec: IntentSpec, change: Dict[str, Any]) -> IntentSpec:
    """Apply constraint-related changes to the specification.
    
    Args:
        spec: The intent specification to update
        change: The change to apply
        
    Returns:
        Updated specification with constraint changes applied
    """
    updated_spec = spec.model_copy(deep=True)
    change_type = change.get("type", "")
    
    if change_type == "add_constraint":
        constraint_key = change.get("key", "")
        constraint_value = change.get("value", "")
        
        if constraint_key and constraint_value is not None:
            logger.info(f"Adding/updating constraint: {constraint_key}={constraint_value}")
            updated_spec.constraints[constraint_key] = constraint_value
            
    elif change_type == "remove_constraint":
        constraint_key = change.get("key", "")
        
        if constraint_key and constraint_key in updated_spec.constraints:
            logger.info(f"Removing constraint: {constraint_key}")
            del updated_spec.constraints[constraint_key]
    
    return updated_spec


def _add_reasoning_to_history(spec: IntentSpec, reasoning: str) -> IntentSpec:
    """Add reasoning to the critique history.
    
    Args:
        spec: The intent specification to update
        reasoning: The reasoning to add
        
    Returns:
        Updated specification with reasoning added to critique history
    """
    updated_spec = spec.model_copy(deep=True)
    
    if reasoning:
        if not updated_spec.critique_history:
            updated_spec.critique_history = []
        updated_spec.critique_history.append(f"Feedback applied: {reasoning}")
    
    return updated_spec


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
    logger.info(f"Applying feedback to spec {existing_spec.spec_id}")
    
    # Update revision number
    updated_spec = _update_spec_revision(existing_spec)
    
    # Process each change by type
    for change in feedback_result.get("changes_to_make", []):
        change_type = change.get("type", "")
        
        # Group changes by category
        if change_type in ["add_url", "remove_url", "replace_urls"]:
            updated_spec = _apply_url_changes(updated_spec, change)
        elif change_type in ["add_field", "remove_field", "update_field"]:
            updated_spec = _apply_field_changes(updated_spec, change)
        elif change_type in ["add_constraint", "remove_constraint"]:
            updated_spec = _apply_constraint_changes(updated_spec, change)
        else:
            logger.warning(f"Unknown change type: {change_type}")
    
    # Store the reasoning in the critique history
    reasoning = feedback_result.get("reasoning", "")
    if reasoning:
        updated_spec = _add_reasoning_to_history(updated_spec, reasoning)
    
    return updated_spec
