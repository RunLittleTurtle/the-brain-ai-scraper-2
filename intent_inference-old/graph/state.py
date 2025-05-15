"""
This is a compatibility module that re-exports from the new location.
State was moved from intent_inference/graph/state.py to intent_inference/state.py.
"""

# Re-export all symbols from the new location to maintain compatibility
from intent_inference.state import *
