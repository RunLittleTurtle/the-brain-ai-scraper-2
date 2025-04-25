#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Implementation of the 'brain config set' command.

This module provides functionality to set configuration values and secrets.
"""

from typing import Optional
import typer
from rich.console import Console

import config_secrets
from config_secrets.exceptions import DotEnvWriteError
from cli.app import state

console = Console()

def set_config(
    key: str = typer.Argument(..., help="The configuration key to set"),
    value: Optional[str] = typer.Argument(None, help="The value to set (not required with --secure)"),
    secure_input: bool = typer.Option(
        False,
        "--secure",
        "-s",
        help="Prompt for value securely (without echo)",
    ),
) -> None:
    """
    Set a configuration value or secret.
    
    This command sets a configuration value or secret in the .env file.
    For sensitive values like API keys, you can use the --secure flag
    to enter the value without it being shown on screen.
    
    Examples:
        brain config set OPENAI_KEY sk-abcdef123456
        brain config set SCRAPERAPI_KEY --secure
    """
    try:
        # If secure input is requested, prompt for the value
        if secure_input:
            value = typer.prompt(f"Enter value for {key}", hide_input=True)
        elif value is None:
            console.print("[bold red]Error: Value is required unless using --secure flag[/bold red]")
            raise typer.Exit(code=1)
        
        # Set the configuration value
        config_secrets.set_config_value(key, value)
        
        # Output success message
        if state.json_output:
            typer.echo(f'{{"status": "success", "message": "Configuration value {key} set successfully"}}')
        else:
            # Mask the value for display
            masked_value = "****" if len(value) > 4 else "****"
            console.print(f"[green]✓ Configuration value '[bold]{key}[/bold]' set to '{masked_value}'[/green]")
        
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
            console.print(f"[bold red]Error setting configuration: {str(e)}[/bold red]")
        raise typer.Exit(code=1)
