"""
Intent inference package for web scraping intent extraction and validation.

This package uses LangGraph to provide a structured workflow for processing
user queries into formal intent specifications for web scraping tasks.
"""

from .state import DataField, IntentSpec
from .graph.graph import create_intent_inference_graph, create_initial_state

__all__ = [
    "create_intent_inference_graph",
    "create_initial_state",
    "DataField",
    "IntentSpec",
]
