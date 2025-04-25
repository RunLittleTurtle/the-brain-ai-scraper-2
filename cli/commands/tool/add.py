#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Implementation of the 'brain tools add' command.

This module provides functionality to add a new tool to the registry
with its metadata.
"""

from typing import Optional, List
import typer
from rich.console import Console

from tool_registry import ToolRegistry
from tool_registry.models import ToolMetadata
from tool_registry.exceptions import ToolValidationError, ToolAlreadyExistsError
from cli.app import state

console = Console()

def add_tool(
    name: str = typer.Option(..., "--name", "-n", help="Unique name for the tool"),
    description: str = typer.Option(..., "--description", "-d", help="Short description of the tool"),
    tool_type: str = typer.Option(..., "--type", "-t", help="Tool type (e.g., browser, parser)"),
    package_name: str = typer.Option(..., "--package", "-p", help="Name of the Python package"),
    pip_install_command: Optional[str] = typer.Option(
        None, 
        "--pip-cmd", 
        help="Custom pip install command (default: pip install {package_name})"
    ),
    execution_mode: str = typer.Option(
        "sync", 
        "--mode", 
        "-m", 
        help="Execution mode (sync or async)"
    ),
    capabilities: List[str] = typer.Option(
        ..., 
        "--capability", 
        "-c", 
        help="Capabilities of the tool (can specify multiple)"
    ),
    compatibilities: Optional[List[str]] = typer.Option(
        None, 
        "--compatible-with", 
        help="Tools/types this tool is compatible with (can specify multiple)"
    ),
    incompatible_with: Optional[List[str]] = typer.Option(
        None, 
        "--incompatible-with", 
        help="Tools/types this tool is incompatible with (can specify multiple)"
    ),
    required_config: Optional[List[str]] = typer.Option(
        None, 
        "--requires", 
        help="Configuration keys required by this tool (can specify multiple)"
    ),
    overwrite: bool = typer.Option(
        False, 
        "--overwrite", 
        help="Overwrite existing tool if it exists"
    ),
) -> None:
    """
    Add a new tool to the registry.
    
    This command adds a new tool with its metadata to the tool registry.
    All required parameters must be specified, and the tool will be validated
    before adding.
    
    Examples:
        brain tools add --name playwright --type browser --package playwright \\
            --description "Browser automation framework" \\
            --capability javascript_rendering --capability headless_mode
    """
    try:
        # Create registry
        registry = ToolRegistry()
        
        # Create tool metadata
        tool_metadata = ToolMetadata(
            name=name,
            description=description,
            tool_type=tool_type,
            package_name=package_name,
            pip_install_command=pip_install_command or f"pip install {package_name}",
            execution_mode=execution_mode,
            capabilities=capabilities,
            compatibilities=compatibilities or [],
            incompatible_with=incompatible_with or [],
            required_config=required_config or []
        )
        
        # Check if tool already exists and we're not overwriting
        if not overwrite and name in [tool.name for tool in registry.list_tools()]:
            console.print(f"[bold red]Tool '{name}' already exists. Use --overwrite to replace it.[/bold red]")
            raise typer.Exit(code=1)
        
        # Add the tool
        registry.add_tool(tool_metadata)
        
        # Output success message
        if state.json_output:
            typer.echo(f'{{"status": "success", "message": "Tool {name} added successfully"}}')
        else:
            console.print(f"[green]✓ Tool '{name}' added successfully[/green]")
        
    except ToolValidationError as e:
        if state.json_output:
            typer.echo(f'{{"status": "error", "type": "validation", "message": "{str(e)}"}}')
        else:
            console.print(f"[bold red]Validation error: {str(e)}[/bold red]")
        raise typer.Exit(code=1)
        
    except Exception as e:
        if state.verbose:
            console.print_exception()
        if state.json_output:
            typer.echo(f'{{"status": "error", "message": "{str(e)}"}}')
        else:
            console.print(f"[bold red]Error adding tool: {str(e)}[/bold red]")
        raise typer.Exit(code=1)
