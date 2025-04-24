#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for the tool_registry.core_tool module.

This module contains tests for the ToolRegistry class and related functionality.
"""

import os
import json
import tempfile
from pathlib import Path

import pytest

from tool_registry.core_tool import ToolRegistry
from tool_registry.models import ToolMetadata
from tool_registry.exceptions import (
    ToolNotFoundError,
    ToolValidationError,
    ToolAlreadyExistsError
)


@pytest.fixture
def temp_storage_file():
    """Create a temporary file for tool registry storage."""
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    yield path
    # Cleanup
    if os.path.exists(path):
        os.unlink(path)


@pytest.fixture
def test_tools():
    """Create sample tool metadata for testing."""
    playwright = ToolMetadata(
        name="playwright",
        description="A browser automation tool",
        tool_type="browser",
        package_name="playwright",
        pip_install_command="pip install playwright",
        execution_mode="async",
        capabilities=["javascript_rendering", "headless_mode"],
        compatibilities=["type:parser"],
        incompatible_with=["selenium"]
    )
    
    beautifulsoup = ToolMetadata(
        name="beautifulsoup4",
        description="A parsing library",
        tool_type="parser",
        package_name="beautifulsoup4",
        execution_mode="sync",
        capabilities=["html_parsing", "xml_parsing"],
        compatibilities=["type:browser", "type:http_client"]
    )
    
    selenium = ToolMetadata(
        name="selenium",
        description="A browser automation tool",
        tool_type="browser",
        package_name="selenium",
        execution_mode="sync",
        capabilities=["javascript_rendering", "headless_mode"],
        compatibilities=["type:parser"],
        incompatible_with=["playwright"]
    )
    
    return [playwright, beautifulsoup, selenium]


class TestToolRegistry:
    """Tests for the ToolRegistry class."""
    
    def test_init_with_custom_path(self, temp_storage_file):
        """Test initializing with a custom storage path."""
        # Act
        registry = ToolRegistry(storage_path=temp_storage_file)
        
        # Assert
        assert registry.storage_path == Path(temp_storage_file)
        assert registry.tools == {}
        assert os.path.exists(temp_storage_file)
    
    def test_add_tool(self, temp_storage_file, test_tools):
        """Test adding a tool to the registry."""
        # Arrange
        registry = ToolRegistry(storage_path=temp_storage_file)
        tool = test_tools[0]  # playwright
        
        # Act
        result = registry.add_tool(tool)
        
        # Assert
        assert result == tool
        assert tool.name in registry.tools
        assert registry.tools[tool.name] == tool
        
        # Check if file was saved correctly
        with open(temp_storage_file, 'r') as f:
            saved_data = json.load(f)
        assert len(saved_data) == 1
        assert saved_data[0]["name"] == tool.name
    
    def test_add_tool_from_dict(self, temp_storage_file):
        """Test adding a tool from a dictionary."""
        # Arrange
        registry = ToolRegistry(storage_path=temp_storage_file)
        tool_dict = {
            "name": "requests",
            "description": "HTTP client library",
            "tool_type": "http_client",
            "package_name": "requests",
            "execution_mode": "sync",
            "capabilities": ["http_request"]
        }
        
        # Act
        result = registry.add_tool(tool_dict)
        
        # Assert
        assert result.name == "requests"
        assert result.description == "HTTP client library"
        assert "requests" in registry.tools
    
    def test_get_tool(self, temp_storage_file, test_tools):
        """Test getting a tool from the registry."""
        # Arrange
        registry = ToolRegistry(storage_path=temp_storage_file)
        tool = test_tools[0]  # playwright
        registry.add_tool(tool)
        
        # Act
        result = registry.get_tool(tool.name)
        
        # Assert
        assert result == tool
    
    def test_get_nonexistent_tool(self, temp_storage_file):
        """Test getting a tool that doesn't exist."""
        # Arrange
        registry = ToolRegistry(storage_path=temp_storage_file)
        
        # Act & Assert
        with pytest.raises(ToolNotFoundError):
            registry.get_tool("nonexistent_tool")
    
    def test_list_tools(self, temp_storage_file, test_tools):
        """Test listing all tools in the registry."""
        # Arrange
        registry = ToolRegistry(storage_path=temp_storage_file)
        for tool in test_tools:
            registry.add_tool(tool)
        
        # Act
        result = registry.list_tools()
        
        # Assert
        assert len(result) == 3
        tool_names = [tool.name for tool in result]
        assert "playwright" in tool_names
        assert "beautifulsoup4" in tool_names
        assert "selenium" in tool_names
    
    def test_list_tools_with_type_filter(self, temp_storage_file, test_tools):
        """Test listing tools filtered by type."""
        # Arrange
        registry = ToolRegistry(storage_path=temp_storage_file)
        for tool in test_tools:
            registry.add_tool(tool)
        
        # Act
        result = registry.list_tools(tool_type="browser")
        
        # Assert
        assert len(result) == 2
        tool_names = [tool.name for tool in result]
        assert "playwright" in tool_names
        assert "selenium" in tool_names
        assert "beautifulsoup4" not in tool_names
    
    def test_list_tools_with_capability_filter(self, temp_storage_file, test_tools):
        """Test listing tools filtered by capability."""
        # Arrange
        registry = ToolRegistry(storage_path=temp_storage_file)
        for tool in test_tools:
            registry.add_tool(tool)
        
        # Act
        result = registry.list_tools(capability="html_parsing")
        
        # Assert
        assert len(result) == 1
        assert result[0].name == "beautifulsoup4"
    
    def test_remove_tool(self, temp_storage_file, test_tools):
        """Test removing a tool from the registry."""
        # Arrange
        registry = ToolRegistry(storage_path=temp_storage_file)
        for tool in test_tools:
            registry.add_tool(tool)
        
        # Act
        result = registry.remove_tool("playwright")
        
        # Assert
        assert result is True
        assert "playwright" not in registry.tools
        assert len(registry.tools) == 2
    
    def test_remove_nonexistent_tool(self, temp_storage_file):
        """Test removing a tool that doesn't exist."""
        # Arrange
        registry = ToolRegistry(storage_path=temp_storage_file)
        
        # Act
        result = registry.remove_tool("nonexistent_tool")
        
        # Assert
        assert result is False
    
    def test_check_compatibility_compatible_tools(self, temp_storage_file, test_tools):
        """Test checking compatibility for compatible tools."""
        # Arrange
        registry = ToolRegistry(storage_path=temp_storage_file)
        for tool in test_tools:
            registry.add_tool(tool)
        
        # Act
        result = registry.check_compatibility(["playwright", "beautifulsoup4"])
        
        # Assert
        assert result is True
    
    def test_check_compatibility_incompatible_tools(self, temp_storage_file, test_tools):
        """Test checking compatibility for incompatible tools."""
        # Arrange
        registry = ToolRegistry(storage_path=temp_storage_file)
        for tool in test_tools:
            registry.add_tool(tool)
        
        # Act
        result = registry.check_compatibility(["playwright", "selenium"])
        
        # Assert
        assert result is False
    
    def test_find_compatible_tools(self, temp_storage_file, test_tools):
        """Test finding compatible tools for a specified tool."""
        # Arrange
        registry = ToolRegistry(storage_path=temp_storage_file)
        for tool in test_tools:
            registry.add_tool(tool)
        
        # Act
        result = registry.find_compatible_tools("playwright")
        
        # Assert
        assert len(result) == 1
        assert result[0].name == "beautifulsoup4"
    
    def test_find_compatible_tools_with_type_filter(self, temp_storage_file, test_tools):
        """Test finding compatible tools filtered by type."""
        # Arrange
        registry = ToolRegistry(storage_path=temp_storage_file)
        for tool in test_tools:
            registry.add_tool(tool)
        
        # Act
        result = registry.find_compatible_tools("beautifulsoup4", target_type="browser")
        
        # Assert
        # Both playwright and selenium should be compatible with beautifulsoup4 since it's compatible with 'type:browser'
        assert len(result) == 2
        
        # Both browser tools should be in the results
        tool_names = [tool.name for tool in result]
        assert "playwright" in tool_names
        assert "selenium" in tool_names
