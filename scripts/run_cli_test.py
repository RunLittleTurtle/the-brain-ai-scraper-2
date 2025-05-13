#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple non-interactive test script for the CLI integration.
This script runs a preset query using the CLI command.
"""
import os
import sys
import logging
import subprocess

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Set the test query
TEST_QUERY = "Find all product managers in Montreal on LinkedIn and Indeed from the past 7 days"

def main():
    """Run the CLI test with a preset query."""
    # Set up environment for tracing if desired (uncomment these lines)
    # os.environ["LANGCHAIN_TRACING_V2"] = "true"
    # os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
    # os.environ["LANGCHAIN_PROJECT"] = "brain_ai_scraper"
    
    # Make sure OPENAI_API_KEY is set
    if not os.getenv("OPENAI_API_KEY"):
        logger.warning("No OpenAI API key found in environment. Set OPENAI_API_KEY environment variable.")
    
    # Build the command
    cmd = ["python", "-m", "cli.app", "scrape", TEST_QUERY]
    
    # Run the command
    logger.info(f"Running command: {' '.join(cmd)}")
    return subprocess.call(cmd)

if __name__ == "__main__":
    sys.exit(main())
