# The Brain CLI Module

## Overview

The CLI module provides a command-line interface for "The Brain" project, enabling users to interact with the scraping system through intuitive commands. It serves as a thin wrapper around other modules while providing rich, interactive terminal output.

## Technical Specifications

- **Language:** Python 3.13+
- **Framework:** Typer, Rich (for terminal formatting)
- **Type Hints:** All code uses strict type hints
- **Interactive Components:** Prompt_toolkit/Inquirer for interactive menus
- **Output Formats:** Human-readable (default) and JSON (with --json flag)

## Module Structure

```
cli/
├── __init__.py                # Public exports
├── app.py                     # Main CLI application (Typer app)
├── commands/                  # Command implementations 
│   ├── config/                # Configuration commands
│   ├── scrape/                # Scraping commands
│   └── tool/                  # Tool registry commands
├── formatters/                # Output formatting
│   ├── json_formatter.py      # JSON output
│   └── table_formatter.py     # Human-readable tables
├── interactive/               # Interactive components
│   └── prompts.py             # User prompts
└── mocks/                     # Mock implementations
    ├── mock_intent_inference.py
    ├── mock_pipeline_builder.py
    └── mock_executor.py
```

## Installation

The CLI is part of the main project package and will be available once the project is installed:

```bash
pip install -e .
```

## Usage

### Global Options

All commands support these global options:

- `--json`: Output in JSON format (for machine parsing)
- `--verbose`: Enable verbose output with detailed logs

### Tool Management

```bash
# List all registered tools
brain tools list

# Add a new tool
brain tools add --name "tool-name" --description "Tool description" --type "parser" --package "package-name" --capability "capability1" --capability "capability2"

# Check compatibility between tools
brain tools check-compat tool1 tool2

# Remove a tool
brain tools remove tool-name
```

### Configuration Management

```bash
# Set a configuration value
brain config set KEY_NAME value

# Set a sensitive value (will prompt securely)
brain config set API_KEY --secure

# List all configuration values
brain config list

# Show actual values (instead of masked)
brain config list --show-values

# Remove a configuration value
brain config unset KEY_NAME
```

### Scraping Operations

```bash
# Scrape with free-text description
brain scrape "Get the price and title from https://example.com"

# Scrape with structured arguments
brain scrape --url https://example.com --extract price,title

# Scrape with JavaScript rendering enabled
brain scrape --url https://example.com --extract price,title --javascript
```

## Examples

### Example 1: Tool Management Workflow

```bash
# List all available tools
brain tools list

# Add a new scraping tool
brain tools add --name "custom-browser" --type "browser" --package "custombrowser" --description "Custom browser implementation" --capability "javascript_rendering" --capability "headless_mode"

# Check if the new tool is compatible with a parser
brain tools check-compat custom-browser beautifulsoup4
```

### Example 2: Scraping Workflow

```bash
# Set required API key for a tool
brain config set SCRAPERAPI_KEY --secure

# Execute a scrape using natural language
brain scrape "Get the price and description from https://example.com/product"

# Export the results as JSON
brain scrape --url https://example.com/product --extract price,description --json > results.json
```

## Integration Points

- **tool_registry**: The CLI directly interacts with the tool registry to list, add, and manage tools
- **config_secrets**: Uses this module to securely store and retrieve configuration values
- **Future modules**: Will integrate with progress_tracker, intent_inference, pipeline_builder, and executor modules as they become available

## Mocks

The CLI includes mock implementations of future modules to enable testing and development:

- **mock_intent_inference**: Simulates natural language understanding
- **mock_pipeline_builder**: Creates mock scraping pipelines
- **mock_executor**: Simulates pipeline execution with progress updates

## Testing

To run the CLI tests:

```bash
pytest tests/cli/
```

The test suite verifies all command functionality, option handling, and integration with available modules.

## Error Handling

All commands include robust error handling with:

- Descriptive error messages
- Suggestions for corrective actions
- JSON-formatted errors when using --json flag
- Detailed error information in verbose mode

## Development Status

This module is currently in the Testing phase with all core functionality implemented:

1. Core Framework - ✅ Complete
2. Tool Commands - ✅ Complete
3. Config Commands - ✅ Complete
4. Basic Scraping - ✅ Complete

Future development will add integrations with other modules as they become available.
