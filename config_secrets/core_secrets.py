#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Core functionality for loading, retrieving, and managing configuration values and secrets.

This module provides the central implementation for accessing configuration from
environment variables with fallback to .env files, as well as securely managing
sensitive information like API keys.
"""

import os
import pathlib
from typing import Any, Optional, Dict, List, Tuple
from dotenv import load_dotenv, find_dotenv, set_key, unset_key

from config_secrets.exceptions import SecretNotFoundError, DotEnvWriteError


def load_dotenv_file(dotenv_path: Optional[str] = None, verbose: bool = False) -> bool:
    """
    Load environment variables from .env file if it exists.
    
    This function uses python-dotenv to load variables from a .env file into
    the environment. It only sets variables that aren't already set in the
    environment, so system environment variables always take precedence.
    
    Args:
        dotenv_path: Path to the .env file. If None, will search for .env
                     in the current and parent directories.
        verbose: If True, will output which file is being loaded.
        
    Returns:
        True if .env file was found and loaded, False otherwise.
    """
    if dotenv_path is None:
        dotenv_path = find_dotenv(usecwd=True)
    
    if not dotenv_path:
        return False
    
    return load_dotenv(dotenv_path, override=False, verbose=verbose)


def get_config(key: str, default: Any = None) -> Optional[str]:
    """
    Get a configuration value from environment variables.
    
    Use this function for non-sensitive configuration values.
    
    Args:
        key: The environment variable name to retrieve
        default: The value to return if the key is not found
        
    Returns:
        The value of the environment variable, or the default if not found
    """
    return os.getenv(key, default)


def get_secret(key: str, default: Any = None) -> Optional[str]:
    """
    Get a sensitive secret value from environment variables.
    
    Use this function for sensitive values like API keys. Functionally identical
    to get_config() but named differently for semantic clarity.
    
    Args:
        key: The environment variable name to retrieve
        default: The value to return if the key is not found
        
    Returns:
        The value of the environment variable, or the default if not found
    """
    return os.getenv(key, default)


def get_required_secret(key: str) -> str:
    """
    Get a required secret value from environment variables.
    
    Similar to get_secret(), but raises an exception if the key is not found.
    Use this when a secret is absolutely required for the application to work.
    
    Args:
        key: The environment variable name to retrieve
        
    Returns:
        The value of the environment variable
        
    Raises:
        SecretNotFoundError: If the key is not found in environment variables
    """
    value = os.getenv(key)
    if value is None:
        raise SecretNotFoundError(key)
    return value


def set_config_value(key: str, value: str, dotenv_path: Optional[str] = None) -> bool:
    """
    Set a configuration value in the .env file.
    
    This only modifies the local .env file, not the current environment.
    
    Args:
        key: The environment variable name to set
        value: The value to set
        dotenv_path: Path to the .env file. If None, will search for .env
                     in the current and parent directories.
                     
    Returns:
        True if successful
        
    Raises:
        DotEnvWriteError: If writing to the .env file fails
    """
    if dotenv_path is None:
        dotenv_path = find_dotenv(usecwd=True)
    
    if not dotenv_path:
        # If no .env file exists, create one in the current directory
        dotenv_path = os.path.join(os.getcwd(), '.env')
        # Create the file if it doesn't exist
        if not os.path.exists(dotenv_path):
            try:
                with open(dotenv_path, 'w') as f:
                    f.write("# The Brain AI Scraper Environment Variables\n\n")
            except Exception as e:
                raise DotEnvWriteError(f"Failed to create .env file: {str(e)}")
    
    try:
        # Use python-dotenv's set_key function to update the .env file
        set_key(dotenv_path, key, value, quote_mode="always")
        
        # Update the current process environment with the new value
        os.environ[key] = value
        
        return True
    except Exception as e:
        raise DotEnvWriteError(f"Failed to set {key} in .env file: {str(e)}")


def unset_config_value(key: str, dotenv_path: Optional[str] = None) -> bool:
    """
    Remove a configuration value from the .env file.
    
    This only modifies the local .env file, not the current environment.
    
    Args:
        key: The environment variable name to remove
        dotenv_path: Path to the .env file. If None, will search for .env
                     in the current and parent directories.
                     
    Returns:
        True if successful or if key doesn't exist in .env
        
    Raises:
        DotEnvWriteError: If writing to the .env file fails
    """
    if dotenv_path is None:
        dotenv_path = find_dotenv(usecwd=True)
    
    if not dotenv_path or not os.path.exists(dotenv_path):
        return True  # Nothing to unset if there's no .env file
    
    try:
        # Use python-dotenv's unset_key function
        unset_key(dotenv_path, key)
        
        # Remove from the current process environment if present
        if key in os.environ:
            del os.environ[key]
        
        return True
    except Exception as e:
        raise DotEnvWriteError(f"Failed to unset {key} from .env file: {str(e)}")


def list_config_keys(mask_sensitive: bool = True, dotenv_path: Optional[str] = None) -> List[Tuple[str, str]]:
    """
    List all configuration keys and values from the .env file.
    
    Args:
        mask_sensitive: If True, mask values that might be sensitive
                        (containing 'key', 'password', 'secret', etc.)
        dotenv_path: Path to the .env file. If None, will search for .env
                     in the current and parent directories.
                     
    Returns:
        List of (key, value) tuples from the .env file
    """
    if dotenv_path is None:
        dotenv_path = find_dotenv(usecwd=True)
    
    if not dotenv_path or not os.path.exists(dotenv_path):
        return []
    
    result = []
    sensitive_patterns = ['key', 'password', 'secret', 'token', 'credential']
    
    try:
        # Parse the .env file manually to extract keys and values
        with open(dotenv_path, 'r') as f:
            lines = f.readlines()
            
        for line in lines:
            line = line.strip()
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
                
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                # Remove quotes if present
                if (value.startswith('"') and value.endswith('"')) or \
                   (value.startswith("'") and value.endswith("'")):
                    value = value[1:-1]
                
                # Mask sensitive values
                if mask_sensitive and any(pattern in key.lower() for pattern in sensitive_patterns):
                    # Show first 2 chars, mask the rest
                    if len(value) > 4:
                        value = value[:2] + '*' * (len(value) - 2)
                    else:
                        value = '*' * len(value)
                
                result.append((key, value))
                
        return result
    except Exception as e:
        # Just return empty list on error
        return []
