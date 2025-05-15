"""
Visualization helpers for LangGraph Studio.

This module provides utility functions for enriching the graph state
with visualization-friendly messages and metadata for LangGraph Studio.
"""
from typing import Dict, Any, List, Optional, cast
from datetime import datetime
import json
import os

from langsmith.run_helpers import traceable

from intent_inference.graph.state import GraphState, Message, IntentSpec


def add_user_message(messages: List[Message], content: str, metadata: Optional[Dict[str, Any]] = None) -> List[Message]:
    """
    Add a user message to the key messages list.
    
    Args:
        messages: Current list of messages
        content: Message content
        metadata: Optional metadata for the message
        
    Returns:
        Updated list with new message added
    """
    new_messages = messages.copy()
    new_messages.append(
        Message(
            role="user",
            content=content,
            timestamp=datetime.now().isoformat(),
            metadata=metadata or {}
        )
    )
    return new_messages


def add_assistant_message(messages: List[Message], content: str, metadata: Optional[Dict[str, Any]] = None) -> List[Message]:
    """
    Add an assistant message to the key messages list.
    
    Args:
        messages: Current list of messages
        content: Message content
        metadata: Optional metadata for the message
        
    Returns:
        Updated list with new message added
    """
    new_messages = messages.copy()
    new_messages.append(
        Message(
            role="assistant",
            content=content,
            timestamp=datetime.now().isoformat(),
            metadata=metadata or {}
        )
    )
    return new_messages


def add_system_message(messages: List[Message], content: str, metadata: Optional[Dict[str, Any]] = None) -> List[Message]:
    """
    Add a system message to the key messages list.
    
    Args:
        messages: Current list of messages
        content: Message content
        metadata: Optional metadata for the message
        
    Returns:
        Updated list with new message added
    """
    new_messages = messages.copy()
    new_messages.append(
        Message(
            role="system",
            content=content,
            timestamp=datetime.now().isoformat(),
            metadata=metadata or {}
        )
    )
    return new_messages


def format_intent_spec_for_display(intent_spec: IntentSpec) -> str:
    """
    Format an intent specification for human-readable display.
    
    Args:
        intent_spec: The intent specification to format
        
    Returns:
        Formatted string representation
    """
    lines = [
        f"## Intent Specification ({intent_spec.spec_id})",
        f"**Original Query:** {intent_spec.original_user_query}",
        "",
        "**Target URLs/Sites:**",
    ]
    
    for url in intent_spec.target_urls_or_sites:
        health_status = intent_spec.url_health_status.get(url, "unknown")
        status_emoji = "✅" if health_status == "healthy" else "❓" if health_status == "unknown" else "❌"
        lines.append(f"- {url} {status_emoji}")
    
    lines.extend(["", "**Data to Extract:**"])
    for field in intent_spec.data_to_extract:
        lines.append(f"- **{field.field_name}**: {field.description}")
    
    if intent_spec.constraints:
        lines.extend(["", "**Constraints:**"])
        for k, v in intent_spec.constraints.items():
            lines.append(f"- **{k}**: {v}")
    
    if intent_spec.critique_history:
        lines.extend(["", "**Critique History:**"])
        for critique in intent_spec.critique_history:
            lines.append(f"- {critique}")
    
    return "\n".join(lines)


@traceable(run_type="tool")
def create_state_representation(state: GraphState) -> Dict[str, Any]:
    """
    Create a JSON-compatible representation of the current state for visualization.
    
    Args:
        state: Current graph state
        
    Returns:
        JSON-compatible dictionary
    """
    repr_data: Dict[str, Any] = {
        "context": {
            "user_query": state.context.user_query,
            "input_type": state.context.input_type,
            "iteration_count": state.context.iteration_count,
            "conversation_id": state.context.conversation_id,
        }
    }
    
    if state.context.critique_hints:
        repr_data["context"]["critique_hints"] = state.context.critique_hints
    
    if state.current_intent_spec:
        repr_data["current_intent_spec"] = {
            "spec_id": state.current_intent_spec.spec_id,
            "target_urls_count": len(state.current_intent_spec.target_urls_or_sites),
            "data_fields_count": len(state.current_intent_spec.data_to_extract),
            "constraints_count": len(state.current_intent_spec.constraints),
            "validation_status": state.current_intent_spec.validation_status,
        }
    
    if state.validation_result:
        repr_data["validation_result"] = {
            "is_valid": state.validation_result.is_valid,
            "issues_count": len(state.validation_result.issues),
        }
    
    if state.needs_human_review:
        repr_data["needs_human_review"] = True
        
    if state.human_approval is not None:
        repr_data["human_approval"] = state.human_approval
        
    if state.error_message:
        repr_data["error_message"] = state.error_message
        
    return repr_data


def setup_langsmith_tracing() -> None:
    """
    Set up LangSmith tracing based on environment variables.
    This should be called at the start of any script that uses the intent inference graph.
    """
    langsmith_api_key = os.environ.get("LANGSMITH_API_KEY")
    langsmith_project = os.environ.get("LANGSMITH_PROJECT", "brain-ai-scraper")
    
    if langsmith_api_key:
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_PROJECT"] = langsmith_project
        print(f"LangSmith tracing enabled for project: {langsmith_project}")
    else:
        print("LangSmith API key not found. Tracing is disabled.")


def create_studio_metadata(state: GraphState) -> Dict[str, Any]:
    """
    Create metadata specifically formatted for LangGraph Studio visualization.
    
    Args:
        state: Current graph state
        
    Returns:
        Studio-compatible metadata dictionary
    """
    metadata = {
        "studio": {
            "state_type": "intent_inference",
            "iteration": state.context.iteration_count,
            "messages": [msg.model_dump() for msg in state.messages],
        }
    }
    
    if state.current_intent_spec:
        metadata["studio"]["intent_spec"] = {
            "id": state.current_intent_spec.spec_id,
            "urls": state.current_intent_spec.target_urls_or_sites,
            "fields": [field.field_name for field in state.current_intent_spec.data_to_extract],
            "status": state.current_intent_spec.validation_status
        }
    
    return metadata
