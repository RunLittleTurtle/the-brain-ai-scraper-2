#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify config_secrets is loading API keys correctly.
"""
from config_secrets import get_secret, get_required_secret

# Test OpenAI API Key
openai_key = get_secret("OPENAI_API_KEY")
print(f"OpenAI API Key found: {bool(openai_key)}")
if openai_key:
    # Mask the key for security
    masked_key = f"{openai_key[:8]}...{openai_key[-4:]}" if len(openai_key) > 12 else "***"
    print(f"OpenAI Key (masked): {masked_key}")

# Test LangSmith API Key
langsmith_key = get_secret("LANGSMITH_API_KEY")
print(f"LangSmith API Key found: {bool(langsmith_key)}")
if langsmith_key:
    # Mask the key for security
    masked_key = f"{langsmith_key[:8]}...{langsmith_key[-4:]}" if len(langsmith_key) > 12 else "***"
    print(f"LangSmith Key (masked): {masked_key}")

# Test LangSmith Project
langsmith_project = get_secret("LANGSMITH_PROJECT", "default_project")
print(f"LangSmith Project: {langsmith_project}")

# Test LangChain Tracing
langchain_tracing = get_secret("LANGCHAIN_TRACING_V2")
print(f"LangChain Tracing enabled: {langchain_tracing}")
