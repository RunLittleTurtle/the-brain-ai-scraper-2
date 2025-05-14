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


class ValidationStatus(str, Enum):
    """Enhanced validation status enum with more nuanced states."""
    VALID = "valid"  # Fully valid, ready for human review
    INVALID = "invalid"  # General invalid state
    NEEDS_CLARIFICATION = "needs_clarification"  # User needs to provide more info
    URL_ISSUE = "url_issue"  # Specific URL-related problems
    MISSING_DATA = "missing_data"  # Critical data fields are missing


class ValidationResult(BaseModel):
    """Enhanced validation result with more detailed tracking."""
    is_valid: bool
    status: ValidationStatus = ValidationStatus.INVALID
    issues: List[str] = Field(default_factory=list)
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    
    @property
    def needs_clarification(self) -> bool:
        """Check if the validation result indicates a need for clarification."""
        return self.status == ValidationStatus.NEEDS_CLARIFICATION
    
    @property
    def has_url_issues(self) -> bool:
        """Check if the validation result indicates URL issues."""
        return self.status == ValidationStatus.URL_ISSUE
    
    @property
    def missing_critical_data(self) -> bool:
        """Check if the validation result indicates missing critical data."""
        return self.status == ValidationStatus.MISSING_DATA


class ValidationHistoryEntry(BaseModel):
    """Entry in the validation history tracking."""
    iteration: int
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    status: str  # String representation of ValidationStatus
    issues: List[str] = Field(default_factory=list)
    spec_id: Optional[str] = None


class ContextStore(BaseModel):
    """Enhanced context management for conversations with history tracking."""
    user_query: str
    input_type: InputType = InputType.NEW_INTENT
    critique_hints: List[str] = Field(default_factory=list)
    last_spec: Optional[IntentSpec] = None
    iteration_count: int = 0
    conversation_id: str = Field(default_factory=lambda: f"conv_{uuid.uuid4().hex[:8]}")
    # New fields for better history tracking
    validation_history: List[ValidationHistoryEntry] = Field(default_factory=list)
    
    def increment_iteration(self) -> "ContextStore":
        """Increment the iteration counter."""
        updated = self.model_copy(deep=True)
        updated.iteration_count += 1
        return updated
    
    def add_critique_hints(self, new_hints: List[str]) -> "ContextStore":
        """Add critique hints to the context with deduplication."""
        updated = self.model_copy(deep=True)
        if not updated.critique_hints:
            updated.critique_hints = []
            
        # Deduplicate hints to avoid repeating the same critique
        existing_hints_lower = [hint.lower() for hint in updated.critique_hints]
        for hint in new_hints:
            if hint.lower() not in existing_hints_lower:
                updated.critique_hints.append(hint)
                existing_hints_lower.append(hint.lower())
                
        return updated
    
    def update_last_spec(self, spec: IntentSpec) -> "ContextStore":
        """Update the last spec in the context."""
        updated = self.model_copy(deep=True)
        updated.last_spec = spec
        return updated
        
    def add_validation_history(self, validation_result: ValidationResult, spec_id: Optional[str] = None) -> "ContextStore":
        """Add a validation result to the history."""
        updated = self.model_copy(deep=True)
        
        # Create a new history entry
        entry = ValidationHistoryEntry(
            iteration=updated.iteration_count,
            status=validation_result.status.value,
            issues=validation_result.issues.copy() if validation_result.issues else [],
            spec_id=spec_id
        )
        
        # Add to history
        if not updated.validation_history:
            updated.validation_history = []
        updated.validation_history.append(entry)
        
        return updated
    
    def convert_to_feedback(self, feedback_query: str) -> "ContextStore":
        """Convert this context to handle feedback."""
        updated = self.model_copy(deep=True)
        updated.user_query = feedback_query
        updated.input_type = InputType.FEEDBACK
        return updated





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
    
    # For LangGraph Studio visualization - renamed for LangGraph Studio compatibility
    messages: List[Message] = Field(default_factory=list)
    
    # Private state for sharing between nodes
    private_data: Dict[str, Any] = Field(default_factory=dict)
