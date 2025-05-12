"""
Intent specification models for the intent inference module.

This module defines the Pydantic models for representing user intent specifications.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator
import uuid


class ExtractedField(BaseModel):
    """Model representing a field to be extracted from a target URL or site."""
    
    field_name: str = Field(..., description="Name of the field to extract")
    description: str = Field(..., description="Description of what this field represents")


class IntentSpec(BaseModel):
    """
    Model representing a fully specified user intent for scraping.
    
    This model captures all aspects of what the user wants to extract, from which 
    sources, and under what constraints.
    """
    
    spec_id: str = Field(
        default_factory=lambda: f"intent_{uuid.uuid4().hex[:8]}",
        description="Unique identifier for this intent specification"
    )
    original_user_query: str = Field(
        ..., 
        description="Original user query that created this spec"
    )
    target_urls_or_sites: List[str] = Field(
        ..., 
        description="Target websites or URLs to scrape from"
    )
    data_to_extract: List[ExtractedField] = Field(
        ..., 
        description="Data fields to extract from the target sites"
    ) 
    constraints: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Additional constraints on the scraping operation"
    )
    url_health_status: Dict[str, str] = Field(
        default_factory=dict,
        description="Health status for each URL (healthy, unavailable, etc.)"
    )
    validation_status: str = Field(
        default="pending", 
        description="Status of validation (pending, validated_by_llm_judge, user_approved, etc.)"
    )
    critique_history: List[str] = Field(
        default_factory=list, 
        description="History of validation issues and critiques"
    )
    clarification_questions_for_user: List[str] = Field(
        default_factory=list,
        description="Questions to ask the user for clarification if necessary"
    )
    human_approval_notes: Optional[str] = Field(
        default=None,
        description="Notes provided during human approval"
    )
    
    @field_validator('spec_id')
    @classmethod
    def validate_spec_id(cls, v: str, info: Dict[str, Any]) -> str:
        """
        Update spec_id to include revision number if this is based on a previous spec.
        
        Args:
            v: The current spec_id value
            info: Validation context with access to other model fields
            
        Returns:
            Updated spec_id with revision if appropriate
        """
        # If this is a revision of an existing spec, add a revision number
        if 'last_spec' in info.data and info.data.get('last_spec') and '_rev' not in v:
            return f"{v}_rev1"
        return v
