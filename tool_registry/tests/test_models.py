#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for the tool_registry.models module.

This module contains tests for the Pydantic models used in the tool registry.
"""

import pytest
from pydantic import ValidationError

from tool_registry.models import ToolMetadata


class TestToolMetadata:
    """Tests for the ToolMetadata Pydantic model."""
    
    def test_valid_tool_metadata(self):
        """Test that a valid tool metadata passes validation."""
        # Arrange
        valid_data = {
            "name": "test_tool",
            "description": "A test tool",
            "tool_type": "browser",
            "package_name": "test_package",
            "execution_mode": "sync",
            "capabilities": ["test_capability"],
        }
        
        # Act
        tool = ToolMetadata(**valid_data)
        
        # Assert
        assert tool.name == "test_tool"
        assert tool.description == "A test tool"
        assert tool.tool_type == "browser"
        assert tool.package_name == "test_package"
        assert tool.execution_mode == "sync"
        assert tool.capabilities == ["test_capability"]
        assert tool.compatibilities == []
        assert tool.incompatible_with == []
        assert tool.required_config == []
    
    def test_invalid_execution_mode(self):
        """Test that an invalid execution mode fails validation."""
        # Arrange
        invalid_data = {
            "name": "test_tool",
            "description": "A test tool",
            "tool_type": "browser",
            "package_name": "test_package",
            "execution_mode": "invalid",  # Not 'sync' or 'async'
            "capabilities": ["test_capability"],
        }
        
        # Act & Assert
        with pytest.raises(ValidationError):
            ToolMetadata(**invalid_data)
    
    def test_missing_required_fields(self):
        """Test that missing required fields fail validation."""
        # Arrange - missing name, description, tool_type
        invalid_data = {
            "package_name": "test_package",
            "execution_mode": "sync",
            "capabilities": ["test_capability"],
        }
        
        # Act & Assert
        with pytest.raises(ValidationError):
            ToolMetadata(**invalid_data)
    
    def test_default_values(self):
        """Test that default values are set correctly."""
        # Arrange
        minimal_data = {
            "name": "test_tool",
            "description": "A test tool",
            "tool_type": "browser",
            "package_name": "test_package",
            "execution_mode": "sync",
            "capabilities": ["test_capability"],
        }
        
        # Act
        tool = ToolMetadata(**minimal_data)
        
        # Assert
        assert tool.pip_install_command == "pip install test_package"
        assert tool.compatibilities == []
        assert tool.incompatible_with == []
        assert tool.required_config == []
    
    def test_custom_pip_command(self):
        """Test that a custom pip command is set correctly."""
        # Arrange
        data = {
            "name": "test_tool",
            "description": "A test tool",
            "tool_type": "browser",
            "package_name": "test_package",
            "pip_install_command": "pip install test_package[extra]",
            "execution_mode": "sync",
            "capabilities": ["test_capability"],
        }
        
        # Act
        tool = ToolMetadata(**data)
        
        # Assert
        assert tool.pip_install_command == "pip install test_package[extra]"
