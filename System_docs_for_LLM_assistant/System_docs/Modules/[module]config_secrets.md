# [Module] config_secrets

config_secrets/
  ├── __init__.py          # Loads config on import, exports key functions
  ├── core_secrets.py      # Main logic for loading .env and retrieving values
  ├── exceptions.py        # Custom exceptions (e.g., SecretNotFoundError)
  ├── models.py            # (Optional V1 Placeholder) Pydantic models if needed later
  ├── cli.py               # CLI interface for local .env management
  └── tests/               # Unit tests
      ├── __init__.py
      └── test_core_secrets.py # Tests for loading and retrieving secrets

## Description

The `config_secrets` module is the centralized point for managing the application's configuration and sensitive secrets (API keys, passwords, connection URLs). It ensures the application loads configuration from the appropriate source: the `.env` file for local development and environment variables injected by the platform (e.g., Fly.io Secrets) for deployments. This module provides simple and secure functions (`get_config`, `get_secret`) so that other components of "The Brain" can access necessary values without worrying about their origin. It also includes a basic CLI **to manage the local `.env` file only**.

## Main Objective for the LLM

Implement a **reliable and secure** system to provide configurations and secrets to the application, using **`os.getenv()` as the single source of truth** after an initial (and optional) load of the local `.env` file via `python-dotenv`. The goal is to have a unique access interface (`get_config`/`get_secret`) that works transparently, whether the application is running locally or in deployment, without requiring modification of the calling code.

## Dependencies

*   **External:** `python-dotenv` (to load the local `.env` file).
*   **Internal:** No strict dependencies *required* for its core functionality. However, this module is *used by* virtually all other modules that require configuration or API keys. (See notes on future `tool_registry` integration).

## Inputs / Outputs

*   **Inputs (CLI - Local Only):**
    *   `brain config set <KEY> <VALUE>`: Adds or updates an entry in the **local** `.env` file.
    *   `brain config list`: Lists keys present in the **local** `.env` file, with sensitive values masked.
    *   `brain config unset <KEY>`: Removes a key from the **local** `.env` file.
    *   `brain config check <KEY>`: Checks if a key exists (reads from environment via `os.getenv`).
*   **Inputs (Internal - Loading):**
    *   `.env` file at the project root (loaded automatically on startup if present).
    *   System environment variables (take precedence over `.env`, primary source in deployment via Fly.io).
*   **Inputs (API Python - Internal Functions/Methods):**
    *   `config_secrets.get_config(key: str, default: Any = None) -> Optional[str]`: Retrieves a non-sensitive configuration value from environment variables.
    *   `config_secrets.get_secret(key: str, default: Any = None) -> Optional[str]`: Retrieves a sensitive secret value from environment variables. Potentially raises an exception if not found and no default is provided.
*   **Outputs (CLI):**
    *   Status messages (success/failure) for `set`/`unset`.
    *   Formatted list of keys with masked values for `list` (e.g., `OPENAI_API_KEY=sk-*****`).
    *   Confirmation message ("Key '<KEY>' exists." or "Key '<KEY>' not found.") for `check`.
*   **Outputs (API Python):**
    *   The environment variable value as a `str`.
    *   The `default` value if the key is not found.
    *   `None` if the key is not found and `default` is `None`.
    *   May raise `SecretNotFoundError` if a required key is missing and no `default` is handled.
*   **Storage:**
    *   `.env` file (local development only, **NEVER commit to Git**). Managed via CLI commands.
    *   Environment variables (in production/deployment, managed via platform like Fly.io).

## Encapsulated Features

*   **`.env` Loading:** Uses `python-dotenv` to load variables from `.env` into the local environment at application startup (typically in `__init__.py` or via an early explicit call).
*   **Unified Access:** Provides `get_config` and `get_secret` functions that read directly from `os.getenv()`, ensuring consistency between local and deployed environments.
*   **Absence Handling:** Allows providing default values or raising exceptions if required configuration/secrets are missing.
*   **Local CLI Management:** Offers simple commands to manipulate the local `.env` file during development (`set`, `list`, `unset`, `check`).
*   **Security:** Never directly exposes storage mechanisms and promotes reading via environment variables. CLI listing masks sensitive values.

## Pydantic Schema & JSON Format

A dedicated `models.py` file is included as a placeholder for consistency, but it is **not actively used in V1** for schema validation within this module. In the future (V2+), it could hold Pydantic models to validate the overall expected application configuration structure read from the environment, if needed.

## Concrete Examples

**Local `.env` file:**

```dotenv
# Database Configuration
DATABASE_URL=postgresql://user:pass@host:port/dbname
REDIS_URL=redis://host:port

# API Keys
OPENAI_API_KEY=sk-local-xxxxxxxxxx
SCRAPERAPI_KEY=local_scraper_key_yyyyyyy
```

```
**CLI Usage (Local):**

```bash
brain config set MY_NEW_VAR test_value  # Adds MY_NEW_VAR=test_value to .env
brain config list
# Output:
# DATABASE_URL=postgresql://***:***@host:port/dbname
# REDIS_URL=redis://host:port
# OPENAI_API_KEY=sk-**********
# SCRAPERAPI_KEY=local_*********
# MY_NEW_VAR=test_value
brain config check OPENAI_API_KEY
# Output: Key 'OPENAI_API_KEY' exists.
brain config unset MY_NEW_VAR           # Removes the line from .env
```

**Python Code Usage:**

```python
import os
from config_secrets import get_secret, get_config

# Assuming .env was loaded or environment variables are set
db_url = get_config("DATABASE_URL")
openai_key = get_secret("OPENAI_API_KEY")
optional_setting = get_config("NON_EXISTENT_VAR", default="fallback")

print(f"DB URL: {db_url}")
print(f"OpenAI Key: {'Exists' if openai_key else 'Not Found'}") # Avoid printing secret
print(f"Optional: {optional_setting}")

# Example in another module (e.g., pipeline_builder using a tool from tool_registry)
# tool_metadata = registry.get_tool("scraperapi")
# for required_key in tool_metadata.required_config:
#     if not get_secret(required_key):
#          raise ConfigurationError(f"Secret '{required_key}' is required for tool '{tool_metadata.name}' but not found.")
# # Proceed to use the tool...
```

## Useful APIs for Other Modules

*   `get_config(key: str, default: Any = None) -> Optional[str]`: To retrieve non-sensitive configurations.
*   `get_secret(key: str, default: Any = None) -> Optional[str]`: To retrieve secrets (API keys, passwords). Use cautiously to avoid logging values.

## CLI Regression Tests (Focus Local `.env`)

*   `brain config set TEST_KEY 123` (Verify `TEST_KEY=123` is added/modified in `.env`).
*   `brain config list` (Verify `TEST_KEY=123` appears, and keys like `API_KEY` are masked).
*   `brain config check TEST_KEY` (Verify it reports the key exists).
*   `brain config unset TEST_KEY` (Verify the `TEST_KEY` line is removed from `.env`).
*   `brain config list` (Verify `TEST_KEY` no longer appears).
*   `brain config check TEST_KEY` (Verify it reports the key not found).

## Notes for the LLM

*   The core of this module is simple: load `.env` (if local) then use `os.getenv()` for all retrieval. Complexity lies in proper error handling (missing key) and the CLI for the local `.env` file.
*   **NEVER** implement logic that writes secrets to files other than the local `.env` via explicit CLI commands. Application code must **only read** via `os.getenv()`.
*   Ensure the `load_dotenv()` function from `python-dotenv` is called **only once** and **very early** in the application lifecycle (e.g., in the module's `__init__.py` or the main application entry point).
*   The `set`/`unset` CLI commands directly modify the `.env` file. Handle cases where the file doesn't exist or permissions are incorrect.
*   **Integration with `tool_registry`:** Although `config_secrets` doesn't directly depend on `tool_registry`, other modules (like `pipeline_builder` or `executor`) will use `config_secrets.get_secret(key)` to check if secrets listed in a tool's `required_config` (from `tool_registry`) are actually available before attempting to use that tool.

## Features to Develop for `config_secrets` Module

> **Statuses**: `[Backlog]`, `[To_Do_Next]`, `[LLM_In_Progress]`, `[LLM_Test]`, `[LLM_Testing]`, `[Human_Review]`, `[Human_Done]`

This module is **fundamental (P0)** and should be one of the first implemented.

### 1. Core Logic and Exceptions

- **1.1 Custom Exceptions in `exceptions.py`** `[Human_Review]`
  Create `SecretNotFoundError` (perhaps inheriting from `KeyError` or `ValueError`).
- **1.2 `.env` Loading in `core_secrets.py` (or `__init__.py`)** `[Human_Review]`
  Implement a function (e.g., `load_configuration`) using `load_dotenv()` from `python-dotenv`. Ensure it doesn't reload unnecessarily and handles the absence of the `.env` file gracefully (this is normal in production). Call this function upon module import or very early.
- **1.3 Access Functions in `core_secrets.py`** `[Human_Review]`
  Implement `get_config(key, default=None)` and `get_secret(key, default=None)`. They should simply wrap `os.getenv(key, default)`. `get_secret` might add warning or error logic if the key is absent and no `default` is provided, based on the decided error handling policy. Export these functions in `__init__.py`.

### 2. CLI Interface (For Local `.env` Management)

- **2.1 `brain config set` command in `cli.py`** `[Human_Review]`
  Use Typer. Must read the `.env` file, add/modify the `KEY=VALUE` line, and rewrite the file. Handle cases where the file doesn't exist. Consider using existing libraries for modifying `.env` files (like `python-dotenv`'s own manipulation functions if suitable) or simple line reading/writing logic.
- **2.2 `brain config list` command in `cli.py`** `[Human_Review]`
  Read the `.env` file, iterate through keys, and display `KEY=masked_value` for keys containing terms like `KEY`, `SECRET`, `PASSWORD`, `TOKEN` (list to define), and `KEY=value` for others.
- **2.3 `brain config check` command in `cli.py`** `[Human_Review]`
  Use Typer. Implement by calling `os.getenv(KEY)` and checking if the result is not `None`. Print a clear confirmation message.
- **2.4 `brain config unset` command in `cli.py`** `[Human_Review]`
  Read the `.env` file, filter out the line corresponding to `KEY`, and rewrite the file without that line.

### 3. Validation and Tests

- **3.1 Unit Tests in `tests/test_core_secrets.py`** `[Human_Review]`
  Test `get_config`/`get_secret` by simulating environment variables (using `unittest.mock.patch.dict` or `pytest-env`). Test cases where the key exists, doesn't exist, with and without `default`. Test loading (mock `load_dotenv`). Test exceptions.
- **3.2 CLI Tests (more integration)** `[Human_Review]`
  Test the CLI commands by manipulating a temporary `.env` file to verify `set`, `list` (with masking), `check`, and `unset` operations.

### 4. Documentation

- **4.1 Docstrings** `[Human_Review]`
  Add clear docstrings to functions and CLI commands.

## Secret Management Rules

*   **Priority:** System environment variables > Variables loaded from `.env`. `python-dotenv` handles this by default (`override=False`).
*   **Security:** Never log values returned by `get_secret`. Use masking for `brain config list`. `.env` **MUST** be in `.gitignore`.
*   **Simplicity:** No database for secrets in V1. Stick to local `.env` and injected environment variables.

## Development Flow

1.  Implement core logic (1.1, 1.2, 1.3) and unit tests (3.1). This is the **critical P0** core.
2.  Implement the essential CLI commands `set`, `list`, `check` (2.1, 2.2, 2.3) to facilitate local development.
3.  Complete with `unset` command (2.4) and CLI tests (3.2).
4.  Add documentation (4.1).

