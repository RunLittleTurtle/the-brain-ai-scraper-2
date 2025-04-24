#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pydantic models for the config_secrets module.

This is a placeholder file for V1. It may be extended in the future to provide
formal validation schemas if the config_secrets module is enhanced with more
structured configuration handling.
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field


class ConfigEntry(BaseModel):
    """
    A model representing a single configuration entry.
    
    This is a placeholder for potential future use. Currently not used in
    the core implementation, which uses simple string key-value pairs.
    """
    key: str = Field(..., description="The configuration key name")
    value: str = Field(..., description="The configuration value")
    is_secret: bool = Field(False, description="Whether this is a sensitive value that should be masked in output")
    description: Optional[str] = Field(None, description="Optional description of what this configuration does")

    class Config:
        """Pydantic model configuration."""
        extra = "forbid"  # Prevent extra fields
