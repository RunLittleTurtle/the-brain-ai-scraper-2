#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Custom exceptions for the config_secrets module.
"""

from typing import Optional


class ConfigError(Exception):
    """Base exception for all config_secrets related errors."""
    
    def __init__(self, message: str = "An error occurred in the config_secrets module") -> None:
        self.message = message
        super().__init__(self.message)


class SecretNotFoundError(ConfigError):
    """Raised when a required secret is not found in environment variables or .env file."""
    
    def __init__(self, key: str, message: Optional[str] = None) -> None:
        self.key = key
        self.message = message or f"Required secret '{key}' not found in environment variables"
        super().__init__(self.message)


class DotEnvWriteError(ConfigError):
    """Raised when an error occurs while writing to the .env file."""
    
    def __init__(self, message: Optional[str] = None) -> None:
        self.message = message or "Failed to write to .env file"
        super().__init__(self.message)
