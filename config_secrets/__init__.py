#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
config_secrets module - centralized configuration and secrets management.

This module automatically loads configuration from environment variables and 
.env files on import, and provides a consistent interface for other modules 
to access configuration values and sensitive secrets.
"""

from typing import Any, Optional, Dict

from config_secrets.core_secrets import (
    load_dotenv_file,
    get_config,
    get_secret,
    get_required_secret,
    set_config_value,
    unset_config_value,
    list_config_keys
)
from config_secrets.exceptions import (
    ConfigError,
    SecretNotFoundError,
    DotEnvWriteError
)

# Automatically load .env file on import (won't override existing env vars)
load_dotenv_file()

__all__ = [
    # Core functions
    'get_config',
    'get_secret',
    'get_required_secret',
    'set_config_value',
    'unset_config_value',
    'list_config_keys',
    'load_dotenv_file',
    
    # Exceptions
    'ConfigError',
    'SecretNotFoundError', 
    'DotEnvWriteError'
]
