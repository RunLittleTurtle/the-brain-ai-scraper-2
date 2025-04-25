#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Implementation of the 'brain tools check-compat' command.

This module provides functionality to check compatibility between tools.
"""

from typing import List
import typer
from rich.console import Console

from tool_registry import ToolRegistry
from tool_registry.exceptions import ToolNotFoundError, ToolCompatibilityError
from cli.app import state

console = Console()

def check_compatibility(
    names: List[str] = typer.Argument(
        ..., 
        help="Names of tools to check for compatibility"
    ),
) -> None:
    """
    Check if a set of tools is compatible.
    
    This command checks whether the specified tools can be used together
    in a pipeline, based on their compatibility metadata.
    
    Examples:
        brain tools check-compat playwright beautifulsoup4
        brain tools check-compat playwright selenium  # Should show incompatible
    """
    if len(names) < 2:
        console.print("[bold yellow]Error: At least two tools must be specified[/bold yellow]")
        raise typer.Exit(code=1)
        
    try:
        # Create registry
        registry = ToolRegistry()
        
        # Try to get all tools (raises ToolNotFoundError if any is missing)
        tools = []
        for name in names:
            try:
                tools.append(registry.get_tool(name))
            except ToolNotFoundError:
                console.print(f"[bold red]Error: Tool '{name}' not found in registry[/bold red]")
                raise typer.Exit(code=1)
        
        # Check compatibility
        compatible = registry.check_compatibility(names)
        tool_names = ", ".join(names)
        
        # Output results
        if state.json_output:
            typer.echo(f'{{"compatible": {str(compatible).lower()}, "tools": {names}}}')
        else:
            if compatible:
                console.print(f"[green]✓ Tools are compatible:[/green] {tool_names}")
            else:
                console.print(f"[bold red]✗ Tools are not compatible:[/bold red] {tool_names}")
                
                # Provide information about incompatibilities
                console.print("\n[yellow]Incompatibility details:[/yellow]")
                console.print("  • Specific incompatibility details not available")
                console.print("  • Check tool metadata for compatibility information")
                
                # For verbose mode, show the tool metadata
                if state.verbose:
                    console.print("\n[yellow]Tool details:[/yellow]")
                    for name in names:
                        tool = registry.get_tool(name)
                        console.print(f"\n[bold]{tool.name}[/bold] ({tool.tool_type})")
                        console.print(f"  • Compatible with: {', '.join(tool.compatibilities) if tool.compatibilities else 'No specific compatibilities'}")
                        console.print(f"  • Incompatible with: {', '.join(tool.incompatible_with) if tool.incompatible_with else 'No specific incompatibilities'}")
        
    except Exception as e:
        if state.verbose:
            console.print_exception()
        if state.json_output:
            typer.echo(f'{{"status": "error", "message": "{str(e)}"}}')
        else:
            console.print(f"[bold red]Error checking compatibility: {str(e)}[/bold red]")
        raise typer.Exit(code=1)
