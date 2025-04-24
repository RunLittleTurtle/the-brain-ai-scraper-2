#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo script for the tool_registry module.

This script demonstrates how to use the tool_registry to add tools,
check compatibility, and find compatible tools for building pipelines.
"""

import os
import sys
import json
from pathlib import Path

# Add the parent directory to the Python path to import the module
sys.path.insert(0, str(Path(__file__).parent.parent))

from tool_registry import ToolRegistry
from tool_registry.exceptions import ToolRegistryError, ToolNotFoundError


def main():
    """Run a demo of the tool registry functionality."""
    # Create a temporary registry for the demo
    registry = ToolRegistry()
    
    # Sample files are located in the samples directory
    samples_dir = Path(__file__).parent.parent / "samples"
    
    # Load and add sample tools
    print("Loading sample tools...")
    tool_files = ["playwright.json", "beautifulsoup4.json", "scraperapi.json"]
    for file_name in tool_files:
        file_path = samples_dir / file_name
        
        # Skip if file doesn't exist
        if not file_path.exists():
            print(f"Warning: Sample file {file_path} not found. Skipping.")
            continue
        
        try:
            # Load the tool definition from JSON
            with open(file_path, "r") as f:
                tool_data = json.load(f)
            
            # Add the tool to the registry
            tool = registry.add_tool(tool_data)
            print(f"Added tool: {tool.name} ({tool.tool_type})")
        
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in {file_path}")
        except ToolRegistryError as e:
            print(f"Error: {str(e)}")
    
    print("\nListing all tools in the registry:")
    tools = registry.list_tools()
    for tool in tools:
        print(f"- {tool.name} ({tool.tool_type}): {', '.join(tool.capabilities[:3])}...")
    
    print("\nChecking compatibility between tools:")
    try:
        # Check compatibility between Playwright and BeautifulSoup4
        compatible = registry.check_compatibility(["playwright", "beautifulsoup4"])
        print(f"playwright + beautifulsoup4: {'Compatible ✅' if compatible else 'Not compatible ❌'}")
        
        # Check compatibility between Playwright and ScraperAPI
        compatible = registry.check_compatibility(["playwright", "scraperapi"])
        print(f"playwright + scraperapi: {'Compatible ✅' if compatible else 'Not compatible ❌'}")
        
        # Find all tools compatible with Playwright
        print("\nTools compatible with playwright:")
        compatible_tools = registry.find_compatible_tools("playwright")
        for tool in compatible_tools:
            print(f"- {tool.name} ({tool.tool_type})")
        
    except ToolNotFoundError as e:
        print(f"Error: {str(e)}")
    except ToolRegistryError as e:
        print(f"Error: {str(e)}")
    
    print("\nDemo completed successfully!")


if __name__ == "__main__":
    main()
