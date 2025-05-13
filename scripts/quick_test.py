#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick test script for the intent inference module.
This simplified script helps to verify that the basic module structure is working.
"""
import os
import sys
import json

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the intent inference module - basic imports only
from models.intent.intent_spec import IntentSpec
from intent_inference.models.context import ContextStore


def test_imports():
    """Test that basic imports work."""
    print("✅ Basic model imports successful")
    
    # Create a simple IntentSpec to verify the model works
    spec = IntentSpec(
        original_query="Test query",
        target_urls=["https://example.com"],
        fields_to_extract=[{"name": "test", "description": "Test field"}]
    )
    print(f"✅ Created IntentSpec with ID: {spec.spec_id}")
    
    # Create a context store
    context = ContextStore()
    context.user_query = "Test query"
    print("✅ Created ContextStore")
    
    return True


def test_full_imports():
    """Test the full graph imports."""
    try:
        from intent_inference.graph.app import process_input_sync
        print("✅ LangGraph app imports successful")
        return True
    except ImportError as e:
        print(f"❌ LangGraph app import failed: {str(e)}")
        return False


def main():
    """Run the quick tests."""
    print("\n🔍 Running quick tests for intent inference\n")
    
    # Test basic imports first
    if not test_imports():
        print("\n❌ Basic imports failed, exiting")
        return
    
    # Test full graph imports
    if not test_full_imports():
        print("\n⚠️ Full graph imports failed - this would prevent using LangGraph")
        print("Check that langgraph and its dependencies are installed")
    else:
        print("\n✅ All imports successful")
        
    # Check for LangSmith configuration
    langsmith_vars = ["LANGCHAIN_API_KEY", "LANGCHAIN_ENDPOINT", "LANGCHAIN_PROJECT"]
    missing = [var for var in langsmith_vars if not os.getenv(var)]
    
    if missing:
        print(f"\n⚠️ Missing environment variables for LangSmith: {', '.join(missing)}")
        print("To enable LangSmith, set these variables:")
        for var in missing:
            print(f"  export {var}=your_value_here")
    else:
        print("\n✅ LangSmith environment variables found")
    
    print("\n✨ Quick test complete\n")


if __name__ == "__main__":
    main()
