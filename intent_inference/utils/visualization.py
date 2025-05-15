"""
Visualization utilities for the intent inference graph.

This module provides helper functions for formatting messages and state
information for display in LangGraph Studio and CLI interfaces.
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid

from intent_inference.state import Message, IntentSpec


def add_system_message(messages: List[Message], content: str, metadata: Optional[Dict[str, Any]] = None) -> List[Message]:
    """
    Add a system message to the message list.
    
    Args:
        messages: The current list of messages
        content: The message content
        metadata: Optional metadata for the message
    
    Returns:
        Updated list of messages
    """
    new_messages = messages.copy()
    new_messages.append(Message(
        role="system",
        content=content,
        timestamp=datetime.now().isoformat(),
        id=f"msg_{uuid.uuid4().hex[:8]}",
        metadata=metadata
    ))
    return new_messages


def add_assistant_message(messages: List[Message], content: str, metadata: Optional[Dict[str, Any]] = None) -> List[Message]:
    """
    Add an assistant message to the message list.
    
    Args:
        messages: The current list of messages
        content: The message content
        metadata: Optional metadata for the message
    
    Returns:
        Updated list of messages
    """
    new_messages = messages.copy()
    new_messages.append(Message(
        role="assistant",
        content=content,
        timestamp=datetime.now().isoformat(),
        id=f"msg_{uuid.uuid4().hex[:8]}",
        metadata=metadata
    ))
    return new_messages


def add_human_message(messages: List[Message], content: str, metadata: Optional[Dict[str, Any]] = None) -> List[Message]:
    """
    Add a human message to the message list.
    
    Args:
        messages: The current list of messages
        content: The message content
        metadata: Optional metadata for the message
    
    Returns:
        Updated list of messages
    """
    new_messages = messages.copy()
    new_messages.append(Message(
        role="human",
        content=content,
        timestamp=datetime.now().isoformat(),
        id=f"msg_{uuid.uuid4().hex[:8]}",
        metadata=metadata
    ))
    return new_messages


def format_intent_spec_for_display(intent_spec: IntentSpec) -> str:
    """
    Format an intent specification for display.
    
    Args:
        intent_spec: The intent specification to format
    
    Returns:
        Formatted string representation of the intent specification
    """
    if not intent_spec:
        return "No intent specification available."
    
    # Format the spec
    formatted = f"## Intent Specification: {intent_spec.spec_id}\n\n"
    formatted += f"**Original Query**: {intent_spec.original_user_query}\n\n"
    
    # Add URLs with health status
    formatted += "**Target URLs/Sites**:\n"
    for url in intent_spec.target_urls_or_sites:
        health = intent_spec.url_health_status.get(url, "unknown")
        health_icon = "✅" if health == "healthy" else "⚠️"
        formatted += f"- {health_icon} {url}\n"
    
    # Add data fields
    formatted += "\n**Data to Extract**:\n"
    for field in intent_spec.data_to_extract:
        formatted += f"- **{field.field_name}**: {field.description}\n"
    
    # Add constraints if any
    if intent_spec.constraints:
        formatted += "\n**Constraints**:\n"
        for key, value in intent_spec.constraints.items():
            formatted += f"- **{key}**: {value}\n"
    
    return formatted
