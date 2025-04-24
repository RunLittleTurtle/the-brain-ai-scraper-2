#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for core_secrets.py in the config_secrets module.

These tests verify that the core functionality for managing configuration values
and secrets works correctly, including loading from .env files and environment variables.
"""

import os
import pytest
import tempfile
from pathlib import Path
from typing import Dict, Generator, Tuple

from config_secrets.core_secrets import (
    load_dotenv_file,
    get_config,
    get_secret,
    get_required_secret,
    set_config_value,
    unset_config_value,
    list_config_keys
)
from config_secrets.exceptions import SecretNotFoundError, DotEnvWriteError


@pytest.fixture
def temp_env_file() -> Generator[Tuple[str, Dict[str, str]], None, None]:
    """Create a temporary .env file for testing."""
    # Create a temporary directory and file
    with tempfile.TemporaryDirectory() as temp_dir:
        env_path = Path(temp_dir) / ".env"
        
        # Sample test environment variables
        test_vars = {
            "TEST_VAR": "test_value",
            "TEST_SECRET": "super_secret",
            "API_KEY": "sk-1234567890abcdef"
        }
        
        # Write test variables to the file
        with open(env_path, "w") as f:
            f.write("# Test .env file\n")
            for key, value in test_vars.items():
                f.write(f'{key}="{value}"\n')
        
        yield str(env_path), test_vars


class TestCoreFunctions:
    """Test core functionality of config_secrets module."""
    
    def test_load_dotenv_file(self, temp_env_file: Tuple[str, Dict[str, str]]) -> None:
        """Test loading environment variables from .env file."""
        env_path, test_vars = temp_env_file
        
        # Clear the environment variables first
        for key in test_vars:
            if key in os.environ:
                del os.environ[key]
        
        # Load the .env file
        result = load_dotenv_file(env_path)
        
        # Verify function returns True (file was found and loaded)
        assert result is True
        
        # Verify variables were loaded into environment
        for key, value in test_vars.items():
            assert os.getenv(key) == value
    
    def test_get_config(self, temp_env_file: Tuple[str, Dict[str, str]]) -> None:
        """Test retrieving configuration values."""
        env_path, test_vars = temp_env_file
        load_dotenv_file(env_path)
        
        # Test retrieving existing value
        assert get_config("TEST_VAR") == "test_value"
        
        # Test with default when key doesn't exist
        assert get_config("NONEXISTENT_KEY", "default_value") == "default_value"
        
        # Test with None default
        assert get_config("NONEXISTENT_KEY") is None
    
    def test_get_secret(self, temp_env_file: Tuple[str, Dict[str, str]]) -> None:
        """Test retrieving secret values."""
        env_path, test_vars = temp_env_file
        load_dotenv_file(env_path)
        
        # Test retrieving existing secret
        assert get_secret("TEST_SECRET") == "super_secret"
        assert get_secret("API_KEY") == "sk-1234567890abcdef"
        
        # Test with default when key doesn't exist
        assert get_secret("NONEXISTENT_SECRET", "default_secret") == "default_secret"
    
    def test_get_required_secret(self, temp_env_file: Tuple[str, Dict[str, str]]) -> None:
        """Test retrieving required secret values."""
        env_path, test_vars = temp_env_file
        load_dotenv_file(env_path)
        
        # Test retrieving existing secret
        assert get_required_secret("TEST_SECRET") == "super_secret"
        
        # Test exception when key doesn't exist
        with pytest.raises(SecretNotFoundError) as excinfo:
            get_required_secret("NONEXISTENT_SECRET")
        assert "NONEXISTENT_SECRET" in str(excinfo.value)
    
    def test_set_and_unset_config(self, temp_env_file: Tuple[str, Dict[str, str]]) -> None:
        """Test setting and unsetting configuration values."""
        env_path, _ = temp_env_file
        
        # Set a new value
        set_config_value("NEW_VAR", "new_value", env_path)
        
        # Reload and verify it was set
        load_dotenv_file(env_path)
        assert get_config("NEW_VAR") == "new_value"
        
        # Update existing value
        set_config_value("NEW_VAR", "updated_value", env_path)
        
        # Reload and verify it was updated
        load_dotenv_file(env_path)
        assert get_config("NEW_VAR") == "updated_value"
        
        # Unset the value
        unset_config_value("NEW_VAR", env_path)
        
        # Verify it was removed from .env (need to check manually since it's still in the env)
        with open(env_path, "r") as f:
            content = f.read()
        assert "NEW_VAR" not in content
    
    def test_list_config_keys(self, temp_env_file: Tuple[str, Dict[str, str]]) -> None:
        """Test listing configuration keys and values."""
        env_path, test_vars = temp_env_file
        
        # Test with masking (default)
        configs = list_config_keys(mask_sensitive=True, dotenv_path=env_path)
        
        # Verify the number of items
        assert len(configs) == len(test_vars)
        
        # Verify all keys are present
        keys = [key for key, _ in configs]
        for key in test_vars:
            assert key in keys
        
        # Check that API_KEY is masked
        for key, value in configs:
            if key == "API_KEY":
                assert value != test_vars[key]
                assert "*" in value
            elif key == "TEST_VAR":
                assert value == test_vars[key]
        
        # Test without masking
        configs_unmasked = list_config_keys(mask_sensitive=False, dotenv_path=env_path)
        
        # Verify values are not masked
        for key, value in configs_unmasked:
            assert value == test_vars[key]
