#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
intent_inference module - Transform user input into structured intent specs.

This module provides functionality for inferring user intent from natural language
input and transforming it into a structured specification for web scraping tasks.
"""

# Import and expose public API for direct use from other modules
from intent_inference.main import IntentInferenceAgent, infer_intent_sync
from intent_inference.models.intent_spec import IntentSpec, ExtractedField

# Import and expose CLI adapter for integration with the main CLI
from intent_inference.cli_adapter import infer_intent, IntentSpec as CLIIntentSpec

__all__ = [
    # Core functionality
    'IntentInferenceAgent', 
    'infer_intent_sync',
    'IntentSpec',
    'ExtractedField',
    
    # CLI adapter
    'infer_intent',
    'CLIIntentSpec'
]