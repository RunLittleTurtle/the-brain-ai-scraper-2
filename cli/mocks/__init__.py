#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mock implementations of future modules for The Brain CLI.

These mocks allow the CLI to function and be tested before the
actual modules are implemented.
"""

from typing import Dict, Any, List, Optional

from cli.mocks.mock_intent_inference import mock_infer_intent
from cli.mocks.mock_pipeline_builder import mock_build_pipeline
from cli.mocks.mock_executor import mock_execute_pipeline

__all__ = [
    'mock_infer_intent',
    'mock_build_pipeline',
    'mock_execute_pipeline',
]
