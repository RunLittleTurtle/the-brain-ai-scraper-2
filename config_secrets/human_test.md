# The Brain AI Scraper - Config Secrets Module

## Human Test Guide

This document provides a comprehensive guide for manually testing the `config_secrets` module, which handles environment variables, configuration values, and secrets for The Brain AI Scraper.

## Prerequisites

1. A virtual environment with all dependencies installed (see [requirements.txt](../requirements.txt)):
   ```
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. Basic understanding of environment variables and the `.env` file concept.

## Overview of Commands

The `config_secrets` module provides the following CLI commands:

- `set`: Set a configuration value in the .env file
- `list`: List all configuration keys and values from the .env file
- `unset`: Remove a configuration value from the .env file
- `check`: Check if a configuration value exists in the environment

## Test Scenarios

### 1. Setting Configuration Values

Test setting regular and sensitive values in the `.env` file.

```bash
# Set a regular configuration value
python -m config_secrets.cli set API_URL https://api.example.com

# Set a sensitive value (will be masked when displayed)
python -m config_secrets.cli set API_KEY sk_test_abcdefghijklmnopqrstuvwxyz

# Set an additional test variable
python -m config_secrets.cli set TEST_VAR "Hello World"
```

**Expected Output:**
```
✅ Value for 'API_URL' set successfully
✅ Value for 'API_KEY' set successfully
✅ Value for 'TEST_VAR' set successfully
```

### 2. Listing Configuration Values

Test listing all values, which should mask sensitive values.

```bash
python -m config_secrets.cli list
```

**Expected Output:**
```
  Configuration Values  
┏━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Key      ┃ Value                  ┃
┡━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━┩
│ API_URL  │ https://api.example.com│
│ API_KEY  │ sk******************* │
│ TEST_VAR │ Hello World           │
└──────────┴────────────────────────┘
```

Note: The API_KEY value is masked for security reasons.

### 3. Checking Configuration Existence

Test checking if configuration values exist.

```bash
# Check an existing value
python -m config_secrets.cli check API_URL

# Check a non-existent value
python -m config_secrets.cli check NONEXISTENT_KEY
```

**Expected Output:**
```
✅ Key 'API_URL' exists in the environment
❌ Key 'NONEXISTENT_KEY' does not exist in the environment
```

### 4. Removing Configuration Values

Test removing configuration values.

```bash
# Remove a value
python -m config_secrets.cli unset TEST_VAR

# List to verify it's gone
python -m config_secrets.cli list
```

**Expected Output for unset:**
```
✅ Key 'TEST_VAR' removed successfully
```

**Expected Output for list after unset:**
```
  Configuration Values  
┏━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Key      ┃ Value                  ┃
┡━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━┩
│ API_URL  │ https://api.example.com│
│ API_KEY  │ sk******************* │
└──────────┴────────────────────────┘
```

### 5. Testing with Actual Tool Registry Integration

Test how `config_secrets` works with tool requirements from the `tool_registry`:

```bash
# Add ScraperAPI tool that requires an API key
python -m tool_registry.cli add tool_registry/tools/scraperapi.json

# List all tools to verify it was added
python -m tool_registry.cli list

# After adding a tool to the registry, you can use the config_secrets module
# to set up any required configuration values for it
```

**Expected Output for List:**
```
  Tools in Registry  
┏━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Name         ┃ Description                                       ┃
┡━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ scraperapi   │ API service for web scraping with anti-detection │
│              │ and CAPTCHA solving                              │
└──────────────┴────────────────────────────────────────────────────┘
```

The tool definition includes `required_config` which specifies what environment variables the tool needs to function properly.

Now set the required configuration:

```bash
# Set the required API key
python -m config_secrets.cli set SCRAPERAPI_KEY your_scraperapi_key_here
```

**Expected Output:**
```
✅ Value for 'SCRAPERAPI_KEY' set successfully
```

## Using in Python Code

### Demo Script

A complete demo script has been created to show how to use `config_secrets` with `tool_registry`. This demonstrates a real-world usage pattern:

```bash
source venv/bin/activate
python examples/config_secrets_demo.py
```

**Demo Script Output (example):**
```
=== Config Secrets Demo ===

API URL: https://api.example.com
API KEY: sk_t**************************wxyz
ScraperAPI Key is set (24 characters)

=== Tool Required Configurations ===

Tool: scraperapi
Required config: ['SCRAPERAPI_KEY']
  ✅ SCRAPERAPI_KEY is set

=== Required Secret Demo ===
Expected error: Required secret 'NONEXISTENT_KEY' not found in environment variables

Demo complete!
```

The demo script (`examples/config_secrets_demo.py`) shows how to:

1. Import and use functions from the `config_secrets` module
2. Get regular and sensitive configuration values
3. Properly mask sensitive API keys for display
4. Load the tool registry and check which tools need configuration
5. Verify if required configuration values are set
6. Handle errors when required secrets are missing
2. Get regular and sensitive configuration values
3. Properly mask sensitive values for display
4. Load the tool registry and check for required configs
5. Handle missing required secrets with proper error handling

### Viewing Actual Secret Values (Development Only)

For development and debugging purposes, a special script is provided to view the actual content of secrets. **Note: This should only be used in development environments and never in production.**

```bash
# View a specific secret key
python examples/view_secrets.py --key SCRAPERAPI_KEY

# View all configuration values (including secrets)
python examples/view_secrets.py --all
```

**Expected Output for viewing a specific key:**
```
⚠️  WARNING: This tool displays sensitive information for debugging only ⚠️

SCRAPERAPI_KEY = your_scraperapi_key_here
```

**Expected Output for viewing all keys:**
```
⚠️  WARNING: This tool displays sensitive information for debugging only ⚠️

--- Configuration Values (including secrets) ---
API_URL = https://api.example.com
API_KEY = sk_test_abcdefghijklmnopqrstuvwxyz
SCRAPERAPI_KEY = your_scraperapi_key_here
```

## Troubleshooting

### Common Issues:

1. **Empty List Output**: If `list` shows no values, your `.env` file might be empty or not exist. Try setting a value first.

2. **Permission Issues**: If you get permission errors, ensure you have write access to the directory where the `.env` file is located.

3. **Module Not Found**: Ensure you are in the correct directory and have activated your virtual environment.

4. **Value Not Updated**: If a value doesn't seem to update, try setting it again or check if there are environment variables set at the system level that might be overriding your `.env` file.

## Clean Up

After testing, you can clean up the test values:

```bash
python -m config_secrets.cli unset API_URL
python -m config_secrets.cli unset API_KEY
python -m config_secrets.cli unset SCRAPERAPI_KEY
```

---

This test guide covers the basic functionality of the `config_secrets` module. For more advanced usage and integration with other modules, refer to the main documentation.
