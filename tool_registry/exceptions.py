#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Custom exceptions for the tool_registry module.

This module defines specific exception classes for error handling in the tool_registry module,
making it easier to catch and handle specific error conditions.
"""

from typing import Optional, List, Any


class ToolRegistryError(Exception):
    """Base exception class for all tool_registry module errors."""
    pass


class ToolValidationError(ToolRegistryError):
    """Raised when tool metadata validation fails."""
    def __init__(self, message: str, validation_errors: Optional[List[Any]] = None):
        self.validation_errors = validation_errors
        super().__init__(message)


class ToolNotFoundError(ToolRegistryError):
    """Raised when a requested tool is not found in the registry."""
    def __init__(self, tool_name: str):
        self.tool_name = tool_name
        message = f"Tool '{tool_name}' not found in the registry"
        super().__init__(message)


class ToolAlreadyExistsError(ToolRegistryError):
    """Raised when attempting to add a tool that already exists in the registry."""
    def __init__(self, tool_name: str):
        self.tool_name = tool_name
        message = f"Tool '{tool_name}' already exists in the registry"
        super().__init__(message)


class ToolCompatibilityError(ToolRegistryError):
    """Raised when tools are found to be incompatible with each other."""
    def __init__(self, message: str, tools: Optional[List[str]] = None):
        self.tools = tools
        super().__init__(message)


class ToolStorageError(ToolRegistryError):
    """Raised when there's an issue with loading or saving tool metadata to storage."""
    pass
