"""
Helper utilities for LangChain components in the intent inference module.

This module provides utility functions for working with LangChain, including
LLM configuration and shared chain components.
"""
from typing import Dict, Any, Optional
import os
from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langsmith.run_helpers import traceable
from langchain.callbacks.tracers import LangChainTracer

# Import from config_secrets module to get API keys
from config_secrets import get_secret, get_required_secret, SecretNotFoundError


def get_llm(model_name: Optional[str] = None, trace_name: Optional[str] = None) -> BaseChatModel:
    """
    Get a configured LLM instance based on preferences and available API keys.
    
    Args:
        model_name: Optional specific model name to use
        trace_name: Optional name for LangSmith tracing
        
    Returns:
        Configured LangChain LLM instance
    
    Raises:
        SecretNotFoundError: If required API keys are not available
    """
    # Setup LangSmith tracing if credentials are available
    callbacks = []
    try:
        langsmith_api_key = get_secret("LANGSMITH_API_KEY")
        langsmith_project = get_secret("LANGSMITH_PROJECT", "intent_inference")
        
        if langsmith_api_key:
            # For newer versions of LangChain
            tracer = LangChainTracer(
                project_name=langsmith_project
            )
            callbacks.append(tracer)
    except Exception as e:
        # Log but continue without LangSmith if there's an issue
        print(f"LangSmith setup failed: {e}. Continuing without tracing.")
    
    # Try OpenAI (primary option)
    try:
        # Use config_secrets to get API key
        openai_api_key = get_secret("OPENAI_API_KEY")
        if openai_api_key:
            # Use specified model or default to GPT-4.1
            model = model_name or "gpt-4-1106-preview"  # Using GPT-4.1 as requested
            return ChatOpenAI(
                model=model,
                temperature=0.2,  # Low temperature for more deterministic outputs
                api_key=openai_api_key,
                callbacks=callbacks if callbacks else None
            )
    except Exception as e:
        print(f"OpenAI setup failed: {e}. Trying fallback.")
    
    # Try Anthropic as fallback
    try:
        anthropic_api_key = get_secret("ANTHROPIC_API_KEY")
        if anthropic_api_key:
            model = model_name or "claude-3-opus-20240229"
            return ChatAnthropic(
                model=model,
                temperature=0.2,
                api_key=anthropic_api_key,
                callbacks=callbacks if callbacks else None
            )
    except Exception as e:
        print(f"Anthropic setup failed: {e}")
    
    # No valid API keys found
    raise SecretNotFoundError(
        "No valid LLM API keys found. Please set either OPENAI_API_KEY or ANTHROPIC_API_KEY "
        "using the config_secrets module."
    )


def get_default_model_kwargs() -> Dict[str, Any]:
    """
    Get default model keyword arguments for LLM configuration.
    
    Returns:
        Dictionary of default model configuration parameters
    """
    return {
        "temperature": 0.2,
        "max_tokens": 4000,
    }
