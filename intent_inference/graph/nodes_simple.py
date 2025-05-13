#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simplified node implementations for the LangGraph-based intent inference workflow.

This version focuses on basic compatibility with different LangGraph versions.
"""
import re
import logging
import uuid
from typing import Dict, Any, List, TypedDict, Optional, Union, Literal

import httpx
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from models.intent.intent_spec import IntentSpec, FieldToExtract
from intent_inference.models.context import ContextStore
from intent_inference.prompts.intent_prompts import INTENT_SYSTEM_PROMPT, INTENT_USER_TEMPLATE
from intent_inference.prompts.feedback_prompts import FEEDBACK_SYSTEM_PROMPT
from intent_inference.prompts.validation_prompts import VALIDATION_SYSTEM_PROMPT
from intent_inference.utils.chain_helpers import call_llm_with_retry
from config_secrets import get_secret

# Configure module logger
logger = logging.getLogger(__name__)


# Define the state type using a TypedDict
class GraphState(TypedDict, total=False):
    """Type definition for the LangGraph state dictionary."""
    context: ContextStore
    intent_output: Optional[Dict[str, Any]]
    feedback_output: Optional[Dict[str, Any]]
    intent_spec: Optional[IntentSpec]
    validation_result: Optional[Dict[str, Any]]
    url_health_status: Optional[Dict[str, str]]


def branch_logic(state: GraphState) -> str:
    """
    Determine whether to process the user input as new intent or feedback.
    
    Args:
        state: The current graph state
        
    Returns:
        The next node to route to: "process_new_intent" or "process_feedback"
    """
    context = state.get("context")
    if not context:
        return "process_new_intent"
    
    # If the context explicitly marks this as feedback, use the feedback path
    if context.is_feedback:
        return "process_feedback"
    
    # If there's no previous spec, it must be a new intent
    if not context.last_spec:
        return "process_new_intent"
    
    # Default to new intent processing
    return "process_new_intent"


def process_new_intent(state: GraphState) -> GraphState:
    """
    Process user input as a new intent specification.
    
    Args:
        state: The current graph state
        
    Returns:
        Updated graph state with LLM intent output
    """
    context = state.get("context")
    if not context or not context.user_query:
        # If there's no context or user query, return the state unchanged
        return state
    
    try:
        # Create the prompt template
        system_prompt = INTENT_SYSTEM_PROMPT
        user_prompt = INTENT_USER_TEMPLATE
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", user_prompt)
        ])
        
        # Get the model - use a safe default API key approach
        api_key = get_secret("OPENAI_API_KEY")
        model = ChatOpenAI(
            model_name="gpt-4",
            temperature=0,
            api_key=api_key
        )
        
        # Prepare the inputs
        inputs = {"query": context.user_query}
        
        # Execute with retry logic
        result = call_llm_with_retry(
            chain=prompt | model,
            inputs=inputs
        )
        
        # Parse the output to a dictionary to avoid model-specific dependencies
        try:
            import json
            parsed_result = json.loads(result.content)
        except Exception as e:
            logger.error(f"Error parsing LLM output: {str(e)}")
            parsed_result = {
                "target_urls": ["https://example.com"],
                "fields_to_extract": [{"name": "content", "description": "Error in parsing"}],
                "technical_requirements": ["html_parsing"]
            }
        
        # Update the state with the intent output
        return {**state, "intent_output": parsed_result}
    
    except Exception as e:
        logger.error(f"Error in process_new_intent: {str(e)}")
        # Return the state unchanged in case of error
        return state


def process_feedback(state: GraphState) -> GraphState:
    """
    Process user input as feedback on an existing intent specification.
    
    Args:
        state: The current graph state
        
    Returns:
        Updated graph state with LLM feedback output
    """
    context = state.get("context")
    if not context or not context.user_query or not context.last_spec:
        # If there's no context, user query, or last spec, return the state unchanged
        return state
    
    try:
        # Create the prompt template directly
        prompt = ChatPromptTemplate.from_messages([
            ("system", FEEDBACK_SYSTEM_PROMPT),
            ("human", "Analyze this feedback: {feedback}\n\nOriginal query: {original_query}\n\nCurrent specification: {current_spec}\n\nRespond with a JSON object indicating required changes.")
        ])
        
        # Get the model - use a safe default API key approach
        api_key = get_secret("OPENAI_API_KEY")
        model = ChatOpenAI(
            model_name="gpt-4",
            temperature=0,
            api_key=api_key
        )
        
        # Prepare the inputs
        inputs = {
            "feedback": context.user_query,
            "original_query": context.last_spec.original_query,
            "current_spec": context.last_spec.model_dump_json()
        }
        
        # Execute with retry logic
        result = call_llm_with_retry(
            chain=prompt | model,
            inputs=inputs
        )
        
        # Parse the output to a dictionary to avoid model-specific dependencies
        try:
            import json
            parsed_result = json.loads(result.content)
        except Exception as e:
            logger.error(f"Error parsing LLM output: {str(e)}")
            parsed_result = {
                "changes_required": False,
                "updated_spec": context.last_spec.model_dump()
            }
        
        # Update the state with the feedback output
        return {**state, "feedback_output": parsed_result}
    
    except Exception as e:
        logger.error(f"Error in process_feedback: {str(e)}")
        # Return the state unchanged in case of error
        return state


def post_process_intent(state: GraphState) -> GraphState:
    """
    Convert the LLM intent output into a complete IntentSpec.
    
    Args:
        state: The current graph state
        
    Returns:
        Updated graph state with processed IntentSpec
    """
    context = state.get("context")
    intent_output = state.get("intent_output")
    
    if not context or not intent_output:
        # If there's no context or intent output, return the state unchanged
        return state
    
    try:
        # Create a new spec ID if this is a completely new spec
        spec_id = f"intent_{uuid.uuid4().hex[:8]}"
        
        # Extract fields from the intent output
        target_urls = intent_output.get("target_urls", ["https://example.com"])
        
        # Process fields to extract
        fields_raw = intent_output.get("fields_to_extract", [{"name": "content"}])
        fields_to_extract = []
        for field in fields_raw:
            if isinstance(field, dict):
                name = field.get("name", "")
                description = field.get("description", "")
                fields_to_extract.append(FieldToExtract(name=name, description=description))
            elif isinstance(field, str):
                fields_to_extract.append(FieldToExtract(name=field))
        
        # Get technical requirements
        tech_reqs = intent_output.get("technical_requirements", ["html_parsing"])
        
        # Get constraints
        constraints = intent_output.get("constraints", {})
        
        # Create the intent spec
        intent_spec = IntentSpec(
            spec_id=spec_id,
            original_query=context.user_query,
            target_urls=target_urls,
            fields_to_extract=fields_to_extract,
            technical_requirements=tech_reqs,
            constraints=constraints,
            validation_status="pending"
        )
        
        # Update the state with the processed intent spec
        return {**state, "intent_spec": intent_spec}
    
    except Exception as e:
        logger.error(f"Error in post_process_intent: {str(e)}")
        # Create a fallback intent spec in case of error
        fallback_spec = IntentSpec(
            spec_id=f"intent_{uuid.uuid4().hex[:8]}",
            original_query=context.user_query if context else "",
            target_urls=["https://example.com"],
            fields_to_extract=[FieldToExtract(name="content", description="Error processing intent")],
            validation_status="error",
            critique_history=["Error processing LLM output"]
        )
        return {**state, "intent_spec": fallback_spec}


def post_process_feedback(state: GraphState) -> GraphState:
    """
    Apply feedback changes to the existing IntentSpec.
    
    Args:
        state: The current graph state
        
    Returns:
        Updated graph state with updated IntentSpec
    """
    context = state.get("context")
    feedback_output = state.get("feedback_output")
    
    if not context or not feedback_output or not context.last_spec:
        # If there's no context, feedback output, or last spec, return the state unchanged
        return state
    
    try:
        # Check if changes are required
        changes_required = feedback_output.get("changes_required", False)
        
        if not changes_required:
            # If no changes are required, keep the existing spec
            return {**state, "intent_spec": context.last_spec}
        
        # Get the updated spec from the feedback output
        updated_spec_dict = feedback_output.get("updated_spec", {})
        
        # Start with the existing spec as a base
        base_spec = context.last_spec.model_dump()
        
        # Update with feedback changes
        base_spec.update(updated_spec_dict)
        
        # Convert back to an IntentSpec
        updated_spec = IntentSpec.model_validate(base_spec)
        
        # Add the feedback to the critique history
        if not updated_spec.critique_history:
            updated_spec.critique_history = []
        
        updated_spec.critique_history.append(f"User feedback: {context.user_query}")
        
        # Reset the validation status to pending
        updated_spec.validation_status = "pending"
        
        # Update the state with the updated intent spec
        return {**state, "intent_spec": updated_spec}
    
    except Exception as e:
        logger.error(f"Error in post_process_feedback: {str(e)}")
        # Return the original spec in case of error
        return {**state, "intent_spec": context.last_spec}


def validate_intent(state: GraphState) -> GraphState:
    """
    Validate the intent specification using an LLM as a judge.
    
    Args:
        state: The current graph state
        
    Returns:
        Updated graph state with validation results
    """
    context = state.get("context")
    intent_spec = state.get("intent_spec")
    
    if not context or not intent_spec:
        # If there's no context or intent spec, return the state unchanged
        return state
    
    try:
        # Create the prompt template directly
        prompt = ChatPromptTemplate.from_messages([
            ("system", VALIDATION_SYSTEM_PROMPT),
            ("human", "Evaluate if this intent specification accurately captures the user's request:\n\nUser query: {query}\n\nIntent specification: {spec}\n\nProvide your evaluation as a JSON object.")
        ])
        
        # Get the model - use a safe default API key approach
        api_key = get_secret("OPENAI_API_KEY")
        model = ChatOpenAI(
            model_name="gpt-4",
            temperature=0,
            api_key=api_key
        )
        
        # Prepare the inputs
        inputs = {
            "query": context.user_query,
            "spec": intent_spec.model_dump_json()
        }
        
        # Execute with retry logic
        result = call_llm_with_retry(
            chain=prompt | model,
            inputs=inputs
        )
        
        # Parse the output to a dictionary to avoid model-specific dependencies
        try:
            import json
            parsed_result = json.loads(result.content)
        except Exception as e:
            logger.error(f"Error parsing LLM output: {str(e)}")
            parsed_result = {
                "is_valid": False,
                "critique": ["Error validating intent"],
                "clarification_questions": ["Can you please clarify your request?"]
            }
        
        # Update intent spec with validation results
        intent_spec.validation_status = "valid" if parsed_result.get("is_valid", False) else "needs_clarification"
        
        # Add critique to the intent spec
        critique = parsed_result.get("critique", [])
        if critique and isinstance(critique, list):
            for item in critique:
                if item and item not in intent_spec.critique_history:
                    intent_spec.critique_history.append(item)
        
        # Add clarification questions to the intent spec
        questions = parsed_result.get("clarification_questions", [])
        if questions and isinstance(questions, list):
            intent_spec.clarification_questions = questions
        
        # Update the state with validation results and updated intent spec
        return {
            **state, 
            "validation_result": parsed_result, 
            "intent_spec": intent_spec
        }
    
    except Exception as e:
        logger.error(f"Error in validate_intent: {str(e)}")
        # Mark as needing clarification in case of error
        intent_spec.validation_status = "needs_clarification"
        intent_spec.critique_history.append("Error during validation")
        intent_spec.clarification_questions = ["Could you provide more details about your request?"]
        
        # Return updated state
        return {
            **state, 
            "validation_result": {"is_valid": False, "critique": ["Error during validation"]}, 
            "intent_spec": intent_spec
        }


def check_url_health(state: GraphState) -> GraphState:
    """
    Check the health of URLs in the intent specification.
    
    Args:
        state: The current graph state
        
    Returns:
        Updated graph state with URL health status
    """
    intent_spec = state.get("intent_spec")
    
    if not intent_spec or not intent_spec.target_urls:
        # If there's no intent spec or target URLs, return the state unchanged
        return state
    
    try:
        url_health = {}
        
        # Use a short timeout to avoid hanging
        timeout = httpx.Timeout(5.0)
        
        for url in intent_spec.target_urls:
            try:
                # Add http:// prefix if missing
                if not url.startswith(("http://", "https://")):
                    url = "https://" + url
                
                # Make a HEAD request to check if the URL is accessible
                with httpx.Client(timeout=timeout) as client:
                    response = client.head(url, follow_redirects=True)
                
                # Check the status code
                if response.status_code < 400:
                    url_health[url] = "healthy"
                else:
                    url_health[url] = f"error: status {response.status_code}"
            
            except Exception as e:
                url_health[url] = f"error: {str(e)}"
        
        # Update the intent spec with URL health status
        intent_spec.url_health_status = url_health
        
        # Update the state with URL health status and updated intent spec
        return {
            **state, 
            "url_health_status": url_health, 
            "intent_spec": intent_spec
        }
    
    except Exception as e:
        logger.error(f"Error in check_url_health: {str(e)}")
        # Return the state unchanged in case of error
        return state


def make_decision(state: GraphState) -> str:
    """
    Determine the next step based on validation results.
    
    Args:
        state: The current graph state
        
    Returns:
        The next node to route to: "human_review", "add_critique", or "error"
    """
    context = state.get("context")
    intent_spec = state.get("intent_spec")
    validation_result = state.get("validation_result")
    
    if not intent_spec:
        return "error"
    
    # Check for processing attempt limit
    if context and context.processing_attempt >= context.max_attempts:
        # If we've reached the maximum number of attempts, go to human review
        return "human_review"
    
    # Check validation status
    if validation_result:
        is_valid = validation_result.get("is_valid", False)
        
        if is_valid:
            # If the intent is valid, go to human review for final approval
            return "human_review"
        else:
            # If the intent is not valid, add critique and try again
            return "add_critique"
    
    # Check URL health status
    url_health = intent_spec.url_health_status
    if url_health:
        # Check if any URL is unhealthy
        unhealthy_urls = [url for url, status in url_health.items() if status != "healthy"]
        
        if unhealthy_urls:
            # If there are unhealthy URLs, go to human review
            return "human_review"
    
    # Check for critiques or clarification questions
    if intent_spec.critique_history or intent_spec.clarification_questions:
        if context and context.processing_attempt < context.max_attempts:
            # If we have critiques and haven't reached the max attempts, try again
            return "add_critique"
        else:
            # Otherwise, go to human review
            return "human_review"
    
    # Default to human review
    return "human_review"


def add_critique(state: GraphState) -> GraphState:
    """
    Add critique to the context for another iteration.
    
    Args:
        state: The current graph state
        
    Returns:
        Updated graph state with critique added to context
    """
    context = state.get("context")
    intent_spec = state.get("intent_spec")
    validation_result = state.get("validation_result")
    
    if not context or not intent_spec:
        # If there's no context or intent spec, return the state unchanged
        return state
    
    try:
        # Get critiques from the validation result
        critiques = []
        if validation_result and "critique" in validation_result:
            critiques = validation_result["critique"]
        elif intent_spec.critique_history:
            critiques = intent_spec.critique_history
        
        # Update the context
        context.critique_hints = critiques
        context.last_spec = intent_spec
        context.processing_attempt += 1
        
        # Update the state with the updated context
        return {**state, "context": context}
    
    except Exception as e:
        logger.error(f"Error in add_critique: {str(e)}")
        # Return the state unchanged in case of error
        return state


def mark_for_human_review(state: GraphState) -> GraphState:
    """
    Mark the intent spec for human review.
    
    Args:
        state: The current graph state
        
    Returns:
        Updated graph state with spec marked for human review
    """
    intent_spec = state.get("intent_spec")
    
    if not intent_spec:
        # If there's no intent spec, return the state unchanged
        return state
    
    try:
        # Set the validation status to indicate human review is needed
        if intent_spec.validation_status == "valid":
            intent_spec.validation_status = "needs_human_approval"
        else:
            intent_spec.validation_status = "needs_human_review"
        
        # Check for URL health issues
        url_health = intent_spec.url_health_status
        if url_health:
            unhealthy_urls = [url for url, status in url_health.items() if status != "healthy"]
            
            if unhealthy_urls:
                # Add a critique about URL health issues
                intent_spec.critique_history.append(
                    f"The following URLs have accessibility issues: {', '.join(unhealthy_urls)}"
                )
        
        # Update the state with the updated intent spec
        return {**state, "intent_spec": intent_spec}
    
    except Exception as e:
        logger.error(f"Error in mark_for_human_review: {str(e)}")
        # Return the state unchanged in case of error
        return state
