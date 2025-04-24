# The Brain AI Scraper

An intelligent web scraping system that dynamically selects the most appropriate tools for each specific scraping task. The Brain understands user intent, builds optimal pipelines, executes scraping operations, and learns from successes and failures.

## Core Features

- **Intelligent Intent Parsing**: Converts both structured commands and natural language requests into standardized specifications
- **Dynamic Pipeline Building**: Selects and configures the right tools based on website characteristics
- **Self-Healing Capabilities**: Detects failures and adapts its approach automatically
- **Collective Learning**: Improves over time based on user feedback

## Project Structure

The project follows a modular architecture with clear separation of concerns:

```
the-brain-ai-scraper-2/
├── tool_registry/       # Plugin catalog of scraping tools with metadata
├── config_secrets/      # Centralized secrets & config management (coming soon)
├── cli/                 # Command-line interface for user interaction (coming soon)
├── progress_tracker/    # Real-time status updates and logging (coming soon)
├── api_gateway/         # REST API endpoint (coming soon)
└── samples/             # Sample tool definitions for testing
```

## Getting Started

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)

### Installation

1. Clone the repository
   ```bash
   git clone https://github.com/RunLittleTurtle/the-brain-ai-scraper-2.git
   cd the-brain-ai-scraper-2
   ```

2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

### Usage

#### Tool Registry

The first implemented module is the `tool_registry`, which provides a catalog of scraping tools and their compatibility information.

```python
# Example: Using the Tool Registry
from tool_registry import ToolRegistry

# Initialize the registry
registry = ToolRegistry()

# Add a tool from a JSON file
with open("samples/playwright.json", "r") as f:
    tool_data = json.load(f)
    tool = registry.add_tool(tool_data)

# Check compatibility between tools
compatible = registry.check_compatibility(["playwright", "beautifulsoup4"])
print(f"Compatible: {compatible}")
```

## Development Roadmap

The project is being developed in a strict priority order:

1. **P0 (Core Foundations)**
   - [x] tool_registry - Plugin catalog of scraping tools
   - [ ] config_secrets - Centralized secrets & configuration management
   - [ ] cli - Command-line interface for user interaction
   - [ ] progress_tracker - Real-time status updates and logging
   - [ ] api_gateway - REST API endpoint

2. **P1-P3 (Coming Soon)**
   - intent_inference, pipeline_builder, executor, evaluator, knowledge_base, aggregator

## License

This project is licensed under the MIT License - see the LICENSE file for details.