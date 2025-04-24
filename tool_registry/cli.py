#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLI interface for the tool registry module.

This module provides command-line commands for interacting with the tool registry,
allowing users to add, list, remove, and check compatibility of tools.
"""

import os
import sys
import json
from pathlib import Path
from typing import Optional, List, Dict, Any

import typer
from rich.console import Console
from rich.table import Table

from tool_registry.core_tool import ToolRegistry
from tool_registry.models import ToolMetadata
from tool_registry.exceptions import (
    ToolRegistryError,
    ToolNotFoundError,
    ToolValidationError,
    ToolAlreadyExistsError,
    ToolCompatibilityError
)

# Create CLI app
app = typer.Typer(help="Tool Registry CLI for The Brain")
console = Console()

# Global registry instance
registry = ToolRegistry()


@app.command("add")
def add_tool(
    file_path: Path = typer.Argument(
        ...,
        help="Path to JSON file containing tool metadata",
        exists=True,
        readable=True,
        dir_okay=False,
        resolve_path=True
    ),
):
    """Add a new tool to the registry from a JSON file."""
    try:
        # Load JSON file
        with open(file_path, "r") as f:
            tool_data = json.load(f)
        
        # Add tool to registry
        tool = registry.add_tool(tool_data)
        console.print(f"✅ Tool '[bold green]{tool.name}[/bold green]' added successfully to the registry")
        
    except json.JSONDecodeError:
        console.print(f"[bold red]Error:[/bold red] Invalid JSON in file {file_path}")
        sys.exit(1)
    except ToolValidationError as e:
        console.print(f"[bold red]Validation Error:[/bold red] {str(e)}")
        sys.exit(1)
    except ToolRegistryError as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        sys.exit(1)


@app.command("list")
def list_tools(
    tool_type: Optional[str] = typer.Option(None, "--type", "-t", help="Filter by tool type"),
    capability: Optional[str] = typer.Option(None, "--capability", "-c", help="Filter by capability"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output in JSON format")
):
    """List all tools in the registry with optional filtering."""
    try:
        tools = registry.list_tools(tool_type=tool_type, capability=capability)
        
        if output_json:
            # Output JSON format
            tool_list = [tool.dict() for tool in tools]
            console.print(json.dumps(tool_list, indent=2))
        else:
            # Output table format
            if not tools:
                console.print("[yellow]No tools found matching the criteria[/yellow]")
                return
                
            table = Table(title="Tool Registry")
            table.add_column("Name", style="cyan")
            table.add_column("Type", style="green")
            table.add_column("Execution Mode", style="blue")
            table.add_column("Capabilities", style="magenta")
            
            for tool in tools:
                table.add_row(
                    tool.name,
                    tool.tool_type,
                    tool.execution_mode,
                    ", ".join(tool.capabilities[:3]) + (" ..." if len(tool.capabilities) > 3 else "")
                )
                
            console.print(table)
            console.print(f"\nTotal tools: {len(tools)}")
            
    except ToolRegistryError as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        sys.exit(1)


@app.command("remove")
def remove_tool(
    name: str = typer.Argument(..., help="Name of the tool to remove")
):
    """Remove a tool from the registry."""
    try:
        success = registry.remove_tool(name)
        if success:
            console.print(f"✅ Tool '[bold green]{name}[/bold green]' removed successfully")
        else:
            console.print(f"[yellow]Tool '{name}' not found in the registry[/yellow]")
            
    except ToolRegistryError as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        sys.exit(1)


@app.command("check-compat")
def check_compatibility(
    names: List[str] = typer.Argument(..., help="Names of tools to check for compatibility")
):
    """Check if the specified tools are compatible with each other."""
    try:
        compatible = registry.check_compatibility(names)
        
        if compatible:
            console.print(f"✅ [bold green]Compatible:[/bold green] The specified tools can work together in a pipeline")
        else:
            console.print(f"❌ [bold red]Not Compatible:[/bold red] The specified tools cannot work together in a pipeline")
            
    except ToolNotFoundError as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        sys.exit(1)
    except ToolRegistryError as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        sys.exit(1)


@app.command("find-compatible")
def find_compatible_tools(
    name: str = typer.Argument(..., help="Name of the tool to find compatibilities for"),
    target_type: Optional[str] = typer.Option(None, "--type", "-t", help="Filter by target tool type"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output in JSON format")
):
    """Find all tools that are compatible with the specified tool."""
    try:
        tools = registry.find_compatible_tools(name, target_type=target_type)
        
        if output_json:
            # Output JSON format
            tool_list = [tool.dict() for tool in tools]
            console.print(json.dumps(tool_list, indent=2))
        else:
            # Output table format
            if not tools:
                console.print(f"[yellow]No compatible tools found for '{name}'[/yellow]")
                return
                
            table = Table(title=f"Tools Compatible with {name}")
            table.add_column("Name", style="cyan")
            table.add_column("Type", style="green")
            table.add_column("Execution Mode", style="blue")
            
            for tool in tools:
                table.add_row(tool.name, tool.tool_type, tool.execution_mode)
                
            console.print(table)
            console.print(f"\nTotal compatible tools: {len(tools)}")
            
    except ToolNotFoundError as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        sys.exit(1)
    except ToolRegistryError as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    app()
