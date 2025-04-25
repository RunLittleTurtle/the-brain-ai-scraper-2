#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
The Brain - CLI Module

This module provides a command-line interface for interacting with The Brain
scraping system, including tool management, configuration, and scraping operations.
"""

from typing import Dict, Any
import typer
from cli.app import app as brain_app

__version__ = "0.1.0"

__all__ = [
    'brain_app',
]

def main() -> None:
    """Entry point for CLI when installed via pip."""
    brain_app()
