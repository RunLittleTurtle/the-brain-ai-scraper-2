# The Brain CLI - Human Testing Guide

This document provides a complete guide for human testing of the CLI module functionality. It references detailed documentation for specific command groups with expected outputs.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Documentation Structure](#documentation-structure)
3. [Automated Testing](#automated-testing)
4. [Complete Testing Workflow](#complete-testing-workflow)

## Prerequisites

Before testing, ensure you have:

1. Python 3.9+ installed
2. All dependencies installed (`pydantic`, `typer`, `rich`, etc.)
3. The Brain project code on your local machine

## Documentation Structure

The CLI testing documentation is organized into the following files:

1. **[Core Commands](./core_commands.md)** - Testing the version, help, and global options
2. **[Tool Management Commands](./tool_commands.md)** - Testing the `tools` command group
3. **[Configuration Commands](./config_commands.md)** - Testing the `config` command group
4. **[Scraping Commands](./scrape_commands.md)** - Testing the `scrape` command group

Each documentation file contains:
- Step-by-step instructions for testing specific features
- Example commands to run
- Expected output for each command
- Common error scenarios and their handling

## Automated Testing

You can run the automated tests for the CLI module with:

```bash
python -m cli.tests.test_commands
```

**Expected Output:**
```
Running CLI module tests...
✅ Version command test passed
✅ Tools list command test passed
✅ Tools add/remove test passed
✅ Tools compatibility check test passed
✅ Scrape command test passed
✅ Config commands test passed
✅ All CLI module tests passed!
```

## Complete Testing Workflow

For a comprehensive test of the CLI, follow these steps:

1. **Start with Core Commands**:
   - Run all commands in [core_commands.md](./core_commands.md)
   - Verify all outputs match expected results

2. **Test Tool Management**:
   - Run all commands in [tool_commands.md](./tool_commands.md)
   - Verify that tools can be listed, added, and removed as expected

3. **Test Configuration Management**:
   - Run all commands in [config_commands.md](./config_commands.md)
   - Verify that configs can be set, listed, and removed as expected

4. **Test Scraping Functionality**:
   - Run all commands in [scrape_commands.md](./scrape_commands.md)
   - Verify that scraping works with various input methods and formats

5. **Verify Error Handling**:
   - Try invalid commands and inputs to test error handling
   - Example: `python -m cli.app tools check-compat nonexistent-tool`
   - The CLI should provide clear, helpful error messages

6. **Run Automated Tests**:
   - Run the full test suite to verify all functionality programmatically
   - `python -m cli.tests.test_commands`

After completing all tests, document any issues or unexpected behaviors for further investigation.
