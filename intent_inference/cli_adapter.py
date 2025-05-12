#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLI adapter for the intent_inference module.

This module provides an adapter between the intent_inference module's 
internal models and the CLI's expected interface.
"""

from typing import List, Optional, Dict, Any

from intent_inference.main import infer_intent_sync
from intent_inference.models.intent_spec import IntentSpec as InternalIntentSpec

# Pydantic models to match CLI expectations
from pydantic import BaseModel


class IntentTarget(BaseModel):
    """Target of the scraping intent."""
    type: str  # e.g., 'url', 'search', 'file'
    value: str  # The actual target value


class TechnicalRequirements(BaseModel):
    """Technical requirements for scraping."""
    technical: List[str]  # e.g., 'javascript_rendering', 'html_parsing'


class IntentSpec(BaseModel):
    """Specification of a scraping intent."""
    target: IntentTarget
    requirements: TechnicalRequirements
    data_to_extract: List[str]  # fields to extract


def infer_intent(text: str) -> IntentSpec:
    """
    Infer intent from natural language input.
    
    This function provides a compatible interface for the CLI module,
    mapping our internal IntentSpec to the expected CLI format.
    
    Args:
        text: Free-text description of the scraping task
        
    Returns:
        An IntentSpec object with the parsed intent in CLI format
    """
    # Use our internal implementation
    internal_spec = infer_intent_sync(text)
    
    if not internal_spec:
        # Fallback if inference fails
        return IntentSpec(
            target=IntentTarget(type="url", value="https://example.com"),
            requirements=TechnicalRequirements(technical=["html_parsing"]),
            data_to_extract=["title"]
        )
    
    # Extract the first URL
    url = internal_spec.target_urls_or_sites[0] if internal_spec.target_urls_or_sites else "https://example.com"
    
    # Extract field names
    fields = [field.field_name for field in internal_spec.data_to_extract]
    
    # Determine technical requirements based on constraints and metadata
    requirements = ["html_parsing"]
    
    # Check if JavaScript rendering is likely needed
    js_indicators = ["javascript", "dynamic", "spa", "render"]
    domain = url.split("//")[-1].split("/")[0].lower()
    js_sites = ["amazon", "ebay", "walmart", "etsy", "airbnb", "booking"]
    
    if (any(indicator in str(internal_spec.constraints).lower() for indicator in js_indicators) or
        any(site in domain for site in js_sites)):
        requirements.append("javascript_rendering")
    
    # Map to CLI-expected format
    return IntentSpec(
        target=IntentTarget(type="url", value=url),
        requirements=TechnicalRequirements(technical=requirements),
        data_to_extract=fields
    )
