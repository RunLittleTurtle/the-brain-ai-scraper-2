#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main CLI application for The Brain.

This module sets up the Typer application with command groups and global flags,
providing the entry point for all CLI commands.
"""

from typing import Optional
import typer
from rich.console import Console

# Create the main application
app = typer.Typer(
    name="brain",
    help="The Brain AI Scraper - Command Line Interface",
    add_completion=True,
)

# Global console instance for rich output
console = Console()

# Global state to track CLI options
class GlobalState:
    """Global state shared across commands."""
    json_output: bool = False
    verbose: bool = False
    
state = GlobalState()

@app.callback()
def global_options(
    json: bool = typer.Option(
        False, 
        "--json", 
        help="Output in JSON format for machine parsing"
    ),
    verbose: bool = typer.Option(
        False, 
        "--verbose", 
        "-v", 
        help="Enable verbose output with detailed logs"
    ),
    ctx: typer.Context = typer.Context,
) -> None:
    """
    Global options that apply to all brain commands.
    
    These options should be specified before the command.
    """
    # Update global state with the provided options
    state.json_output = json
    state.verbose = verbose
    
    if verbose:
        console.print("[dim]Verbose mode enabled[/dim]")

@app.command()
def version() -> None:
    """
    Display the version of The Brain CLI.
    """
    from cli import __version__
    if state.json_output:
        import json
        typer.echo(json.dumps({"version": __version__}))
    else:
        console.print(f"[bold]The Brain CLI[/bold] version: {__version__}")

# Import command groups - must be after app is created to avoid circular imports
from cli.commands.tool import app as tool_app
from cli.commands.config import app as config_app
from cli.commands.scrape.execute_graph import scrape  # Using our LangGraph implementation

# Add the command groups to the main app
app.add_typer(tool_app, name="tools", help="Manage scraping tools")
app.add_typer(config_app, name="config", help="Manage configuration and secrets")

# Add the scrape command directly to the main app
app.command(name="scrape", help="Execute a scraping operation")(scrape)

if __name__ == "__main__":
    app()
