#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for the CLI module commands.

These tests verify the functionality of all CLI commands,
including tools, config, and scrape operations.
"""

import os
import subprocess
from typing import List, Dict, Any, Optional, Tuple


def run_command(cmd: List[str]) -> Tuple[int, str, str]:
    """
    Run a command and return exit code, stdout, and stderr.
    
    Args:
        cmd: Command to run as a list of strings
    
    Returns:
        Tuple of (exit_code, stdout, stderr)
    """
    process = subprocess.Popen(
        cmd, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE,
        universal_newlines=True
    )
    stdout, stderr = process.communicate()
    return process.returncode, stdout, stderr


def test_version_command() -> None:
    """Test the version command returns the expected output."""
    returncode, stdout, stderr = run_command(["python3", "-m", "cli.app", "version"])
    assert returncode == 0, f"Command failed with: {stderr}"
    assert "version" in stdout
    print("✅ Version command test passed")


def test_tools_list() -> None:
    """Test the tools list command returns expected output."""
    returncode, stdout, stderr = run_command(["python3", "-m", "cli.app", "tools", "list"])
    assert returncode == 0, f"Command failed with: {stderr}"
    assert "Registered Tools" in stdout
    print("✅ Tools list command test passed")


def test_tools_add_remove() -> None:
    """Test adding and removing a tool."""
    # Define test tool parameters
    test_tool = "test-cli-tool"
    
    # Add the tool
    add_returncode, add_stdout, add_stderr = run_command([
        "python3", "-m", "cli.app", "tools", "add",
        "--name", test_tool,
        "--description", "Test tool for CLI testing",
        "--type", "parser",
        "--package", "test-package",
        "--capability", "html_parsing"
    ])
    assert add_returncode == 0, f"Add tool command failed with: {add_stderr}"
    assert f"Tool '{test_tool}' added successfully" in add_stdout
    
    # Verify the tool was added
    list_returncode, list_stdout, list_stderr = run_command(["python3", "-m", "cli.app", "tools", "list"])
    assert list_returncode == 0, f"List command failed with: {list_stderr}"
    assert test_tool in list_stdout
    
    # Remove the tool
    remove_returncode, remove_stdout, remove_stderr = run_command([
        "python3", "-m", "cli.app", "tools", "remove",
        test_tool, "--force"
    ])
    assert remove_returncode == 0, f"Remove tool command failed with: {remove_stderr}"
    assert f"Tool '{test_tool}' removed successfully" in remove_stdout
    
    # Verify the tool was removed
    list_returncode, list_stdout, list_stderr = run_command(["python3", "-m", "cli.app", "tools", "list"])
    assert list_returncode == 0, f"List command failed with: {list_stderr}"
    assert test_tool not in list_stdout
    
    print("✅ Tools add/remove test passed")


def test_tools_check_compat() -> None:
    """Test checking compatibility between tools."""
    returncode, stdout, stderr = run_command([
        "python3", "-m", "cli.app", "tools", "check-compat",
        "beautifulsoup4", "playwright"
    ])
    # The command should run (exit code 0) even if tools are not compatible
    assert "Tools are" in stdout
    print("✅ Tools compatibility check test passed")


def test_scrape_command() -> None:
    """Test the scrape command with structured arguments."""
    returncode, stdout, stderr = run_command([
        "python3", "-m", "cli.app", "scrape",
        "--url", "https://example.com",
        "--extract", "price,title"
    ])
    assert returncode == 0, f"Command failed with: {stderr}"
    assert "Structured request" in stdout
    assert "Scraping completed successfully" in stdout
    print("✅ Scrape command test passed")


def test_config_commands() -> None:
    """Test the config commands (set, list, unset)."""
    # Set a test config value
    test_key = "TEST_CONFIG_CLI_TEST"
    test_value = "test_value_12345"
    
    # Set the config value
    set_returncode, set_stdout, set_stderr = run_command([
        "python3", "-m", "cli.app", "config", "set",
        test_key, test_value
    ])
    assert set_returncode == 0, f"Set command failed with: {set_stderr}"
    assert f"Configuration value '{test_key}' set" in set_stdout
    
    # List the config values
    list_returncode, list_stdout, list_stderr = run_command([
        "python3", "-m", "cli.app", "config", "list"
    ])
    assert list_returncode == 0, f"List command failed with: {list_stderr}"
    assert test_key in list_stdout
    
    # Unset the config value
    unset_returncode, unset_stdout, unset_stderr = run_command([
        "python3", "-m", "cli.app", "config", "unset",
        test_key, "--force"
    ])
    assert unset_returncode == 0, f"Unset command failed with: {unset_stderr}"
    assert f"Configuration value '{test_key}' removed successfully" in unset_stdout

    print("✅ Config commands test passed")


def run_tests() -> None:
    """Run all tests."""
    print("Running CLI module tests...")
    test_version_command()
    test_tools_list()
    test_tools_add_remove()
    test_tools_check_compat()
    test_scrape_command()
    test_config_commands()
    print("✅ All CLI module tests passed!")


if __name__ == "__main__":
    run_tests()
