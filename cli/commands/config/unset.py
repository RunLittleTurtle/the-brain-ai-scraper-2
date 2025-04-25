#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Implementation of the 'brain config unset' command.

This module provides functionality to remove configuration values and secrets.
"""

from typing import Optional
import typer
from rich.console import Console

import config_secrets
from config_secrets.exceptions import DotEnvWriteError
from cli.app import state

console = Console()

def unset_config(
    key: str = typer.Argument(..., help="The configuration key to remove"),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Remove without confirmation prompt"
    ),
) -> None:
    """
    Remove a configuration value or secret.
    
    This command removes a configuration value or secret from the .env file.
    It will ask for confirmation unless the --force flag is used.
    
    Examples:
        brain config unset OPENAI_KEY
        brain config unset SCRAPERAPI_KEY --force
    """
    try:
        # Confirm removal if not forced
        if not force and not state.json_output:
            confirm = typer.confirm(f"Are you sure you want to remove configuration '{key}'?")
            if not confirm:
                console.print("[yellow]Operation cancelled[/yellow]")
                return
        
        # Check if key exists in environment
        # We need to get the actual environment value, not the list of keys
        # from config_secrets which might be out of sync
        import os
        env_value = os.getenv(key)
        
        # Handle case where key doesn't exist
        if env_value is None:
            if state.json_output:
                typer.echo(f'{{"status": "warning", "message": "Key {key} doesn\'t exist in configuration"}}')
            else:
                console.print(f"[yellow]Warning: Key '[bold]{key}[/bold]' doesn't exist in configuration[/yellow]")
            # If not forcing, exit; otherwise continue to the unset operation
            if not force:
                return
                
        # Remove the configuration value
        result = config_secrets.unset_config_value(key)
        
        # Output success message only if a key was actually removed
        if env_value is not None and result:
            if state.json_output:
                typer.echo(f'{{"status": "success", "message": "Configuration value {key} removed successfully"}}')
            else:
                console.print(f"[green]✓ Configuration value '[bold]{key}[/bold]' removed successfully[/green]")
        elif env_value is None:
            # Don't output success for non-existent keys, even with --force
            # (The warning about non-existent key is already shown above)
            pass
        else:
            if state.json_output:
                typer.echo(f'{{"status": "warning", "message": "Key {key} not found in configuration"}}')
            else:
                console.print(f"[yellow]Key [bold]{key}[/bold] not found in configuration[/yellow]")
        
    except DotEnvWriteError as e:
        if state.json_output:
            typer.echo(f'{{"status": "error", "type": "write_error", "message": "{str(e)}"}}')
        else:
            console.print(f"[bold red]Error writing to .env file: {str(e)}[/bold red]")
        raise typer.Exit(code=1)
        
    except Exception as e:
        if state.verbose:
            console.print_exception()
        if state.json_output:
            typer.echo(f'{{"status": "error", "message": "{str(e)}"}}')
        else:
            console.print(f"[bold red]Error removing configuration: {str(e)}[/bold red]")
        raise typer.Exit(code=1)
