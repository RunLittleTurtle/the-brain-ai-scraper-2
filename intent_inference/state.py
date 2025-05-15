"""
State management models for the intent inference graph.

This module defines Pydantic v2 models for managing state throughout the
intent inference process, including data fields and intent specifications.
"""
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from datetime import datetime
import uuid

from pydantic import BaseModel, Field


class DataField(BaseModel):
    """Data field to extract from websites."""
    
    field_name: str
    description: str


class IntentSpec(BaseModel):
    """Intent specification model for web scraping tasks."""
    
    spec_id: str
    original_user_query: str
    target_urls_or_sites: List[str]
    data_to_extract: List[DataField]
    constraints: Dict[str, Any] = Field(default_factory=dict)
    url_health_status: Dict[str, str] = Field(default_factory=dict)
    validation_status: str = "pending"
    
    @classmethod
    def create_new(cls, user_query: str, **kwargs) -> "IntentSpec":
        """Create a new spec with a unique ID."""
        spec_id = f"intent_{uuid.uuid4().hex[:8]}"
        return cls(
            spec_id=spec_id,
            original_user_query=user_query,
            **kwargs
        )
    
    def create_revision(self, **updates) -> "IntentSpec":
        """Create a revision of this spec with updated fields."""
        new_spec = self.model_copy(deep=True)
        
        # Update spec ID to indicate revision
        if "_rev" in new_spec.spec_id:
            base, rev_num = new_spec.spec_id.rsplit("_rev", 1)
            rev_num = int(rev_num) + 1
            new_spec.spec_id = f"{base}_rev{rev_num}"
        else:
            new_spec.spec_id = f"{new_spec.spec_id}_rev1"
        
        # Apply updates
        for key, value in updates.items():
            if hasattr(new_spec, key):
                setattr(new_spec, key, value)
        
        return new_spec


class Message(BaseModel):
    """Message for visualization in LangGraph Studio."""
    
    role: str
    content: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    id: str = Field(default_factory=lambda: f"msg_{uuid.uuid4().hex[:8]}")
    metadata: Optional[Dict[str, Any]] = None


class ValidationStatus(str, Enum):
    """Validation status enum."""
    
    VALID = "valid"
    INVALID = "invalid"


class ValidationResult(BaseModel):
    """Validation result with issues and status."""
    
    is_valid: bool
    status: ValidationStatus = ValidationStatus.INVALID
    issues: List[str] = Field(default_factory=list)
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
