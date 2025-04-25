#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Implementation of the 'brain tools remove' command.

This module provides functionality to remove a tool from the registry.
"""

from typing import Optional
import typer
from rich.console import Console

from tool_registry import ToolRegistry
from tool_registry.exceptions import ToolNotFoundError
from cli.app import state

console = Console()

def remove_tool(
    name: str = typer.Argument(..., help="Name of the tool to remove"),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Remove without confirmation prompt"
    ),
) -> None:
    """
    Remove a tool from the registry.
    
    This command removes a tool from the registry by its name.
    It will ask for confirmation unless the --force flag is used.
    
    Examples:
        brain tools remove playwright
        brain tools remove playwright --force
    """
    try:
        # Create registry
        registry = ToolRegistry()
        
        # Check if tool exists
        try:
            registry.get_tool(name)
        except ToolNotFoundError:
            console.print(f"[bold red]Tool '{name}' not found in registry[/bold red]")
            raise typer.Exit(code=1)
        
        # Confirm removal if not forced
        if not force and not state.json_output:
            confirm = typer.confirm(f"Are you sure you want to remove tool '{name}'?")
            if not confirm:
                console.print("[yellow]Operation cancelled[/yellow]")
                return
        
        # Remove the tool
        registry.remove_tool(name)
        
        # Output success message
        if state.json_output:
            typer.echo(f'{{"status": "success", "message": "Tool {name} removed successfully"}}')
        else:
            console.print(f"[green]✓ Tool '{name}' removed successfully[/green]")
        
    except Exception as e:
        if state.verbose:
            console.print_exception()
        if state.json_output:
            typer.echo(f'{{"status": "error", "message": "{str(e)}"}}')
        else:
            console.print(f"[bold red]Error removing tool: {str(e)}[/bold red]")
        raise typer.Exit(code=1)
