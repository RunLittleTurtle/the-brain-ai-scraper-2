#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
The Brain - Tool Registry Module

This module provides a central registry for managing and querying
scraping tools and their metadata. It allows discovering compatible tools
for building dynamic scraping pipelines.
"""

from tool_registry.models import ToolMetadata
from tool_registry.core_tool import ToolRegistry
from tool_registry.exceptions import (
    ToolRegistryError,
    ToolValidationError,
    ToolNotFoundError,
    ToolAlreadyExistsError,
    ToolCompatibilityError,
    ToolStorageError
)

__all__ = [
    'ToolMetadata',
    'ToolRegistry',
    'ToolRegistryError',
    'ToolValidationError',
    'ToolNotFoundError',
    'ToolAlreadyExistsError',
    'ToolCompatibilityError',
    'ToolStorageError',
]
