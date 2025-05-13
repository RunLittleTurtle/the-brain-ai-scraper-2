"""
State management models for the intent inference graph.

This module defines Pydantic v2 models for managing state throughout the
intent inference process, including context, intent specifications, and
visualization messages.
"""
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field
from enum import Enum
import uuid
from datetime import datetime


class DataField(BaseModel):
    """Data field to extract from websites."""
    field_name: str
    description: str


class IntentSpec(BaseModel):
    """Intent specification model."""
    spec_id: str
    original_user_query: str
    target_urls_or_sites: List[str]
    data_to_extract: List[DataField]
    constraints: Dict[str, Any] = Field(default_factory=dict)
    url_health_status: Dict[str, str] = Field(default_factory=dict)
    validation_status: str = "pending"
    critique_history: Optional[List[str]] = None
    
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
        """Create a revision of this spec."""
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


class LLMIntentSpecSchema(BaseModel):
    """Raw LLM output for new intent processing."""
    target_urls_or_sites: List[str]
    data_to_extract: List[DataField]
    constraints: Dict[str, Any] = Field(default_factory=dict)
    reasoning: str


class LLMFeedbackSchema(BaseModel):
    """Raw LLM output for feedback processing."""
    updated_target_urls: Optional[List[str]] = None
    updated_data_fields: Optional[List[DataField]] = None
    updated_constraints: Optional[Dict[str, Any]] = None
    reasoning: str
    requires_revalidation: bool = True


class InputType(str, Enum):
    """Type of user input being processed."""
    NEW_INTENT = "new_intent"
    FEEDBACK = "feedback"


class ContextStore(BaseModel):
    """Context management for conversations."""
    user_query: str
    input_type: InputType = InputType.NEW_INTENT
    critique_hints: List[str] = Field(default_factory=list)
    last_spec: Optional[IntentSpec] = None
    iteration_count: int = 0
    conversation_id: str = Field(default_factory=lambda: f"conv_{uuid.uuid4().hex[:8]}")
    
    def increment_iteration(self) -> "ContextStore":
        """Increment the iteration counter."""
        updated = self.model_copy(deep=True)
        updated.iteration_count += 1
        return updated
    
    def add_critique_hints(self, new_hints: List[str]) -> "ContextStore":
        """Add critique hints to the context."""
        updated = self.model_copy(deep=True)
        if not updated.critique_hints:
            updated.critique_hints = []
        updated.critique_hints.extend(new_hints)
        return updated
    
    def update_last_spec(self, spec: IntentSpec) -> "ContextStore":
        """Update the last spec in the context."""
        updated = self.model_copy(deep=True)
        updated.last_spec = spec
        return updated
    
    def convert_to_feedback(self, feedback_query: str) -> "ContextStore":
        """Convert this context to handle feedback."""
        updated = self.model_copy(deep=True)
        updated.user_query = feedback_query
        updated.input_type = InputType.FEEDBACK
        return updated


class ValidationResult(BaseModel):
    """Validation result from the judge chain."""
    is_valid: bool
    issues: List[str] = Field(default_factory=list)


class Message(BaseModel):
    """Message for visualization."""
    role: str
    content: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    id: str = Field(default_factory=lambda: f"msg_{uuid.uuid4().hex[:8]}")
    metadata: Optional[Dict[str, Any]] = None


class GraphState(BaseModel):
    """Main state for the inference graph."""
    context: ContextStore
    current_intent_spec: Optional[IntentSpec] = None
    validation_result: Optional[ValidationResult] = None
    user_feedback: Optional[str] = None
    needs_human_review: bool = False
    human_approval: Optional[bool] = None
    error_message: Optional[str] = None
    
    # For LangGraph Studio visualization
    key_messages: List[Message] = Field(default_factory=list)
    
    # Private state for sharing between nodes
    private_data: Dict[str, Any] = Field(default_factory=dict)
