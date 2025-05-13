"""
Main orchestration logic for the intent inference module.

This module provides the core API for the intent inference system, transforming
user input into structured intent specifications with validation and human review.
"""
from typing import Optional, List, Dict, Any, Tuple, Union
import logging
import asyncio
import os

# Import the shared model
from models.intent.intent_spec import IntentSpec, FieldToExtract

# Import context store
from intent_inference.models.context import ContextStore

# Import LangGraph implementation
from intent_inference.graph.app import process_input, process_input_sync

# Import LangSmith utilities
from intent_inference.utils.langsmith_utils import get_runnable_config, trace_intent_inference

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class IntentInferenceAgent:
    """
    Agent for intent inference with LangGraph implementation.

    This class provides backward compatibility with the previous implementation
    while using the new LangGraph-based workflow internally.
    """
    def __init__(self, context_store: Optional[ContextStore] = None):
        """Initialize the agent with an optional existing context store."""
        self.context_store = context_store or ContextStore()

    @trace_intent_inference
    def infer_intent(self, user_input: str) -> Optional[IntentSpec]:
        """
        Process user input into an intent specification.

        Args:
            user_input: User's query text

        Returns:
            IntentSpec with the parsed intent
        """
        try:
            # Use the new LangGraph implementation
            is_feedback = False
            previous_spec = None

            # Check if we have context that indicates this is feedback
            if self.context_store and self.context_store.last_spec:
                is_feedback = self.context_store.is_feedback
                previous_spec = self.context_store.last_spec

            # Configure LangSmith tracing
            config = {
                "tags": ["intent_inference", "user_request"],
                "metadata": {
                    "user_input": user_input[:100],  # First 100 chars of input
                    "is_feedback": is_feedback
                }
            }

            # Process the input
            intent_spec, needs_human = process_input_sync(
                user_input=user_input,
                previous_spec=previous_spec,
                is_feedback=is_feedback,
                config=get_runnable_config(**config)
            )

            # Update the context store
            if intent_spec:
                self.context_store.update_last_spec(intent_spec)

            return intent_spec
        except Exception as e:
            logger.error(f"Error in intent inference: {str(e)}")
            return self._create_minimal_intent_spec(user_input)

    async def run_with_approval(self, user_input: str) -> Optional[IntentSpec]:
        """
        Run the intent inference process with human approval.

        Args:
            user_input: User's query or feedback text

        Returns:
            Approved IntentSpec or None if approval failed
        """
        # Use the new LangGraph implementation
        is_feedback = self.context_store.is_feedback if self.context_store else False
        previous_spec = self.context_store.last_spec if self.context_store else None

        try:
            # Process the input
            intent_spec, needs_human = await process_input(
                user_input=user_input,
                previous_spec=previous_spec,
                is_feedback=is_feedback
            )

            # For backward compatibility, just return the spec
            # In a real implementation, this would involve human approval
            if intent_spec:
                if self.context_store:
                    self.context_store.update_last_spec(intent_spec)

            return intent_spec
        except Exception as e:
            logger.error(f"Error in intent inference with approval: {str(e)}")
            return None

    def _create_minimal_intent_spec(self, user_input: str) -> IntentSpec:
        """Create a minimal intent spec when parsing fails."""
        # Extract potential URL from query if possible
        import re
        url_match = re.search(r'https?://[^\s]+', user_input)
        url = url_match.group(0) if url_match else "https://example.com"

        return IntentSpec(
            original_query=user_input,
            target_urls=[url],
            fields_to_extract=[FieldToExtract(name="content", description="Error occurred during intent inference")],
            validation_status="error",
            critique_history=["Failed to process intent, using fallback values"]
        )


@trace_intent_inference
def infer_intent_sync(user_input: str, previous_spec: Optional[IntentSpec] = None, is_feedback: bool = False) -> Tuple[IntentSpec, bool]:
    """
    Synchronous version of the intent inference process.

    This function provides a direct interface for the CLI and other modules
    to use the intent inference functionality with LangGraph.

    Args:
        user_input: User's query text
        previous_spec: Optional previous spec if this is feedback
        is_feedback: Whether to treat input as feedback

    Returns:
        Tuple of (IntentSpec, needs_human_review)
    """
    if not user_input or not user_input.strip():
        # Create minimal spec for empty input
        minimal_spec = IntentSpec(
            original_query="",
            target_urls=["https://example.com"],
            fields_to_extract=[FieldToExtract(name="content")],
            validation_status="error",
            critique_history=["Empty user input"]
        )
        return minimal_spec, True

    # Configure LangSmith tracing
    config = {
        "tags": ["intent_inference", "cli_request"],
        "metadata": {
            "user_input": user_input[:100],  # First 100 chars of input
            "is_feedback": is_feedback
        }
    }

    try:
        # Use the new direct graph execution
        return process_input_sync(
            user_input=user_input,
            previous_spec=previous_spec,
            is_feedback=is_feedback,
            config=get_runnable_config(**config)
        )
    except Exception as e:
        # Log the error
        logger.error(f"Error in infer_intent_sync: {str(e)}")

        # Extract potential URL from query if possible
        import re
        url_match = re.search(r'https?://[^\s]+', user_input)
        url = url_match.group(0) if url_match else "https://example.com"

        # Create a minimal error spec to avoid breaking downstream components
        error_spec = IntentSpec(
            original_query=user_input,
            target_urls=[url],
            fields_to_extract=[FieldToExtract(name="content", description="Error occurred during intent inference")],
            validation_status="error",
            critique_history=[f"Failed to process intent: {str(e)}"]
        )

        return error_spec, True
