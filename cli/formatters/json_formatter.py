#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JSON output formatter for CLI responses.

This module provides functions to convert various data types to JSON format
for machine-readable CLI output.
"""

import json
from typing import Any, Dict, List, Union, Optional
from datetime import datetime
from pydantic import BaseModel

def format_json(data: Any) -> str:
    """
    Format data as a JSON string.
    
    This function handles special cases like Pydantic models and datetime objects.
    
    Args:
        data: The data to format as JSON
        
    Returns:
        JSON-formatted string
    """
    return json.dumps(_prepare_for_json(data), indent=2)

def _prepare_for_json(data: Any) -> Any:
    """
    Prepare data for JSON serialization by handling special cases.
    
    This function recursively processes data structures to ensure they can be
    properly serialized to JSON.
    
    Args:
        data: The data to prepare for JSON serialization
        
    Returns:
        JSON-serializable data
    """
    # Handle None
    if data is None:
        return None
        
    # Handle Pydantic models
    if isinstance(data, BaseModel):
        return _prepare_for_json(data.dict())
        
    # Handle lists and tuples
    if isinstance(data, (list, tuple)):
        return [_prepare_for_json(item) for item in data]
        
    # Handle dictionaries
    if isinstance(data, dict):
        return {k: _prepare_for_json(v) for k, v in data.items()}
        
    # Handle datetime objects
    if isinstance(data, datetime):
        return data.isoformat()
        
    # Handle custom objects with __dict__
    if hasattr(data, '__dict__'):
        return _prepare_for_json(data.__dict__)
        
    # Return primitive types as-is
    return data
