#!/usr/bin/env python3
"""
Demo script showing how to use the config_secrets module with tool_registry.
This example demonstrates retrieving configuration values for tools.
"""

import sys
import os

# Add the parent directory to the Python path so we can import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  

from config_secrets import get_config, get_secret, get_required_secret
from tool_registry import ToolRegistry

def main():
    """Main demo function for config_secrets module."""
    print("=== Config Secrets Demo ===\n")
    
    # Get regular configuration values
    api_url = get_config("API_URL")
    print(f"API URL: {api_url}")
    
    # Get sensitive values (with masking for display)
    api_key = get_secret("API_KEY")
    if api_key:
        masked_key = f"{api_key[:4]}{'*' * (len(api_key) - 8)}{api_key[-4:]}" if len(api_key) > 8 else "****"
        print(f"API KEY: {masked_key}")
    
    # Check for ScraperAPI configuration
    scraperapi_key = get_config("SCRAPERAPI_KEY")
    if scraperapi_key:
        print(f"ScraperAPI Key is set ({len(scraperapi_key)} characters)")
    
    # Load tool registry and check for required configs
    try:
        registry = ToolRegistry()
        tools = registry.list_tools()
        
        print("\n=== Tool Required Configurations ===")
        if not tools:
            print("No tools found in registry")
        
        for tool in tools:
            if hasattr(tool, "required_config") and tool.required_config:
                print(f"\nTool: {tool.name}")
                print(f"Required config: {tool.required_config}")
                
                for config_key in tool.required_config:
                    value = get_config(config_key)
                    if value:
                        print(f"  ✅ {config_key} is set")
                    else:
                        print(f"  ❌ {config_key} is not set")
    
    except Exception as e:
        print(f"Error loading tool registry: {str(e)}")
    
    # Demonstrate required_secret with error handling
    print("\n=== Required Secret Demo ===")
    try:
        required_key = get_required_secret("NONEXISTENT_KEY")
    except Exception as e:
        print(f"Expected error: {str(e)}")
    
    print("\nDemo complete!")

if __name__ == "__main__":
    main()
