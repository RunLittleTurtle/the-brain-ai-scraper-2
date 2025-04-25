# Tool Registry Module Overview

## Purpose

The `tool_registry` module provides a central registry for managing, querying, and discovering web scraping tools. It enables dynamic assembly of compatible scraping pipelines by tracking tool metadata, capabilities, and compatibility with other tools.

## Technical Specifications

- **Storage**: JSON-based storage (`~/.thebrain/config/tools.json`)
- **Core Model**: Pydantic-based `ToolMetadata` class for validation
- **API**: Python class interface + CLI commands
- **Error Handling**: Specialized exception hierarchy for registry operations

## Module Structure

```
tool_registry/
├── __init__.py          # Public API exports
├── core_tool.py         # Core ToolRegistry implementation
├── models.py            # Pydantic data models for tool metadata
├── exceptions.py        # Custom exception classes
├── cli.py               # Command-line interface
└── tools/               # Directory containing specific tool implementations
    └── [...tool implementations...]
```

## Key Components

### `ToolMetadata` (models.py)

A Pydantic model representing essential metadata for scraping tools, including:

- `name`: Unique identifier for the tool
- `description`: Purpose and functionality explanation
- `tool_type`: Functional category (browser, parser, etc.)
- `package_name`: Associated Python package
- `execution_mode`: Synchronous or asynchronous execution
- `capabilities`: List of key features provided
- `compatibilities`: List of compatible tools or tool types
- `incompatible_with`: Explicit incompatibilities 
- `required_config`: Configuration or secrets needed by the tool

### `ToolRegistry` (core_tool.py)

The central class managing the tool catalog, with methods for:

- Adding, updating, and removing tools
- Retrieving tool metadata
- Listing and filtering available tools
- Verifying compatibility between tools
- Finding compatible tools for pipeline construction

## Integration Points

- **Scraping Pipelines**: Provides compatible tools for constructing pipelines
- **CLI**: Command-line interface for tool registration and discovery
- **Config Integration**: Requires `config_secrets` module for tool configuration

## Usage Example

```python
from tool_registry import ToolRegistry
from tool_registry.models import ToolMetadata

# Create and register a tool
registry = ToolRegistry()
tool = ToolMetadata(
    name="playwright",
    description="Browser automation framework",
    tool_type="browser",
    package_name="playwright",
    execution_mode="async",
    capabilities=["javascript_rendering", "headless_mode"],
    required_config=["PROXY_URL"]
)
registry.add_tool(tool)

# Find compatible tools for a pipeline
compatible_tools = registry.find_compatible_tools("playwright")
```

## Design Principles

1. **Validation**: Strong validation of tool metadata using Pydantic
2. **Compatibility**: Tool compatibility checking for reliable pipeline assembly
3. **Discovery**: Automatic discovery of tools based on capabilities
4. **Extensibility**: Easy registration of new scraping tools
5. **Pipeline Support**: Intelligent tool selection for pipeline construction

## Configuration Files

- **Tool Registry**: `~/.thebrain/config/tools.json`
