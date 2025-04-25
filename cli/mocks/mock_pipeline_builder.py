#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mock implementation of the pipeline_builder module.

This module provides mock functionality for building scraping pipelines
based on an intent specification.
"""

from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel
from uuid import uuid4

from cli.mocks.mock_intent_inference import IntentSpec


class ToolConfig(BaseModel):
    """Configuration for a tool in a pipeline."""
    name: str
    tool_type: str
    config: Dict[str, Any]
    selectors: Dict[str, str] = {}


class PipelineSpec(BaseModel):
    """Specification of a scraping pipeline."""
    id: str
    intent: IntentSpec
    tools: List[ToolConfig]
    timeout_seconds: int = 30
    max_retries: int = 2


def mock_build_pipeline(intent: IntentSpec) -> PipelineSpec:
    """
    Mock implementation of pipeline building.
    
    This function takes an intent specification and creates a pipeline
    of tools to fulfill that intent, simulating the pipeline_builder module.
    
    Args:
        intent: Specification of the scraping intent
        
    Returns:
        A PipelineSpec object with the pipeline configuration
    """
    # Generate a unique ID for the pipeline
    pipeline_id = f"pipe_{str(uuid4())[:8]}"
    
    # Build pipeline tools based on intent requirements
    tools: List[ToolConfig] = []
    
    # Determine browser tool based on requirements
    if "javascript_rendering" in intent.requirements.technical:
        # Use Playwright for JavaScript rendering
        tools.append(ToolConfig(
            name="playwright",
            tool_type="browser",
            config={
                "headless": True,
                "timeout": 30000,
                "wait_until": "networkidle"
            }
        ))
    else:
        # Use Requests for simple HTTP requests
        tools.append(ToolConfig(
            name="requests",
            tool_type="http_client",
            config={
                "timeout": 10,
                "headers": {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
            }
        ))
    
    # Add parser tool
    parser_tool = ToolConfig(
        name="beautifulsoup4",
        tool_type="parser",
        config={
            "parser": "html.parser"
        },
        selectors={}
    )
    
    # Add selectors based on fields to extract
    for field in intent.data_to_extract:
        if field == "title":
            parser_tool.selectors[field] = "title, h1.product-title, h1.title, h1"
        elif field == "price":
            parser_tool.selectors[field] = ".price, .product-price, span[itemprop='price']"
        elif field == "description":
            parser_tool.selectors[field] = "meta[name='description'], #description, .product-description"
        elif field == "image":
            parser_tool.selectors[field] = "img.product-image, meta[property='og:image']"
        elif field == "rating":
            parser_tool.selectors[field] = ".rating, .product-rating, [itemprop='ratingValue']"
        else:
            # Generic selector for other fields
            parser_tool.selectors[field] = f".{field}, [itemprop='{field}'], #{field}"
    
    tools.append(parser_tool)
    
    # Return pipeline specification
    return PipelineSpec(
        id=pipeline_id,
        intent=intent,
        tools=tools,
        timeout_seconds=60 if "javascript_rendering" in intent.requirements.technical else 30,
        max_retries=2
    )
