#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for the intent inference module with LangSmith integration.

This script allows you to test the intent inference module with various queries
and visualize the graph execution in LangSmith/LangGraph Studio.
"""
import os
import sys
import json
import logging
from typing import Optional, Dict, Any
import argparse

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the intent inference module
from intent_inference import infer_intent_sync
from intent_inference.graph.app import process_input_sync
from intent_inference.utils.langsmith_utils import get_runnable_config
from models.intent.intent_spec import IntentSpec

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def check_langsmith_config() -> bool:
    """Check if LangSmith is configured correctly."""
    required_vars = ["LANGCHAIN_API_KEY", "LANGCHAIN_ENDPOINT", "LANGCHAIN_PROJECT"]
    missing = [var for var in required_vars if not os.getenv(var)]
    
    if missing:
        logger.warning(f"Missing environment variables for LangSmith: {', '.join(missing)}")
        print("\n⚠️  LangSmith configuration is incomplete. Set these environment variables:")
        for var in missing:
            print(f"   export {var}=your_value_here")
        print("\nTracing will be disabled without these variables.")
        return False
    return True


def print_intent_spec(intent_spec: IntentSpec, needs_human: bool) -> None:
    """Pretty print the intent specification."""
    print("\n" + "-" * 60)
    print(f"🎯 Intent Specification (ID: {intent_spec.spec_id})")
    print("-" * 60)
    print(f"Original Query: {intent_spec.original_query}")
    print(f"Target URLs: {', '.join(intent_spec.target_urls)}")
    
    print("\nFields to Extract:")
    for field in intent_spec.fields_to_extract:
        print(f"  • {field.name}: {field.description}")
    
    print(f"\nTechnical Requirements: {', '.join(intent_spec.technical_requirements)}")
    
    if intent_spec.constraints:
        print("\nConstraints:")
        for key, value in intent_spec.constraints.items():
            print(f"  • {key}: {value}")
    
    if intent_spec.url_health_status:
        print("\nURL Health Status:")
        for url, status in intent_spec.url_health_status.items():
            print(f"  • {url}: {status}")
    
    print(f"\nValidation Status: {intent_spec.validation_status}")
    
    if intent_spec.critique_history:
        print("\nCritique History:")
        for critique in intent_spec.critique_history:
            print(f"  • {critique}")
    
    if intent_spec.clarification_questions:
        print("\nClarification Questions:")
        for question in intent_spec.clarification_questions:
            print(f"  • {question}")
    
    print(f"\nNeeds Human Review: {'Yes' if needs_human else 'No'}")
    print("-" * 60)


def main() -> None:
    """Run the test script."""
    parser = argparse.ArgumentParser(description="Test the intent inference module")
    parser.add_argument("query", nargs="?", default=None, help="The query to test")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    parser.add_argument("--is-feedback", action="store_true", help="Treat the query as feedback")
    parser.add_argument("--previous-spec", type=str, help="Path to a JSON file containing a previous IntentSpec")
    args = parser.parse_args()
    
    # Check if LangSmith is configured
    has_langsmith = check_langsmith_config()
    
    if not args.query:
        # Use example queries if none provided
        print("No query provided. Here are some example queries you can try:")
        examples = [
            "find all the product managers in Montreal in LinkedIn and Indeed of the past 7 days",
            "scrape all Nvidia GPUs with prices from Amazon and Newegg",
            "get all apartments for rent in New York under $2000 with at least 2 bedrooms",
        ]
        for i, example in enumerate(examples, 1):
            print(f"{i}. {example}")
        
        try:
            choice = int(input("\nEnter a number to select an example (or type your own query): "))
            if 1 <= choice <= len(examples):
                query = examples[choice-1]
            else:
                print("Invalid choice. Please enter a valid number.")
                return
        except ValueError:
            query = input("Enter your query: ")
    else:
        query = args.query
    
    # Load previous spec if provided
    previous_spec = None
    if args.previous_spec:
        try:
            with open(args.previous_spec, 'r') as f:
                spec_dict = json.load(f)
                previous_spec = IntentSpec.model_validate(spec_dict)
                print(f"Loaded previous spec from {args.previous_spec}")
        except Exception as e:
            logger.error(f"Error loading previous spec: {e}")
            return
    
    print(f"\n🔍 Processing query: {query}")
    
    # Configure LangSmith tracing
    config = {
        "tags": ["intent_inference", "test_script"],
        "metadata": {
            "query": query,
            "is_feedback": args.is_feedback
        }
    }
    
    # Process the query
    try:
        intent_spec, needs_human = process_input_sync(
            user_input=query,
            previous_spec=previous_spec,
            is_feedback=args.is_feedback,
            config=get_runnable_config(**config) if has_langsmith else None
        )
        
        # Output the result
        if args.json:
            print(json.dumps(intent_spec.model_dump(), indent=2))
        else:
            print_intent_spec(intent_spec, needs_human)
        
        # Provide link to LangSmith if configured
        if has_langsmith:
            project = os.getenv("LANGCHAIN_PROJECT", "brain_ai_scraper")
            print(f"\n📊 View the trace in LangSmith: https://smith.langchain.com/projects/{project}")
            print("   This shows the complete graph execution with all steps.")
        
        # Save the spec to a file for future reference
        output_file = f"intent_spec_{intent_spec.spec_id}.json"
        with open(output_file, 'w') as f:
            json.dump(intent_spec.model_dump(), f, indent=2)
        print(f"\n💾 Saved intent specification to {output_file}")
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        return


if __name__ == "__main__":
    main()
