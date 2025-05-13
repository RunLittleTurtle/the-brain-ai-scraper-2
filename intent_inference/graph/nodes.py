#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Node implementations for the LangGraph-based intent inference workflow.

This module defines the node functions that make up the different steps
in the intent inference workflow graph.
"""
import re
import logging
from typing import Dict, Any, List, TypedDict, Optional, Union, Tuple

import httpx
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from models.intent.intent_spec import IntentSpec, FieldToExtract
from intent_inference.models.context import ContextStore
from intent_inference.models.llm_schema import LLMIntentSpec, LLMFeedback, LLMValidation
from intent_inference.prompts.intent_prompts import (
    INTENT_SYSTEM_PROMPT, 
    INTENT_USER_TEMPLATE,
    INTENT_WITH_CONTEXT_PROMPT,
    INTENT_WITH_CONTEXT_TEMPLATE
)
from intent_inference.prompts.feedback_prompts import (
    FEEDBACK_SYSTEM_PROMPT, 
    FEEDBACK_USER_TEMPLATE
)
from intent_inference.prompts.validation_prompts import (
    VALIDATION_SYSTEM_PROMPT, 
    VALIDATION_USER_TEMPLATE
)
from intent_inference.utils.chain_helpers import call_llm_with_retry
from intent_inference.utils.parsing import parse_llm_json_response


# Configure module logger
logger = logging.getLogger(__name__)


class GraphState(TypedDict):
    """Type definition for the LangGraph state dictionary."""
    context: ContextStore
    intent_output: Optional[LLMIntentSpec]
    feedback_output: Optional[LLMFeedback]
    intent_spec: Optional[IntentSpec]
    validation_result: Optional[LLMValidation]
    url_health_status: Optional[Dict[str, str]]


def branch_logic(state: GraphState) -> str:
    """
    Determine whether to process the user input as new intent or feedback.
    
    Args:
        state: The current graph state
        
    Returns:
        The next node to route to: "process_new_intent" or "process_feedback"
    """
    context = state["context"]
    
    if context.is_feedback and context.last_spec is not None:
        logger.info("Processing user input as feedback")
        return "process_feedback"
    else:
        logger.info("Processing user input as new intent")
        return "process_new_intent"


def process_new_intent(state: GraphState) -> GraphState:
    """
    Process user input as a new intent specification.
    
    Args:
        state: The current graph state
        
    Returns:
        Updated graph state with LLM intent output
    """
    context = state["context"]
    
    # Choose the appropriate prompt based on context
    if context.critique_hints:
        system_prompt = INTENT_WITH_CONTEXT_PROMPT
        template = INTENT_WITH_CONTEXT_TEMPLATE
        inputs = {
            "query": context.user_query,
            "context": "\n".join(context.critique_hints)
        }
    else:
        system_prompt = INTENT_SYSTEM_PROMPT
        template = INTENT_USER_TEMPLATE
        inputs = {"query": context.user_query}
    
    # Create the prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", template),
    ])
    
    # Get the model
    model = ChatOpenAI(temperature=0.1)
    
    # Create the chain
    chain = prompt | model | PydanticOutputParser(pydantic_object=LLMIntentSpec)
    
    try:
        # Call the chain
        logger.info(f"Calling intent extraction chain with query: {context.user_query[:50]}...")
        result = call_llm_with_retry(chain=chain, inputs=inputs)
        
        # Return updated state
        return {
            **state,
            "intent_output": result
        }
    except Exception as e:
        logger.error(f"Error in intent extraction: {str(e)}")
        # Return state with None for intent_output to indicate error
        return {
            **state,
            "intent_output": None
        }


def process_feedback(state: GraphState) -> GraphState:
    """
    Process user input as feedback on an existing intent specification.
    
    Args:
        state: The current graph state
        
    Returns:
        Updated graph state with LLM feedback output
    """
    context = state["context"]
    
    if not context.last_spec:
        logger.warning("Cannot process feedback without an existing specification")
        return {
            **state,
            "feedback_output": None
        }
    
    # Create the prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", FEEDBACK_SYSTEM_PROMPT),
        ("human", FEEDBACK_USER_TEMPLATE),
    ])
    
    # Get the model with lower temperature for more precise output
    model = ChatOpenAI(temperature=0.0)
    
    # Create the chain
    chain = prompt | model | PydanticOutputParser(pydantic_object=LLMFeedback)
    
    try:
        # Call the chain
        logger.info(f"Calling feedback processing chain with feedback: {context.user_query[:50]}...")
        result = call_llm_with_retry(
            chain=chain,
            inputs={
                "feedback": context.user_query,
                "current_spec": context.last_spec.model_dump_json(indent=2)
            }
        )
        
        # Return updated state
        return {
            **state,
            "feedback_output": result
        }
    except Exception as e:
        logger.error(f"Error in feedback processing: {str(e)}")
        # Return state with None for feedback_output to indicate error
        return {
            **state,
            "feedback_output": None
        }


def post_process_intent(state: GraphState) -> GraphState:
    """
    Convert the LLM intent output into a complete IntentSpec.
    
    Args:
        state: The current graph state
        
    Returns:
        Updated graph state with processed IntentSpec
    """
    context = state["context"]
    intent_output = state["intent_output"]
    
    if not intent_output:
        # Handle error case
        logger.warning("Cannot post-process intent output: None provided")
        # Create minimal fallback intent spec
        spec = _create_minimal_intent_spec(context.user_query)
    else:
        # Create IntentSpec from LLM output
        spec = IntentSpec(
            original_query=context.user_query,
            target_urls=intent_output.target_urls,
            fields_to_extract=[
                FieldToExtract(
                    name=field.get("name", field.get("field_name", "unknown")),
                    description=field.get("description", None)
                )
                for field in intent_output.data_to_extract
            ],
            technical_requirements=intent_output.technical_requirements,
            constraints=intent_output.constraints,
            validation_status="pending"
        )
    
    # Update context with the new spec
    context.update_last_spec(spec)
    
    # Return updated state
    return {
        **state,
        "context": context,
        "intent_spec": spec
    }


def post_process_feedback(state: GraphState) -> GraphState:
    """
    Apply feedback changes to the existing IntentSpec.
    
    Args:
        state: The current graph state
        
    Returns:
        Updated graph state with updated IntentSpec
    """
    context = state["context"]
    feedback_output = state["feedback_output"]
    
    if not context.last_spec:
        logger.warning("Cannot apply feedback: No existing spec")
        return state
    
    if not feedback_output:
        logger.warning("Cannot apply feedback: No feedback output")
        return {
            **state,
            "intent_spec": context.last_spec
        }
    
    # Create a deep copy of the existing spec
    spec = context.last_spec.model_copy(deep=True)
    
    # Update spec_id to indicate revision
    if not spec.spec_id.endswith("_rev1"):
        spec.spec_id = f"{spec.spec_id}_rev1"
    
    # Apply URL changes
    if feedback_output.target_urls_to_add:
        for url in feedback_output.target_urls_to_add:
            if url not in spec.target_urls:
                spec.target_urls.append(url)
    
    if feedback_output.target_urls_to_remove:
        spec.target_urls = [
            url for url in spec.target_urls 
            if url not in feedback_output.target_urls_to_remove
        ]
    
    # Apply field changes
    if feedback_output.fields_to_add:
        for field_dict in feedback_output.fields_to_add:
            field = FieldToExtract(
                name=field_dict.get("name", field_dict.get("field_name", "unknown")),
                description=field_dict.get("description", None)
            )
            spec.fields_to_extract.append(field)
    
    if feedback_output.fields_to_remove:
        spec.fields_to_extract = [
            field for field in spec.fields_to_extract
            if field.name not in feedback_output.fields_to_remove
        ]
    
    # Apply constraint changes
    if feedback_output.constraints_to_update:
        for key, value in feedback_output.constraints_to_update.items():
            spec.constraints[key] = value
    
    # Apply technical requirement changes
    if feedback_output.requirements_to_add:
        for req in feedback_output.requirements_to_add:
            if req not in spec.technical_requirements:
                spec.technical_requirements.append(req)
    
    # Add reasoning to history if provided
    if feedback_output.reasoning:
        if not spec.critique_history:
            spec.critique_history = []
        spec.critique_history.append(f"Feedback applied: {feedback_output.reasoning}")
    
    # Reset validation status since the spec has been modified
    spec.validation_status = "pending"
    
    # Clear any clarification questions since the user has provided input
    spec.clarification_questions = []
    
    # Update context with the revised spec
    context.update_last_spec(spec)
    
    # Return updated state
    return {
        **state,
        "context": context,
        "intent_spec": spec
    }


def validate_intent(state: GraphState) -> GraphState:
    """
    Validate the intent specification using an LLM as a judge.
    
    Args:
        state: The current graph state
        
    Returns:
        Updated graph state with validation results
    """
    intent_spec = state["intent_spec"]
    
    if not intent_spec:
        logger.warning("Cannot validate intent: No spec provided")
        return state
    
    # Create the prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", VALIDATION_SYSTEM_PROMPT),
        ("human", VALIDATION_USER_TEMPLATE),
    ])
    
    # Get the model with zero temperature for consistent validation
    model = ChatOpenAI(temperature=0)
    
    # Create the chain
    chain = prompt | model | PydanticOutputParser(pydantic_object=LLMValidation)
    
    try:
        # Call the chain
        logger.info(f"Calling validation chain for spec: {intent_spec.spec_id}")
        result = call_llm_with_retry(
            chain=chain,
            inputs={
                "spec": intent_spec.model_dump_json(indent=2),
                "query": intent_spec.original_query
            }
        )
        
        # Update the spec based on validation results
        if result.is_valid:
            intent_spec.validation_status = "validated_by_llm_judge"
        elif result.needs_clarification:
            intent_spec.validation_status = "needs_clarification"
            intent_spec.clarification_questions = result.clarification_questions
        else:
            intent_spec.validation_status = "invalid"
        
        # Add issues to critique history
        if result.issues:
            if not intent_spec.critique_history:
                intent_spec.critique_history = []
            for issue in result.issues:
                if issue not in intent_spec.critique_history:
                    intent_spec.critique_history.append(issue)
        
        # Return updated state
        return {
            **state,
            "validation_result": result,
            "intent_spec": intent_spec
        }
    except Exception as e:
        logger.error(f"Error in validation: {str(e)}")
        # Return state with None for validation_result to indicate error
        return {
            **state,
            "validation_result": None
        }


async def check_url_health(state: GraphState) -> GraphState:
    """
    Check the health of URLs in the intent specification.
    
    Args:
        state: The current graph state
        
    Returns:
        Updated graph state with URL health status
    """
    intent_spec = state["intent_spec"]
    
    if not intent_spec or not intent_spec.target_urls:
        logger.warning("Cannot check URL health: No URLs provided")
        return state
    
    results = {}
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            for url in intent_spec.target_urls:
                try:
                    # Normalize URL if needed
                    if not url.startswith(("http://", "https://")):
                        url = f"https://{url}"
                    
                    # Try HEAD request first (faster)
                    response = await client.head(url)
                    if response.status_code < 400:
                        results[url] = "healthy"
                    else:
                        # Try GET if HEAD fails (some servers don't support HEAD)
                        response = await client.get(url)
                        results[url] = "healthy" if response.status_code < 400 else "unavailable"
                except Exception as e:
                    logger.warning(f"Error checking URL {url}: {str(e)}")
                    results[url] = "error"
    except Exception as e:
        logger.error(f"Error in URL health check: {str(e)}")
    
    # Update the spec with URL health status
    intent_spec.url_health_status = results
    
    # Return updated state
    return {
        **state,
        "url_health_status": results,
        "intent_spec": intent_spec
    }


def make_decision(state: GraphState) -> str:
    """
    Determine the next step based on validation results.
    
    Args:
        state: The current graph state
        
    Returns:
        The next node to route to: "human_review", "add_critique", or "error"
    """
    validation_result = state["validation_result"]
    intent_spec = state["intent_spec"]
    context = state["context"]
    
    if not validation_result:
        logger.warning("Cannot make decision: No validation result")
        return "error"
    
    if validation_result.is_valid:
        # Check URL health as well
        url_health = state.get("url_health_status", {})
        if any(status != "healthy" for status in url_health.values()):
            logger.info("Some URLs are not healthy, adding critique")
            return "add_critique"
        
        logger.info("Intent is valid, proceeding to human review")
        return "human_review"
    elif context.processing_attempt >= context.max_attempts:
        logger.info("Maximum attempts reached, proceeding to human review despite issues")
        return "human_review"
    else:
        logger.info("Intent is invalid, adding critique and retrying")
        return "add_critique"


def add_critique(state: GraphState) -> GraphState:
    """
    Add critique to the context for another iteration.
    
    Args:
        state: The current graph state
        
    Returns:
        Updated graph state with critique added to context
    """
    validation_result = state["validation_result"]
    context = state["context"]
    intent_spec = state["intent_spec"]
    
    # Add URL health issues if any
    url_health = state.get("url_health_status", {})
    url_issues = []
    for url, status in url_health.items():
        if status != "healthy":
            url_issues.append(f"URL '{url}' is {status}")
    
    # Add validation issues
    if validation_result and validation_result.issues:
        for issue in validation_result.issues:
            context.add_critique(issue)
    
    # Add URL issues
    for issue in url_issues:
        context.add_critique(issue)
    
    # If we have clarification questions, add them to the spec
    if validation_result and validation_result.needs_clarification:
        intent_spec.clarification_questions = validation_result.clarification_questions
    
    # Return updated state
    return {
        **state,
        "context": context,
        "intent_spec": intent_spec
    }


def mark_for_human_review(state: GraphState) -> GraphState:
    """
    Mark the intent spec for human review.
    
    Args:
        state: The current graph state
        
    Returns:
        Updated graph state with spec marked for human review
    """
    intent_spec = state["intent_spec"]
    
    if not intent_spec:
        logger.warning("Cannot mark for human review: No spec provided")
        return state
    
    # Update status to indicate human review is needed
    if intent_spec.validation_status == "validated_by_llm_judge":
        # Valid but still needs human approval
        intent_spec.validation_status = "needs_human_approval"
    elif intent_spec.clarification_questions:
        # Needs clarification from user
        intent_spec.validation_status = "needs_clarification"
    else:
        # Invalid or other issues
        intent_spec.validation_status = "needs_human_review"
    
    # Return updated state
    return {
        **state,
        "intent_spec": intent_spec
    }


def _create_minimal_intent_spec(query_text: str) -> IntentSpec:
    """Create a minimal intent spec as a fallback."""
    # Extract potential URL from query if possible
    url_match = re.search(r'https?://[^\s]+', query_text)
    url = url_match.group(0) if url_match else "https://example.com"
    
    return IntentSpec(
        original_query=query_text,
        target_urls=[url],
        fields_to_extract=[FieldToExtract(name="content", description="General content")],
        validation_status="error",
        critique_history=["Failed to process intent properly, using fallback values"]
    )
