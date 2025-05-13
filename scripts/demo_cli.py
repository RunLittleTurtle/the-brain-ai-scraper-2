#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo script for the CLI integration of intent inference.

This script provides a simple way to test the CLI command with our
LangGraph implementation.
"""
import os
import sys
import logging
import subprocess
from typing import List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def configure_env() -> None:
    """Configure environment variables for LangSmith if needed."""
    # Don't override existing variables
    if not os.getenv("LANGCHAIN_TRACING_V2"):
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
    
    if not os.getenv("LANGCHAIN_ENDPOINT"):
        os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
    
    if not os.getenv("LANGCHAIN_PROJECT"):
        os.environ["LANGCHAIN_PROJECT"] = "brain_ai_scraper"
    
    # Check for API key - important for LLM calls to work
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.warning("No OpenAI API key found. Set OPENAI_API_KEY environment variable.")


def run_cli_command(query: str, verbose: bool = False) -> int:
    """
    Run the CLI command with the given query.
    
    Args:
        query: The query to process
        verbose: Whether to enable verbose output
        
    Returns:
        Exit code from the command
    """
    # Build the command
    cmd = ["python", "-m", "cli.app"]
    
    if verbose:
        cmd.append("--verbose")
    
    cmd.extend(["scrape", query])
    
    # Run the command
    try:
        logger.info(f"Running command: {' '.join(cmd)}")
        return subprocess.call(cmd)
    except Exception as e:
        logger.error(f"Error running CLI command: {str(e)}")
        return 1


def main() -> int:
    """Run the demo script."""
    # Configure environment
    configure_env()
    
    # Define example queries
    examples = [
        "Find all product managers in Montreal on LinkedIn and Indeed from the past 7 days",
        "Scrape all Nvidia GPUs with prices from Amazon and Newegg",
        "Get all apartments for rent in New York under $2000 with at least 2 bedrooms"
    ]
    
    # Print the examples
    print("\n🧠 The Brain AI Scraper - CLI Demo\n")
    print("Example queries:")
    for i, example in enumerate(examples, 1):
        print(f"{i}. {example}")
    
    # Get user selection
    try:
        choice = int(input("\nSelect an example (1-3) or enter 0 to input your own query: "))
        
        if 1 <= choice <= len(examples):
            query = examples[choice-1]
            print(f"\nUsing example {choice}: {query}\n")
        elif choice == 0:
            query = input("\nEnter your query: ")
        else:
            print("Invalid choice. Using example 1.")
            query = examples[0]
    except ValueError:
        print("Invalid input. Using example 1.")
        query = examples[0]
    
    # Run the CLI command with the selected query
    return run_cli_command(query, verbose=True)


if __name__ == "__main__":
    sys.exit(main())
