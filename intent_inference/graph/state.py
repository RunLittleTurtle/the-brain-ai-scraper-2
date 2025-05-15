"""
Graph-specific state models for the intent inference graph.

This module defines Pydantic v2 models specifically for managing state
within the LangGraph workflow.
"""
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

from intent_inference.state import IntentSpec, ValidationResult, Message


class GraphState(BaseModel):
    """Main state model for the intent inference graph."""
    
    # User context
    context: dict = Field(default_factory=dict)
    
    # The current intent specification
    current_intent_spec: Optional[IntentSpec] = None
    
    # Validation information
    validation_result: Optional[ValidationResult] = None
    
    # Human review flags
    needs_human_review: bool = False
    human_approval: Optional[bool] = None
    user_feedback: Optional[str] = None
    
    # Error tracking
    error_message: Optional[str] = None
    
    # Messages for visualization
    messages: List[Message] = Field(default_factory=list)
    
    # Private data for internal use
    private_data: Dict[str, Any] = Field(default_factory=dict)
