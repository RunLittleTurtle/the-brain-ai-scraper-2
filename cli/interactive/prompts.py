#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interactive prompts for The Brain CLI.

This module provides interactive prompt functions to enhance the CLI experience
by guiding users through complex operations.
"""

from typing import Dict, Any, List, Optional, Union, Callable
import typer
from rich.console import Console
from rich.prompt import Prompt, Confirm

console = Console()

def prompt_for_missing_fields(
    extracted_fields: List[str],
    available_fields: Optional[List[str]] = None
) -> List[str]:
    """
    Prompt the user to confirm or modify extracted fields.
    
    This function shows the currently extracted fields and allows the
    user to add, remove, or confirm them.
    
    Args:
        extracted_fields: List of fields already extracted from input
        available_fields: Optional list of available field options
        
    Returns:
        Updated list of fields to extract
    """
    if available_fields is None:
        available_fields = [
            "title", "price", "description", "image", "rating",
            "reviews", "availability", "brand", "category"
        ]
    
    # Show current fields
    console.print("\n[bold blue]Fields to extract:[/bold blue]")
    for field in extracted_fields:
        console.print(f"  • [cyan]{field}[/cyan]")
    
    # Ask for confirmation
    confirm = Confirm.ask("\nAre these fields correct?", default=True)
    if confirm:
        return extracted_fields
    
    # Allow modification
    console.print("\n[bold blue]Available fields:[/bold blue]")
    for i, field in enumerate(available_fields, 1):
        is_selected = field in extracted_fields
        marker = "✓" if is_selected else "○"
        console.print(f"  {i}. [{marker}] {field}")
    
    # Get new field selection
    selection = Prompt.ask(
        "\nEnter field numbers to select/deselect (comma-separated), or 'all' for all fields",
        default=",".join(str(available_fields.index(field) + 1) for field in extracted_fields)
    )
    
    if selection.lower() == "all":
        return available_fields
    
    # Parse selection
    try:
        selected_indices = [int(idx.strip()) - 1 for idx in selection.split(",") if idx.strip()]
        selected_fields = [available_fields[idx] for idx in selected_indices if 0 <= idx < len(available_fields)]
        return selected_fields
    except (ValueError, IndexError):
        console.print("[yellow]Invalid selection, keeping original fields[/yellow]")
        return extracted_fields


def prompt_for_url() -> str:
    """
    Prompt the user to enter a URL to scrape.
    
    Returns:
        URL entered by the user
    """
    return Prompt.ask("[bold blue]Enter URL to scrape[/bold blue]")


def prompt_for_confirmation(message: str, default: bool = True) -> bool:
    """
    Prompt the user for confirmation.
    
    Args:
        message: The message to display
        default: Default value if user just presses Enter
        
    Returns:
        True if confirmed, False otherwise
    """
    return Confirm.ask(message, default=default)
