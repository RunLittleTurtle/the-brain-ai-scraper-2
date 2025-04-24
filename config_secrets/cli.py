#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLI interface for the config_secrets module.

This module provides command-line commands for managing the local .env file,
including setting, unsetting, and listing configuration values.
"""

import os
import sys
from typing import Optional, List

import typer
from rich.console import Console
from rich.table import Table

from config_secrets.core_secrets import (
    get_config,
    set_config_value,
    unset_config_value,
    list_config_keys
)
from config_secrets.exceptions import DotEnvWriteError, ConfigError

# Create CLI app
app = typer.Typer(help="Configuration and Secrets Management CLI for The Brain")
console = Console()


@app.command("set")
def set_config(
    key: str = typer.Argument(..., help="The environment variable name to set"),
    value: str = typer.Argument(..., help="The value to set"),
):
    """Set a configuration value in the .env file."""
    try:
        set_config_value(key, value)
        console.print(f"✅ Value for '[bold green]{key}[/bold green]' set successfully")
    except DotEnvWriteError as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        sys.exit(1)


@app.command("list")
def list_configs(
    show_all: bool = typer.Option(False, "--all", "-a", help="Show all values without masking"),
):
    """List all configuration keys and values from the .env file."""
    configs = list_config_keys(mask_sensitive=not show_all)
    
    if not configs:
        console.print("No configuration values found in .env file.")
        return
    
    table = Table(title="Configuration Values")
    table.add_column("Key", style="cyan")
    table.add_column("Value", style="green")
    
    for key, value in configs:
        table.add_row(key, value)
    
    console.print(table)


@app.command("unset")
def unset_config(
    key: str = typer.Argument(..., help="The environment variable name to remove"),
):
    """Remove a configuration value from the .env file."""
    try:
        unset_config_value(key)
        console.print(f"✅ Key '[bold green]{key}[/bold green]' removed successfully")
    except DotEnvWriteError as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        sys.exit(1)


@app.command("check")
def check_config(
    key: str = typer.Argument(..., help="The environment variable name to check"),
):
    """Check if a configuration value exists in the environment."""
    value = get_config(key)
    if value is not None:
        console.print(f"✅ Key '[bold green]{key}[/bold green]' exists in the environment")
    else:
        console.print(f"❌ Key '[bold red]{key}[/bold red]' not found in the environment")
        sys.exit(1)


if __name__ == "__main__":
    app()
