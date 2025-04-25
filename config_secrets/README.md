# Config Secrets Module Overview

## Purpose

The `config_secrets` module provides a unified interface for accessing configuration values and securely managing sensitive information across the application. It automatically loads from environment variables and `.env` files, ensuring consistent access to configuration and secrets throughout the application.

## Technical Specifications

- **Storage**: Environment variables with `.env` file fallback
- **Dependencies**: Uses python-dotenv for `.env` file management
- **Security**: Separation of regular config and sensitive secrets
- **API**: Function-based interface + CLI utilities

## Module Structure

```
config_secrets/
├── __init__.py         # Public API exports + auto-loading of .env
├── core_secrets.py     # Core implementation of config/secret management
├── models.py           # Data models for configuration
├── exceptions.py       # Custom exception classes
└── cli.py              # Command-line interface
```

## Key Components

### Core Functions (core_secrets.py)

- `load_dotenv_file()`: Load environment variables from .env file
- `get_config()`: Retrieve non-sensitive configuration values
- `get_secret()`: Retrieve sensitive information (API keys, credentials)
- `get_required_secret()`: Get mandatory secrets with error handling
- `set_config_value()`: Update values in the .env file
- `unset_config_value()`: Remove values from the .env file
- `list_config_keys()`: List all configuration values with optional masking

### Exception Handling

- `ConfigError`: Base exception for configuration-related errors
- `SecretNotFoundError`: Raised when a required secret is missing
- `DotEnvWriteError`: Raised when writing to the .env file fails

## Integration Points

- **Auto-loading**: Automatically loads `.env` file on module import
- **Tool Registry**: Provides secrets needed by tools registered in `tool_registry`
- **CLI**: Command-line interface for configuration management
- **Security**: Used throughout the application for secure credential management

## Usage Example

```python
from config_secrets import get_secret, get_required_secret, set_config_value

# Retrieve a configuration value with fallback
proxy_url = get_secret("PROXY_URL", default="http://localhost:8080")

# Get a required API key (raises exception if missing)
api_key = get_required_secret("API_KEY")

# Set a new configuration value
set_config_value("MAX_THREADS", "10")
```

## Design Principles

1. **Environment First**: Environment variables take precedence over .env files
2. **Secure by Default**: Sensitive values masked in logs and output
3. **Separation of Concerns**: Clear distinction between config and secrets
4. **Fail Fast**: Required secrets raise exceptions when missing
5. **Centralization**: Single source of truth for configuration

## Configuration Files

- **Environment Variables**: System environment variables
- **Local Environment**: `.env` file in the project directory
