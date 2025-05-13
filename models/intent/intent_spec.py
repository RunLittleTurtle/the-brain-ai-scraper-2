#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unified intent specification model for the Brain AI Scraper.

This module defines the Pydantic models for representing user intent specifications
that are shared across the CLI and intent_inference modules.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import uuid


class FieldToExtract(BaseModel):
    """A data field to extract from a webpage."""
    name: str = Field(
        ..., 
        description="Field name (e.g., 'price', 'title')"
    )
    description: Optional[str] = Field(
        None, 
        description="Optional description of what the field represents"
    )


class IntentSpec(BaseModel):
    """
    Unified specification for scraping intent, used across the application.
    
    This model captures all aspects of a user's scraping intent, including validation
    status, critique history, and clarification questions for robust intent inference.
    """
    spec_id: str = Field(
        default_factory=lambda: f"intent_{uuid.uuid4().hex[:8]}",
        description="Unique identifier for this intent specification"
    )
    original_query: str = Field(
        ..., 
        description="Original user query text that created this spec"
    )
    target_urls: List[str] = Field(
        ..., 
        description="Target URLs or websites to scrape from"
    )
    fields_to_extract: List[FieldToExtract] = Field(
        ..., 
        description="Data fields to extract from the target sites"
    )
    technical_requirements: List[str] = Field(
        default_factory=lambda: ["html_parsing"],
        description="Technical requirements (e.g., 'javascript_rendering', 'html_parsing')"
    )
    constraints: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional constraints on the scraping operation (e.g., time periods, locations)"
    )
    url_health_status: Dict[str, str] = Field(
        default_factory=dict,
        description="Health status for each URL (healthy, unavailable, error)"
    )
    validation_status: str = Field(
        default="pending",
        description="Status of validation (pending, validated_by_llm_judge, needs_clarification, human_approved)"
    )
    critique_history: List[str] = Field(
        default_factory=list,
        description="History of validation issues and critiques from the LLM judge"
    )
    clarification_questions: List[str] = Field(
        default_factory=list,
        description="Questions to ask the user for clarification if necessary"
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to a simplified dict for CLI display.
        
        Returns:
            Dictionary with essential information for display
        """
        return {
            "id": self.spec_id,
            "urls": self.target_urls,
            "fields": [f.name for f in self.fields_to_extract],
            "requirements": self.technical_requirements,
            "constraints": self.constraints,
            "validation_status": self.validation_status,
            "url_health": self.url_health_status,
            "needs_clarification": len(self.clarification_questions) > 0,
            "has_critique": len(self.critique_history) > 0
        }
