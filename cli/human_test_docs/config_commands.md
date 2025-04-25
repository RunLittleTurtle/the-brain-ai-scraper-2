# The Brain CLI - Configuration Commands

This document provides step-by-step instructions for testing the configuration management functionality, with expected outputs for each command.

## Configuration Commands

### Set Configuration

Set a configuration value:

```bash
python -m cli.app config set TEST_CONFIG test_value
```

**Expected Output:**
```
✓ Configuration value 'TEST_CONFIG' set to '****'
```

Securely set a sensitive configuration value (password will be prompted):

```bash
python -m cli.app config set API_KEY --secure
```
python -m cli.app config set ANY_NAME_OF_KEY --secure 
**Expected Output:**
```
Enter value for API_KEY: [hidden input]
✓ Configuration value 'API_KEY' set to '****'
```

### List Configuration

List all configuration values:

```bash
python -m cli.app config list
```

**Expected Output:**
```
Found X configuration values
                Configuration Values                 
┏━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Key            ┃ Value                            ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ TEST_CONFIG    │ te**                             │
│ API_KEY        │ ap**                             │
└────────────────┴──────────────────────────────────┘

Note: Values are masked for security. Use --show-values to see actual values.
```

Show unmasked values (with warning about sensitive information):

```bash
python -m cli.app config list --show-values
```

**Expected Output:**
```
⚠️ Warning: This will display sensitive information. Use with caution.

Found X configuration values
                Configuration Values                 
┏━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Key            ┃ Value                            ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ TEST_CONFIG    │ test_value                       │
│ API_KEY        │ api_key_value                    │
└────────────────┴──────────────────────────────────┘
```

### Remove Configuration

Remove a configuration value (with confirmation):

```bash
python -m cli.app config unset TEST_CONFIG
```

**Expected Output:**
```
Are you sure you want to remove configuration 'TEST_CONFIG'? [y/N]: y
✓ Configuration value 'TEST_CONFIG' removed successfully
```

Force remove without confirmation:

```bash
python -m cli.app config unset TEST_CONFIG --force
```

**Expected Output:**
```
✓ Configuration value 'TEST_CONFIG' removed successfully
```

### Handling Non-existent Keys

The command will now gracefully handle attempts to unset non-existent keys:

```bash
python -m cli.app config unset NON_EXISTENT_KEY
```

**Expected Output:**
```
Warning: Key 'NON_EXISTENT_KEY' doesn't exist in configuration
```
