#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LangSmith integration utilities for the intent inference module.

This module provides utilities for integrating with LangSmith for tracing and visualization.
"""
import os
import logging
from typing import Dict, Any, List, Optional, Union

# Use simpler imports that work with any version
from langchain_core.runnables import RunnableConfig

# Try to import langsmith, but make it optional
try:
    from langsmith import Client
    LANGSMITH_AVAILABLE = True
except ImportError:
    LANGSMITH_AVAILABLE = False
    Client = None

# Define a simple decorator as a fallback
def simple_traceable(run_type=None, name=None):
    def decorator(func):
        return func
    return decorator

# Try to import the real traceable
try:
    from langsmith import traceable
except ImportError:
    traceable = simple_traceable

# Configure module logger
logger = logging.getLogger(__name__)


def get_langsmith_client() -> Optional[Client]:
    """
    Get a configured LangSmith client if environment variables are set.
    
    Returns:
        LangSmith client if properly configured, None otherwise
    """
    if not LANGSMITH_AVAILABLE:
        logger.warning("LangSmith is not available (missing dependency)")
        return None
        
    try:
        # Check if LangSmith is configured
        if os.getenv("LANGCHAIN_API_KEY") and os.getenv("LANGCHAIN_ENDPOINT"):
            logger.info("LangSmith environment detected, creating client")
            return Client()
        else:
            logger.warning("LangSmith environment variables not set")
            return None
    except Exception as e:
        logger.error(f"Error creating LangSmith client: {str(e)}")
        return None


def get_runnable_config(
    tags: List[str] = None,
    metadata: Dict[str, Any] = None,
    include_console: bool = True
) -> RunnableConfig:
    """
    Get a simplified runnable config for use with LangChain runnables.
    Fallback implementation that works without full LangChain dependencies.
    
    Args:
        tags: Tags to add to the trace
        metadata: Metadata to add to the trace
        include_console: Whether to include console logging
        
    Returns:
        Configured RunnableConfig
    """
    # Create a basic config that works with any LangChain version
    config = {}
    
    # Add tags if provided
    if tags:
        config["tags"] = tags
    
    # Add metadata if provided
    if metadata:
        config["metadata"] = metadata
    
    # Try to create a RunnableConfig
    try:
        return RunnableConfig(**config)
    except Exception as e:
        logger.warning(f"Could not create RunnableConfig: {str(e)}")
        return config


@traceable(run_type="chain", name="intent_inference")
def trace_intent_inference(func):
    """Decorator to trace intent inference functions in LangSmith."""
    return func
