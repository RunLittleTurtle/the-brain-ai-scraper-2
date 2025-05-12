#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pydantic models for tool registry metadata.

This module defines the data structures used by the tool registry to store
and validate tool metadata, including capabilities, compatibilities, and
required configurations.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class ToolMetadata(BaseModel):
    """
    Represents essential metadata for a tool that can be integrated into The Brain pipelines.
    
    This model is used to validate and store information about scraping tools,
    their capabilities, compatibilities, and configuration requirements.
    """
    name: str = Field(
        description="Unique name and identifier for the tool (e.g., 'playwright', 'requests', 'beautifulsoup4')."
    )
    description: str = Field(
        description="Short text description explaining the tool's main purpose."
    )
    tool_type: str = Field(
        description="Main functional category of the tool (e.g., 'browser', 'http_client', 'parser', 'anti_bot_service', 'captcha_solver', 'proxy_manager', 'data_storage')."
    )
    package_name: str = Field(
        description="Name of the Python package to install via pip (e.g., 'playwright', 'requests', 'beautifulsoup4')."
    )
    pip_install_command: str = Field(
        default="",
        description="Exact pip command to install the tool and its specific dependencies if needed (e.g., 'pip install playwright', 'pip install beautifulsoup4[lxml]')."
    )
    
    def __init__(self, **data):
        # Set default pip_install_command based on package_name if not provided
        if 'pip_install_command' not in data and 'package_name' in data:
            data['pip_install_command'] = f"pip install {data['package_name']}"
        super().__init__(**data)
    execution_mode: str = Field(
        description="Main execution mode ('sync' or 'async'). Crucial for orchestration by the 'executor' module.",
        pattern="^(sync|async)$"
    )
    capabilities: List[str] = Field(
        description="List of key capabilities or features offered by the tool (useful tags for selection, e.g., 'javascript_rendering', 'anti_cloudflare', 'proxy_rotation', 'html_parsing')."
    )
    compatibilities: List[str] = Field(
        default=[],
        description="List of **names** or **types ('type:*')** of other tools with which this tool is designed to interact directly or is commonly used in conjunction."
    )
    incompatible_with: List[str] = Field(
        default=[],
        description="List of tool names or tool types (prefixed with 'type:', e.g., 'type:browser') with which this tool is explicitly incompatible and cannot work in the same pipeline."
    )
    required_config: List[str] = Field(
        default=[],
        description="List of configuration or secret key names that MUST be provided for this tool to function (e.g., ['SCRAPERAPI_KEY', 'ANTICAPTCHA_KEY'])."
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "playwright",
                "description": "A modern browser automation framework by Microsoft",
                "tool_type": "browser",
                "package_name": "playwright",
                "pip_install_command": "pip install playwright==1.40.0 && playwright install --with-deps",
                "execution_mode": "async",
                "capabilities": ["javascript_rendering", "spa_support", "headless_mode"],
                "compatibilities": ["type:parser", "type:captcha_solver"],
                "incompatible_with": ["selenium"],
                "required_config": []
            }
        }
