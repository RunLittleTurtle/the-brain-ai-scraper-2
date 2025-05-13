"""
Helper utilities for LangChain components in the intent inference module.

This module provides utility functions for working with LangChain, including
LLM configuration, shared chain components, and retry logic for API calls.
"""
import logging
from typing import Dict, Any, Optional, Union, TypeVar, cast
import os
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from langchain_core.language_models import BaseLanguageModel
from langchain_core.output_parsers import BaseOutputParser, StrOutputParser
from langchain_core.prompts import BasePromptTemplate
from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langsmith.run_helpers import traceable
from langchain.callbacks.tracers import LangChainTracer

# Import from config_secrets module to get API keys
from config_secrets import get_secret, get_required_secret, SecretNotFoundError

# Configure module logger
logger = logging.getLogger(__name__)


def get_llm(model_name: Optional[str] = None, trace_name: Optional[str] = None) -> BaseLanguageModel:
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


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type((ConnectionError, TimeoutError, Exception)),
    before_sleep=lambda retry_state: logger.warning(
        f"Retrying LLM call after error. Attempt {retry_state.attempt_number}/3"
    )
)
async def call_llm_with_retry(
    llm: BaseLanguageModel,
    prompt: Union[BasePromptTemplate, str],
    inputs: Dict[str, Any]
) -> str:
    """
    Call an LLM with retry logic for handling transient errors.
    
    Args:
        llm: The language model to use
        prompt: The prompt template or string
        inputs: Input values for the prompt
        
    Returns:
        LLM response as a string
    
    Raises:
        Exception: If all retry attempts fail
    """
    logger.info(f"Calling LLM with inputs: {list(inputs.keys())}")
    
    try:
        # Create chain with the prompt and LLM
        chain = prompt | llm
        
        # Call the chain
        result = await chain.ainvoke(inputs)
        
        if isinstance(result, BaseMessage):
            return result.content
        return str(result)
    except Exception as e:
        logger.error(f"Error in LLM call: {str(e)}")
        raise

def call_llm_with_retry(
    chain, 
    inputs: Dict[str, Any]
) -> str:
    """
    Synchronous wrapper for calling a chain with retry logic.
    
    Args:
        chain: The LangChain runnable chain to use
        inputs: Input values for the chain
        
    Returns:
        Chain response as a string
    
    Raises:
        Exception: If all retry attempts fail
    """
    logger.info(f"Calling chain with inputs: {list(inputs.keys())}")
    
    try:
        # Call the chain synchronously
        result = chain.invoke(inputs)
        
        if isinstance(result, BaseMessage):
            return result.content
        return str(result)
    except Exception as e:
        logger.error(f"Error in chain call: {str(e)}")
        raise
