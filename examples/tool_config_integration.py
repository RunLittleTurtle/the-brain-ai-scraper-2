#!/usr/bin/env python3
"""
Integration test script that demonstrates how tool_registry and config_secrets
work together to validate tool configurations.
"""
import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tool_registry import ToolRegistry
from config_secrets import get_config, set_config_value, get_secret

def find_tools_missing_config():
    """Find tools that require configuration but are missing it."""
    registry = ToolRegistry()
    tools = registry.list_tools()
    
    missing_configs = []
    
    for tool in tools:
        if hasattr(tool, "required_config") and tool.required_config:
            print(f"\n🔍 Checking tool: {tool.name}")
            print(f"  Required config keys: {tool.required_config}")
            
            for config_key in tool.required_config:
                value = get_config(config_key)
                if not value:
                    print(f"  ❌ Missing required config: {config_key}")
                    missing_configs.append((tool.name, config_key))
                else:
                    masked_value = "***" if len(value) < 8 else f"{value[:3]}...{value[-3:]}"
                    print(f"  ✅ {config_key} is set: {masked_value}")
    
    return missing_configs

def main():
    """Main function demonstrating the integration between modules."""
    print("=== Tool Registry + Config Secrets Integration ===\n")
    
    # 1. Check for tools with missing configuration
    print("Checking for tools with missing required configuration...")
    missing_configs = find_tools_missing_config()
    
    # 2. Fix missing configurations interactively
    if missing_configs:
        print("\n=== Missing Configurations Detected ===")
        print("The following tools have missing configuration:")
        
        for tool_name, config_key in missing_configs:
            print(f"Tool '{tool_name}' requires '{config_key}'")
            
            # Simulate setting a placeholder value
            placeholder = f"placeholder_{config_key}_value"
            set_config_value(config_key, placeholder)
            print(f"✅ Set placeholder value for {config_key}")
    
        # Verify all configs are now set
        print("\n=== Verification After Setting Values ===")
        missing_after_fix = find_tools_missing_config()
        
        if not missing_after_fix:
            print("\n✅ All tools now have their required configuration values set!")
        else:
            print("\n❌ Some tools still have missing configuration")
    else:
        print("\n✅ All tools already have their required configuration values set!")

if __name__ == "__main__":
    main()
