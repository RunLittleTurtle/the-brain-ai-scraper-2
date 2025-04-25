#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Implementation of the 'brain tools list' command.

This module provides functionality to list all tools in the registry
with optional filtering by type or capability.
"""

from typing import Optional, List
import typer
from rich.console import Console

from tool_registry import ToolRegistry
from cli.formatters.json_formatter import format_json
from cli.formatters.table_formatter import format_table
from cli.app import state

console = Console()

def list_tools(
    tool_type: Optional[str] = typer.Option(
        None, 
        "--type", 
        "-t", 
        help="Filter tools by type (e.g., 'browser', 'parser')"
    ),
    capability: Optional[str] = typer.Option(
        None, 
        "--capability", 
        "-c", 
        help="Filter tools by capability (e.g., 'javascript_rendering', 'html_parsing')"
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output in JSON format"
    ),
) -> None:
    """
    List all registered tools with optional filtering.
    
    This command displays information about all tools in the registry,
    including their name, type, capabilities, and compatibilities.
    You can filter the results by tool type or capability.
    
    Examples:
        brain tools list
        brain tools list --type browser
        brain tools list --capability javascript_rendering
        brain tools list --json
    """
    try:
        # Create registry and get tools
        registry = ToolRegistry()
        tools = registry.list_tools(tool_type=tool_type, capability=capability)
        
        # Output in JSON format if requested
        if json_output or state.json_output:
            # Convert tools to dict format for JSON
            tool_dicts = [tool.dict() for tool in tools]
            typer.echo(format_json(tool_dicts))
            return
        
        # Output in human-readable format
        if not tools:
            console.print(f"[yellow]No tools found[/yellow]", 
                          f"{'with specified filters' if tool_type or capability else ''}")
            return
        
        # Create table with tool details
        table = format_table(
            title="Registered Tools",
            columns=["Name", "Type", "Capabilities", "Compatible With"],
            data=[
                [
                    tool.name,
                    tool.tool_type,
                    ", ".join(tool.capabilities),
                    ", ".join(tool.compatibilities) if tool.compatibilities else "-"
                ]
                for tool in tools
            ]
        )
        
        # Print summary and table
        console.print(f"[green]Found {len(tools)} tools[/green]")
        console.print(table)
        
    except Exception as e:
        if state.verbose:
            console.print_exception()
        console.print(f"[bold red]Error listing tools: {str(e)}[/bold red]")
        raise typer.Exit(code=1)
