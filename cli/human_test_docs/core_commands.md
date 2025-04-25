# The Brain CLI - Core Commands

This document provides step-by-step instructions for testing the core CLI functionality, with expected outputs for each command.

## Prerequisites

Before testing, ensure you have:

1. Python 3.9+ installed
2. All dependencies installed (`pydantic`, `typer`, `rich`, etc.)
3. The Brain project code on your local machine

## Core Commands

### Version Command

Check the version of the CLI:

```bash
python -m cli.app version
```

**Expected Output:**
```
The Brain CLI version: 0.1.0
```

### Help Command

Get help for the CLI:

```bash
python -m cli.app --help
```

**Expected Output:**
```
Usage: python -m cli.app [OPTIONS] COMMAND [ARGS]...

The Brain AI Scraper - Command Line Interface

Options:
  --json                       Output in JSON format for machine parsing
  -v, --verbose                Enable verbose output with detailed logs
  --install-completion         Install completion for the current shell.
  --show-completion            Show completion for the current shell, to copy it or customize the installation.
  --help                       Show this message and exit.

Commands:
  config  Manage configuration values and secrets
  scrape  Execute a scraping operation
  tools   Manage scraping tools
  version  Display the version of the CLI
```

### Global Options

The CLI supports global options that work with any command.

#### Verbose Mode

Verbose mode provides additional detailed information during command execution. It's enabled with the `--verbose` or `-v` flag and applies only to the command it's used with.

```bash
python -m cli.app --verbose version
```

**Expected Output:**
```
Verbose mode enabled
The Brain CLI version: 0.1.0
```

**What Verbose Mode Provides:**
- More detailed debugging information
- Full stack traces for errors
- Additional configuration and process details
- More information about what's happening under the hood

**Note:** Verbose mode is only active for the specific command it's used with. Each new command you run starts with verbose mode disabled unless you specify the flag again.

#### JSON Output

For scripting and automation, you can get output in JSON format using the `--json` flag:

```bash
python -m cli.app --json version
```

**Expected Output:**
```json
{"version": "0.1.0"}
```
