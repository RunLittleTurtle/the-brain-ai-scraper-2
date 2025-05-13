#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
intent_inference module - Transform user input into structured intent specs.

This module provides functionality for inferring user intent from natural language
input and transforming it into a structured specification for web scraping tasks.
"""

# Import and expose public API for direct use from other modules
from intent_inference.main import IntentInferenceAgent, infer_intent_sync

# Import the shared model
from models.intent.intent_spec import IntentSpec, FieldToExtract

__all__ = [
    # Core functionality
    'IntentInferenceAgent', 
    'infer_intent_sync',
    'IntentSpec',
    'FieldToExtract'
]
