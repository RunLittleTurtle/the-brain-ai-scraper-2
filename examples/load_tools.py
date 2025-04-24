#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tool Registry Initialization Script.

This script loads all the tool definitions from the tool_registry/tools directory
into the tool registry and demonstrates basic functionality.
"""

import os
import sys
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add the parent directory to the Python path to import the module
sys.path.insert(0, str(Path(__file__).parent.parent))

from tool_registry import ToolRegistry
from tool_registry.exceptions import ToolRegistryError, ToolNotFoundError
from rich.console import Console
from rich.table import Table


def main() -> None:
    """Load all tools from the tools directory into the registry."""
    console = Console()
    console.print("[bold blue]The Brain AI Scraper[/bold blue] - Tool Registry Initialization")
    console.print("Loading tools into registry...\n")
    
    # Initialize registry
    registry = ToolRegistry()
    
    # Path to tools directory
    tools_dir = Path(__file__).parent.parent / "tool_registry" / "tools"
    
    # Get all JSON files in the tools directory
    tool_files = list(tools_dir.glob("*.json"))
    
    if not tool_files:
        console.print("[bold red]Error:[/bold red] No tool definition files found in the tools directory.")
        return
    
    # Track loaded tools and any errors
    loaded_tools: List[str] = []
    error_files: List[str] = []
    
    # Load each tool
    for file_path in tool_files:
        try:
            # Load the tool definition from JSON
            with open(file_path, "r") as f:
                tool_data = json.load(f)
            
            # Add the tool to the registry
            tool = registry.add_tool(tool_data)
            loaded_tools.append(tool.name)
            console.print(f"[green]✓[/green] Loaded: {tool.name}")
        
        except json.JSONDecodeError:
            console.print(f"[bold red]Error:[/bold red] Invalid JSON in {file_path.name}")
            error_files.append(file_path.name)
        except ToolRegistryError as e:
            console.print(f"[bold red]Error:[/bold red] {str(e)} in {file_path.name}")
            error_files.append(file_path.name)
    
    console.print(f"\nLoaded {len(loaded_tools)} tools out of {len(tool_files)} definition files.")
    
    if error_files:
        console.print(f"[bold yellow]Warning:[/bold yellow] Failed to load {len(error_files)} tool files: {', '.join(error_files)}")
    
    # Display the loaded tools in a table
    if loaded_tools:
        console.print("\n[bold]Tools in Registry:[/bold]")
        table = Table(show_header=True)
        table.add_column("Name", style="cyan")
        table.add_column("Type", style="green")
        table.add_column("Mode", style="magenta")
        table.add_column("Capabilities", style="blue")
        
        for tool_name in sorted(loaded_tools):
            try:
                tool = registry.get_tool(tool_name)
                # Truncate capabilities list if it's too long
                capabilities = ", ".join(tool.capabilities[:3])
                if len(tool.capabilities) > 3:
                    capabilities += "..."
                table.add_row(tool.name, tool.tool_type, tool.execution_mode, capabilities)
            except ToolNotFoundError:
                # Should not happen as we just loaded these tools
                pass
        
        console.print(table)
        
        # Show some compatibility examples
        show_compatibility_examples(registry, console)


def show_compatibility_examples(registry: ToolRegistry, console: Console) -> None:
    """Demonstrate compatibility checking between tools."""
    console.print("\n[bold]Compatibility Examples:[/bold]")
    
    examples = [
        (["playwright", "beautifulsoup4"], "Browser + Parser"),
        (["playwright", "selenium"], "Two browser automation tools"),
        (["playwright", "parsel"], "Browser + Alternative Parser"),
        (["selenium", "undetected-chromedriver"], "Selenium + Stealth Enhancement"),
        (["httpx", "beautifulsoup4"], "HTTP Client + Parser"),
        (["scrapy", "parsel"], "Framework + Its Native Parser")
    ]
    
    table = Table(show_header=True)
    table.add_column("Tools", style="cyan")
    table.add_column("Description", style="blue")
    table.add_column("Compatible?", style="green")
    
    for tools, description in examples:
        try:
            compatible = registry.check_compatibility(tools)
            status = "[green]✓ Yes[/green]" if compatible else "[red]✗ No[/red]"
        except ToolNotFoundError:
            status = "[yellow]? Tool not found[/yellow]"
        
        table.add_row(", ".join(tools), description, status)
    
    console.print(table)


if __name__ == "__main__":
    main()
