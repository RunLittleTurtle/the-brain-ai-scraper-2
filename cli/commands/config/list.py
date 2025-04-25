#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Implementation of the 'brain config list' command.

This module provides functionality to list all configuration values and secrets.
"""

from typing import Optional, List
import typer
from rich.console import Console
from rich.table import Table

import config_secrets
from cli.formatters.json_formatter import format_json
from cli.formatters.table_formatter import format_table
from cli.app import state

console = Console()

def list_config(
    show_values: bool = typer.Option(
        False,
        "--show-values",
        help="Show actual values instead of masking them",
    ),
    filter_keys: Optional[List[str]] = typer.Option(
        None,
        "--filter",
        "-f", 
        help="Only show config keys containing this substring (can specify multiple)",
    ),
) -> None:
    """
    List all configuration values and secrets.
    
    This command lists all configuration values from the .env file.
    By default, values are masked for security. Use --show-values to see actual values.
    
    Examples:
        brain config list
        brain config list --show-values
        brain config list --filter API --filter KEY
    """
    try:
        # Get all config keys and values
        config_list = config_secrets.list_config_keys(mask_sensitive=not show_values)
        
        # Apply filter if specified
        if filter_keys:
            config_list = [
                (key, value) for key, value in config_list
                if any(f.lower() in key.lower() for f in filter_keys)
            ]
        
        # Output in JSON format if requested
        if state.json_output:
            config_dict = {key: value for key, value in config_list}
            typer.echo(format_json(config_dict))
            return
        
        # Output in human-readable format
        if not config_list:
            console.print("[yellow]No configuration values found[/yellow]",
                          f"{'with specified filters' if filter_keys else ''}")
            return
        
        # Create table with config details
        table = Table(title="Configuration Values")
        table.add_column("Key", style="bold cyan")
        table.add_column("Value")
        
        for key, value in config_list:
            table.add_row(key, value)
        
        # Print summary and table
        console.print(f"[green]Found {len(config_list)} configuration values[/green]")
        console.print(table)
        
        # Add note about masking if values are masked
        if not show_values:
            console.print("\n[dim]Note: Values are masked for security. Use --show-values to see actual values.[/dim]")
        
    except Exception as e:
        if state.verbose:
            console.print_exception()
        if state.json_output:
            typer.echo(f'{{"status": "error", "message": "{str(e)}"}}')
        else:
            console.print(f"[bold red]Error listing configuration: {str(e)}[/bold red]")
        raise typer.Exit(code=1)
