#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scrape command group for The Brain CLI.

This module provides commands for executing scraping operations,
including preparing, executing, and retrying scrapes.
"""

import typer
from typing import Optional

app = typer.Typer(help="Execute scraping operations")

# Import commands after app is created to avoid circular imports
from cli.commands.scrape.execute import scrape

# Register commands directly with the app
app.command("execute")(scrape)

# Default command when using 'brain scrape'
@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    """
    Execute a scraping operation.
    
    If no subcommand is provided, the 'execute' command is invoked.
    """
    if ctx.invoked_subcommand is None:
        # Get the command object for 'execute'
        execute_cmd = app.get_command("execute")
        
        # Call the execute command with empty arguments
        ctx.invoke(execute_cmd)

__all__ = ['app']
