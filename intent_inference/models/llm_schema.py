#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Schema models for LLM inputs and outputs in the intent inference module.

This module defines Pydantic models for standardizing LLM interactions,
specifically for the intent extraction, feedback processing, and validation chains.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


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
    constraints: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional constraints on the scraping operation (e.g., time periods, locations)"
    )
    technical_requirements: List[str] = Field(
        default_factory=lambda: ["html_parsing"],
        description="Technical requirements for scraping (e.g., 'javascript_rendering')"
    )


class LLMFeedback(BaseModel):
    """Model for the structured output from the feedback processing LLM chain."""
    
    target_urls_to_add: List[str] = Field(
        default_factory=list,
        description="New URLs to add to the existing list"
    )
    target_urls_to_remove: List[str] = Field(
        default_factory=list,
        description="URLs to remove from the existing list"
    )
    fields_to_add: List[Dict[str, str]] = Field(
        default_factory=list,
        description="New fields to extract with names and descriptions"
    )
    fields_to_remove: List[str] = Field(
        default_factory=list,
        description="Fields to remove (by name) from the existing list"
    )
    constraints_to_update: Dict[str, Any] = Field(
        default_factory=dict,
        description="Constraints to add or update"
    )
    requirements_to_add: List[str] = Field(
        default_factory=list,
        description="Technical requirements to add"
    )
    reasoning: str = Field(
        default="",
        description="Explanation of changes made based on user feedback"
    )


class LLMValidation(BaseModel):
    """Model for the structured output from the validation (LLM-as-Judge) chain."""
    
    is_valid: bool = Field(
        ...,
        description="Whether the intent specification is valid and complete"
    )
    issues: List[str] = Field(
        default_factory=list,
        description="List of issues or problems with the intent specification"
    )
    needs_clarification: bool = Field(
        default=False,
        description="Whether the user needs to provide clarification"
    )
    clarification_questions: List[str] = Field(
        default_factory=list,
        description="Questions to ask the user if clarification is needed"
    )
    suggested_improvements: List[str] = Field(
        default_factory=list,
        description="Suggested improvements that can be made automatically without user input"
    )
