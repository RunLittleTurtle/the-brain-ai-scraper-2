"""
Main orchestration logic for the intent inference module.

This module implements the IntentInferenceAgent which orchestrates the flow between
different chains and manages the context to transform user input into valid intent
specifications with human approval.
"""
from typing import Tuple, Union, List, Dict, Any, Optional
import asyncio
import logging

from .models.intent_spec import IntentSpec
from .models.context import ContextStore
from .chains.intent_chain import create_intent_extraction_chain, convert_to_intent_spec
from .chains.feedback_chain import create_feedback_processing_chain, apply_feedback_to_spec
from .chains.validation_chain import validate_intent_spec


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class IntentInferenceAgent:
    """Main agent for intent inference with human approval"""
    
    def __init__(self, context_store: Optional[ContextStore] = None):
        """Initialize the agent with an optional existing context store."""
        self.context_store = context_store or ContextStore()
    
    async def infer_intent(self, user_input: str) -> Tuple[IntentSpec, bool]:
        """Process user input into an intent specification and validate it.
        
        Args:
            user_input: User's query or feedback text
            
        Returns:
            Tuple of (validated intent spec, is_valid flag)
        """
        # Set user input in context store
        self.context_store.set_user_query(user_input)
        
        try:
            # Process based on whether this is new intent or feedback
            if self.context_store.last_spec and self._is_feedback(user_input):
                logger.info("Processing user input as feedback on existing spec")
                self.context_store.is_feedback = True
                await self._process_feedback()
            else:
                logger.info("Processing user input as new intent")
                self.context_store.is_feedback = False
                await self._process_new_intent()
            
            # Validate the resulting spec
            logger.info("Validating intent specification")
            spec, is_valid, issues, clarification_questions = await self._validate_spec()
            
            # If validation failed and we should retry, do so
            if not is_valid and self.context_store.should_retry():
                logger.info(f"Validation failed with issues: {issues}. Retrying.")
                return await self.infer_intent(user_input)  # Recursive retry
            
            return spec, is_valid
            
        except Exception as e:
            logger.error(f"Error in intent inference: {str(e)}")
            # If we have a partial spec, return it with validation failed
            if self.context_store.last_spec:
                self.context_store.last_spec.validation_status = "error"
                if not self.context_store.last_spec.critique_history:
                    self.context_store.last_spec.critique_history = []
                self.context_store.last_spec.critique_history.append(f"Error: {str(e)}")
                return self.context_store.last_spec, False
            # Otherwise create a minimal error spec
            error_spec = IntentSpec(
                original_user_query=user_input,
                target_urls_or_sites=[],
                data_to_extract=[],
                validation_status="error",
                critique_history=[f"Failed to process intent: {str(e)}"]  
            )
            return error_spec, False
    
    def _is_feedback(self, user_input: str) -> bool:
        """Determine if user input is likely feedback on an existing spec.
        
        Args:
            user_input: User's input text
            
        Returns:
            True if the input appears to be feedback
        """
        # Simple heuristic - could be enhanced with more sophisticated detection
        feedback_indicators = [
            "instead", "change", "modify", "update", "add", "remove", 
            "replace", "not quite", "incorrect", "no, ", "actually", "but"
        ]
        
        # Check if any indicators are present
        return any(indicator in user_input.lower() for indicator in feedback_indicators)
    
    async def _process_new_intent(self) -> None:
        """Process a new intent from scratch using the intent extraction chain."""
        # Get the user query
        user_query = self.context_store.user_query
        if not user_query:
            raise ValueError("No user query available in context")
        
        # Use context-aware prompt if we have critique hints
        use_context = len(self.context_store.critique_hints) > 0
        
        # Create and run the intent extraction chain
        intent_chain = create_intent_extraction_chain(use_context=use_context)
        
        # Prepare inputs including any critique hints
        chain_inputs = {"user_query": user_query}
        if use_context:
            chain_inputs["critique_hints"] = "\n".join(self.context_store.critique_hints)
        
        # Extract the intent
        intent_output = await intent_chain.ainvoke(chain_inputs)
        
        # Convert to IntentSpec and update context
        intent_spec = convert_to_intent_spec(
            output=intent_output, 
            user_query=user_query,
            existing_spec=None  # This is a new spec, not an update
        )
        
        # Update context
        self.context_store.update_last_spec(intent_spec)
    
    async def _process_feedback(self) -> None:
        """Process feedback on an existing intent using the feedback chain."""
        # Get the user feedback and last spec
        user_feedback = self.context_store.user_query
        last_spec = self.context_store.last_spec
        
        if not user_feedback or not last_spec:
            raise ValueError("Missing user feedback or previous specification in context")
        
        # Use context-aware prompt if we have critique hints
        use_context = len(self.context_store.critique_hints) > 0
        
        # Create and run the feedback processing chain
        feedback_chain = create_feedback_processing_chain(use_context=use_context)
        
        # Prepare inputs
        chain_inputs = {
            "user_feedback": user_feedback,
            "current_spec": last_spec.model_dump_json(indent=2)
        }
        if use_context:
            chain_inputs["critique_hints"] = "\n".join(self.context_store.critique_hints)
        
        # Process the feedback
        feedback_output = await feedback_chain.ainvoke(chain_inputs)
        
        # Apply feedback to the existing spec
        updated_spec = apply_feedback_to_spec(
            feedback_result=feedback_output,
            existing_spec=last_spec
        )
        
        # Update context
        self.context_store.update_last_spec(updated_spec)
    
    async def _validate_spec(self) -> Tuple[IntentSpec, bool, List[str], Optional[List[str]]]:
        """Validate the current intent specification using the validation chain.
        
        Returns:
            Tuple of (updated spec, is_valid flag, list of issues, clarification questions)
        """
        # Get the current spec
        spec = self.context_store.last_spec
        if not spec:
            raise ValueError("No specification available to validate")
        
        # Validate the spec (includes URL health checks)
        updated_spec, is_valid, issues, clarification_questions = await validate_intent_spec(spec)
        
        # Update context
        self.context_store.update_last_spec(updated_spec)
        
        # If not valid, add critique hints to context for next iteration
        if not is_valid and issues:
            for issue in issues:
                self.context_store.add_critique(issue)
        
        return updated_spec, is_valid, issues, clarification_questions
    
    async def run_with_approval(self, user_input: str) -> Optional[IntentSpec]:
        """Run the full inference process with human approval.
        
        This method orchestrates the entire process from initial inference to human approval.
        
        Args:
            user_input: User's query or feedback text
            
        Returns:
            Approved IntentSpec or None if approval failed
        """
        # Process the input and get a valid spec
        spec, is_valid = await self.infer_intent(user_input)
        
        # Return only if valid (needs human approval in cli.py)
        if is_valid:
            # Update status to ready for human approval
            spec.validation_status = "ready_for_human_approval"
            return spec
        else:
            # Return the spec anyway, so the human can see the issues
            return spec


# Synchronous wrapper for easier integration
def infer_intent_sync(user_input: str) -> Optional[IntentSpec]:
    """Synchronous version of the intent inference process.
    
    This function provides a simple synchronous interface for the CLI and other modules
    to use the intent inference functionality without dealing with async/await.
    
    Args:
        user_input: User's query or feedback text
        
    Returns:
        Approved IntentSpec or None if approval failed
    """
    try:
        # Initialize the agent
        agent = IntentInferenceAgent()
        
        # Run the async process and return the result
        return asyncio.run(agent.run_with_approval(user_input))
    except Exception as e:
        # Log the error
        logger.error(f"Error in infer_intent_sync: {str(e)}")
        
        # Create a minimal error spec to avoid breaking downstream components
        error_spec = IntentSpec(
            original_user_query=user_input,
            target_urls_or_sites=["https://example.com"],  # Fallback URL
            data_to_extract=[ExtractedField(field_name="error", description="Error occurred during intent inference")],
            validation_status="error",
            critique_history=[f"Failed to process intent: {str(e)}"]
        )
        
        return error_spec