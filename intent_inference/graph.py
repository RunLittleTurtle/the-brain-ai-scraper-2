# intent_inference/graph/workflow.py

"""
LangGraph graph definition for intent inference.

This module defines the full intent inference graph structure,
connecting nodes, routers, and chains into a complete graph.
"""
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.runnables.config import RunnableConfig
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langsmith.run_helpers import traceable

# Import state from its actual location
from intent_inference.state import GraphState, InputType, ContextStore

# routers
from intent_inference.graph.routers.input_router import route_input
from intent_inference.graph.routers.validation_router import route_validation
from intent_inference.graph.routers.human_router import route_human_review

# nodes
from intent_inference.graph.nodes.intent_nodes import process_new_intent
from intent_inference.graph.nodes.feedback_nodes import process_feedback
from intent_inference.graph.nodes.validation_nodes import validate_intent, revise_with_critique
from intent_inference.graph.nodes.human_nodes import prepare_for_human_review, finalize_intent, process_rejection


@traceable(run_type="chain")
def create_intent_inference_graph(config: RunnableConfig) -> StateGraph:
    """
    Factory for the intent inference graph. Takes exactly one
    RunnableConfig argument (as required by LangGraph v0.4).
    """
    # ─── 1) Build the bare graph ───────────────────────────────────────────────
    graph = StateGraph(GraphState)

    # ─── 2) Wire in your LLM ───────────────────────────────────────────────────
    llm = ChatOpenAI(model_name="gpt-4", temperature=0)
    def new_intent(state): return process_new_intent(state, llm)
    def feedback  (state): return process_feedback  (state, llm)
    def validate  (state): return validate_intent   (state, llm)

    graph.add_node("process_new_intent",       new_intent)
    graph.add_node("process_feedback",         feedback)
    graph.add_node("validate_intent",          validate)
    graph.add_node("revise_with_critique",     revise_with_critique)
    graph.add_node("prepare_for_human_review", prepare_for_human_review)
    graph.add_node("process_rejection",        process_rejection)
    graph.add_node("finalize_intent",          finalize_intent)

    # ─── 3) Hook up your routing ──────────────────────────────────────────────
    # entry: dispatch NEW_INTENT vs FEEDBACK
    graph.add_conditional_edges(
        START,
        route_input,
        {
            InputType.NEW_INTENT.value: "process_new_intent",
            InputType.FEEDBACK.value:    "process_feedback",
        }
    )

    # both branches go into validation
    graph.add_edge("process_new_intent", "validate_intent")
    graph.add_edge("process_feedback",    "validate_intent")

    # validation outcome
    graph.add_conditional_edges(
        "validate_intent",
        route_validation,
        {
            "valid":   "prepare_for_human_review",
            "invalid": "revise_with_critique",
        }
    )

    # if we revise, re‐dispatch NEW_INTENT vs FEEDBACK
    graph.add_conditional_edges(
        "revise_with_critique",
        route_input,
        {
            InputType.NEW_INTENT.value: "process_new_intent",
            InputType.FEEDBACK.value:    "process_feedback",
        }
    )

    # human‐in‐the‐loop
    graph.add_conditional_edges(
        "prepare_for_human_review",
        route_human_review,
        {
            "approved": "finalize_intent",
            "rejected": "process_rejection",
            "pending":  END,
        }
    )
    graph.add_edge("process_rejection", "revise_with_critique")
    graph.add_edge("finalize_intent",   END)

    # ─── 4) Compile with a MemorySaver ────────────────────────────────────────
    saver = MemorySaver()
    return graph.compile(checkpointer=saver)


def create_initial_state(user_query: str) -> GraphState:
    """
    Helper (not part of the graph) to spin up your very first state.
    """
    ctx = ContextStore(user_query=user_query)
    return GraphState(context=ctx)
