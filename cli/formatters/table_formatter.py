#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Table formatter for human-readable CLI output.

This module provides functions to format data as tables and key-value displays
using the rich library for attractive terminal output.
"""

from typing import List, Dict, Any, Optional, Union, Sequence
from rich.table import Table
from rich.panel import Panel
from rich.console import Console
from rich import box

def format_table(
    data: Union[List[Dict[str, Any]], Sequence[Sequence[Any]]],
    title: Optional[str] = None,
    columns: Optional[List[str]] = None,
    show_header: bool = True,
    row_styles: Optional[List[str]] = None,
) -> Table:
    """
    Format data as a rich table.
    
    This function handles both list-of-dicts and list-of-lists formats.
    
    Args:
        data: The data to format as a table
        title: Optional title for the table
        columns: Optional column names (required for list-of-lists)
        show_header: Whether to show the header row
        
    Returns:
        Rich Table object ready for console display
    """
    table = Table(
        title=title, 
        show_header=show_header,
        row_styles=["dim", "none"],  # Alternate row styles for better readability
        box=box.SQUARE,
        padding=(0, 1)  # Add more horizontal padding
    )
    
    # If we have a list of dicts, extract columns from the first item
    if data and isinstance(data[0], dict) and columns is None:
        columns = list(data[0].keys())
    
    # Add columns to the table
    if columns:
        for column in columns:
            # Use different overflow settings for capabilities columns
            if column.lower() in ["capabilities", "compatible with"]:
                table.add_column(column, overflow="fold", max_width=60, no_wrap=False)
            else:
                table.add_column(column, overflow="fold")
    
    # Add rows to the table
    for row in data:
        if isinstance(row, dict):
            # For dict rows, extract values in column order
            table.add_row(*[str(row.get(col, "")) for col in columns])
        else:
            # For list rows, use directly
            table.add_row(*[str(item) for item in row])
    
    return table

def format_key_value(
    data: Dict[str, Any],
    title: Optional[str] = None,
    mask_keys: Optional[List[str]] = None,
) -> Panel:
    """
    Format a dictionary as a key-value panel.
    
    Args:
        data: The dictionary to format
        title: Optional title for the panel
        mask_keys: Optional list of keys to mask values for (e.g., for secrets)
        
    Returns:
        Rich Panel object ready for console display
    """
    if mask_keys is None:
        mask_keys = []
    
    # Create console for string rendering
    console = Console(record=True, width=80)
    
    for key, value in data.items():
        # Mask sensitive values if needed
        if key in mask_keys:
            display_value = "****"
        else:
            display_value = value
            
        console.print(f"[bold]{key}:[/bold] {display_value}")
    
    # Capture console output
    output = console.export_text()
    
    return Panel(output, title=title, expand=False)
