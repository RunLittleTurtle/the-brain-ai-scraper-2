#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration command group for The Brain CLI.

This module provides commands for managing configuration and secrets,
including setting, listing, and unsetting configuration values.
"""

import typer
from typing import Optional

app = typer.Typer(help="Manage configuration and secrets")

# Import commands after app is created to avoid circular imports
from cli.commands.config.set import set_config
from cli.commands.config.list import list_config
from cli.commands.config.unset import unset_config

# Register commands directly with the app
app.command("set")(set_config)
app.command("list")(list_config)
app.command("unset")(unset_config)

__all__ = ['app']
