#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tool registry command group for The Brain CLI.

This module provides commands for managing the tool registry, including
listing, adding, removing, and checking compatibility of tools.
"""

import typer
from typing import Optional

app = typer.Typer(help="Manage scraping tools")

# Import commands after app is created to avoid circular imports
from cli.commands.tool.list import list_tools
from cli.commands.tool.add import add_tool
from cli.commands.tool.remove import remove_tool
from cli.commands.tool.check_compat import check_compatibility

# Register commands directly with the app
app.command("list")(list_tools)
app.command("add")(add_tool)
app.command("remove")(remove_tool)
app.command("check-compat")(check_compatibility)

__all__ = ['app']
