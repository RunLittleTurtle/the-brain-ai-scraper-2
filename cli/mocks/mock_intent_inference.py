#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mock implementation of the intent_inference module.

This module provides mock functionality for inferring user intent
from natural language or structured input.
"""

import re
from typing import Dict, Any, List, Optional, Union
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


def mock_infer_intent(text: str) -> IntentSpec:
    """
    Mock implementation of intent inference.
    
    This function parses free-text input to extract a URL and
    fields to extract, simulating the intent_inference module.
    
    Args:
        text: Free-text description of the scraping task
        
    Returns:
        An IntentSpec object with the parsed intent
    """
    # Extract URL using regex
    url_match = re.search(r'https?://[^\s]+', text)
    url = url_match.group(0) if url_match else "https://example.com"
    
    # Extract fields based on common keywords
    fields = []
    if "price" in text.lower():
        fields.append("price")
    if "title" in text.lower() or "name" in text.lower():
        fields.append("title")
    if "description" in text.lower():
        fields.append("description")
    if "image" in text.lower() or "photo" in text.lower():
        fields.append("image")
    if "rating" in text.lower() or "review" in text.lower():
        fields.append("rating")
    
    # If no fields were extracted, default to title
    if not fields:
        fields = ["title"]
    
    # Determine technical requirements based on domain
    requirements = ["html_parsing"]
    domain = url.split("//")[-1].split("/")[0].lower()
    
    # Add JavaScript rendering for sites that likely need it
    js_sites = ["amazon", "ebay", "walmart", "etsy", "airbnb", "booking", "javascript"]
    if any(site in domain for site in js_sites) or "javascript" in text.lower():
        requirements.append("javascript_rendering")
    
    # Return mocked intent spec
    return IntentSpec(
        target=IntentTarget(type="url", value=url),
        requirements=TechnicalRequirements(technical=requirements),
        data_to_extract=fields
    )
