"""
Context store for maintaining conversation state during intent inference.

This module defines the ContextStore model which maintains state between interactions,
including the original user query, current intent specification, and critique history.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from models.intent.intent_spec import IntentSpec


class ContextStore(BaseModel):
    """
    Maintains the conversation context for intent inference.
    
    This model acts as a central store for managing state during the intent inference process,
    including tracking the original user query, any critique hints from the LLM-as-Judge,
    and the most recent intent specification.
    """
    
    user_query: Optional[str] = Field(
        default=None, 
        description="Original user query or most recent feedback"
    )
    is_feedback: bool = Field(
        default=False, 
        description="Whether the current user_query is feedback on an existing spec"
    )
    critique_hints: List[str] = Field(
        default_factory=list, 
        description="Hints from validation to improve the specification"
    )
    last_spec: Optional[IntentSpec] = Field(
        default=None, 
        description="Most recent IntentSpec generated"
    )
    processing_attempt: int = Field(
        default=0, 
        description="Counter for retry attempts to prevent infinite loops"
    )
    max_attempts: int = Field(
        default=3, 
        description="Maximum number of self-correction attempts before requiring human input"
    )
    
    def reset(self) -> None:
        """Reset the context to its initial state."""
        self.user_query = None
        self.is_feedback = False
        self.critique_hints = []
        self.last_spec = None
        self.processing_attempt = 0
    
    def add_critique(self, critique: str) -> None:
        """
        Add a critique hint to the context and increment the processing attempt counter.
        
        Args:
            critique: The critique text to add
        """
        if critique not in self.critique_hints:
            self.critique_hints.append(critique)
        self.processing_attempt += 1
    
    def set_user_query(self, query: str, is_feedback: bool = False) -> None:
        """
        Set the user query and whether it is feedback on an existing spec.
        
        Args:
            query: The user's query or feedback text
            is_feedback: Whether this is feedback on an existing specification
        """
        self.user_query = query
        self.is_feedback = is_feedback
        if not is_feedback:
            # If this is a new query, not feedback, reset relevant state
            self.critique_hints = []
            self.last_spec = None
            self.processing_attempt = 0
    
    def update_last_spec(self, spec: IntentSpec) -> None:
        """
        Update the last specification in the context.
        
        Args:
            spec: The new intent specification
        """
        self.last_spec = spec
    
    def should_retry(self) -> bool:
        """
        Determine if the system should retry refining the spec based on critiques.
        
        Returns:
            True if under max attempts and has critique hints
        """
        return (
            self.processing_attempt < self.max_attempts and 
            len(self.critique_hints) > 0
        )
