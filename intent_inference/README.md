# Intent Inference Module

The Intent Inference module translates natural language user requests into structured specifications for web scraping tasks. It uses LangGraph for workflow management and LangSmith for tracing and visualization.

## Architecture

This module uses a LangGraph-based workflow with the following components:

1. **Intent Extraction**: Converts natural language to a structured `IntentSpec`
2. **Feedback Processing**: Updates existing specifications based on user feedback
3. **Validation**: Verifies the extracted intent meets quality standards
4. **URL Health Checking**: Validates that target URLs are accessible
5. **Human-in-the-Loop**: Provides user review and approval workflow

## Setting Up Environment

The module requires Python 3.13+ and the following environment variables for LangSmith integration:

```bash
# LangSmith for visualization (optional)
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
export LANGCHAIN_API_KEY=your_api_key_here
export LANGCHAIN_PROJECT=brain_ai_scraper

# LLM Configuration (required)
export OPENAI_API_KEY=your_openai_api_key_here
```

## Core API

The module provides two primary interfaces:

### 1. IntentInferenceAgent for programmatic use

```python
from intent_inference import IntentInferenceAgent
from intent_inference.models.context import ContextStore

# Create an agent with a persistent context
context = ContextStore()
agent = IntentInferenceAgent(context)

# Process a new request
intent_spec = agent.infer_intent("Find all product managers in Montreal on LinkedIn")

# Process feedback on previous spec
context.is_feedback = True
updated_spec = agent.infer_intent("Only include jobs from the last 7 days")
```

### 2. Direct functions for CLI or simple use cases

```python
from intent_inference import infer_intent_sync

# Simple synchronous call for new intent
intent_spec, needs_human = infer_intent_sync(
    "Find all product managers in Montreal on LinkedIn"
)

# For processing feedback
updated_spec, needs_human = infer_intent_sync(
    "Only include jobs from the last 7 days",
    previous_spec=intent_spec,
    is_feedback=True
)
```

## Viewing in LangGraph Studio

To visualize the workflow in LangGraph Studio, install the CLI:

```bash
pip install langgraph-cli
```

Then run:

```bash
langgraph dev
```

This will start a local server and open a browser window where you can see the graph visualization.

## Testing

Use the provided scripts to test the module:

```bash
# Quick test for imports and basic functionality
python scripts/quick_test.py

# Test with the CLI
python scripts/run_cli_test.py
```

## CLI Integration

The module is integrated with the main CLI application:

```bash
python -m cli.app scrape "Find all product managers in Montreal on LinkedIn"
```

## Intent Specification

The `IntentSpec` Pydantic model captures:

- **Target URLs**: The websites to scrape
- **Fields to Extract**: What data to collect
- **Technical Requirements**: JavaScript rendering, etc.
- **Constraints**: Time periods, location filters, etc.
- **Validation Status**: Whether human review is needed
- **URL Health**: Accessibility status of targets
- **Critique History**: Feedback from LLM or users

## Development Notes

1. Keep files under 250 lines by refactoring larger modules
2. Use strict type hints and docstrings
3. No hardcoded secrets - use environment variables via `os.getenv()`
4. Test thoroughly with various query types and feedback scenarios
