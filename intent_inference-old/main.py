"""
FastAPI application for the Intent Inference module.

This module provides API endpoints for processing intent inference requests
and integrating with LangGraph Studio and LangSmith.
"""
import os
from typing import Dict, Any, Optional, List
import uuid
from datetime import datetime

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from langchain_openai import ChatOpenAI
from langgraph.persist import MemorySaver
from langsmith import Client
from langsmith.run_helpers import traceable

from intent_inference.graph.workflow import create_intent_inference_graph, create_initial_state
from intent_inference.graph.state import GraphState, InputType, ContextStore, IntentSpec


# Initialize LangSmith tracing
from intent_inference.utils.visualization import setup_langsmith_tracing
setup_langsmith_tracing()

# Initialize FastAPI app
app = FastAPI(
    title="Intent Inference API",
    description="API for processing user intents with LangGraph",
    version="0.1.0",
)

# Add CORS middleware to allow connections from LangGraph Studio
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize LLM - will read from environment variables
llm = ChatOpenAI(
    model="gpt-4",  # Default model, can be overridden by env vars
    temperature=0,  # Use deterministic output for intent inference
)

# Initialize graph with memory-based checkpointing
memory_saver = MemorySaver()
intent_graph = create_intent_inference_graph(llm).with_checkpointer(memory_saver)

# Store active threads
threads: Dict[str, Any] = {}


# Request and response models
class IntentRequest(BaseModel):
    """Request for new intent processing."""
    user_query: str


class FeedbackRequest(BaseModel):
    """Request for feedback on existing intent."""
    thread_id: str
    feedback: str


class HumanReviewRequest(BaseModel):
    """Request for human review decision."""
    thread_id: str
    approved: bool
    feedback: Optional[str] = None


class IntentResponse(BaseModel):
    """Response for intent processing."""
    thread_id: str
    state: Dict[str, Any]
    needs_human_review: bool
    intent_spec: Optional[Dict[str, Any]] = None


@app.get("/")
async def root():
    """Root endpoint for health check."""
    return {"status": "Intent Inference API is running"}


@app.post("/infer", response_model=IntentResponse)
async def infer_intent(request: IntentRequest, background_tasks: BackgroundTasks):
    """
    Process a new intent from user query.
    
    This endpoint starts a new intent inference process for the provided
    user query, returning the created thread ID and initial state.
    """
    # Create initial state
    initial_state = create_initial_state(request.user_query)
    
    # Create a new thread ID
    thread_id = f"thread_{uuid.uuid4().hex[:8]}"
    
    # Start the graph execution
    config = {"configurable": {"thread_id": thread_id}}
    thread = intent_graph.start_with_state(initial_state, config=config)
    
    # Store the thread
    threads[thread_id] = thread
    
    # Get initial state
    state = thread.get_state()
    
    return IntentResponse(
        thread_id=thread_id,
        state=state.model_dump(),
        needs_human_review=state.needs_human_review,
        intent_spec=state.current_intent_spec.model_dump() if state.current_intent_spec else None
    )


@app.post("/feedback", response_model=IntentResponse)
async def process_feedback(request: FeedbackRequest):
    """
    Process feedback for an existing intent.
    
    This endpoint processes feedback on an existing intent thread,
    continuing the intent inference process with the feedback.
    """
    # Check if thread exists
    if request.thread_id not in threads:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    # Get the thread
    thread = threads[request.thread_id]
    
    # Get the current state
    current_state = thread.get_state()
    
    # Update the state with feedback
    updated_state = current_state.model_copy(deep=True)
    updated_state.user_feedback = request.feedback
    updated_state.context = updated_state.context.convert_to_feedback(request.feedback)
    
    # Continue the thread with the updated state
    thread.update_state(updated_state)
    result = thread.continue_async()
    
    # Get the updated state
    state = thread.get_state()
    
    return IntentResponse(
        thread_id=request.thread_id,
        state=state.model_dump(),
        needs_human_review=state.needs_human_review,
        intent_spec=state.current_intent_spec.model_dump() if state.current_intent_spec else None
    )


@app.post("/human-review", response_model=IntentResponse)
async def submit_human_review(request: HumanReviewRequest):
    """
    Submit human review decision for an intent.
    
    This endpoint processes a human review decision (approval or rejection)
    for an intent that is awaiting human review.
    """
    # Check if thread exists
    if request.thread_id not in threads:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    # Get the thread
    thread = threads[request.thread_id]
    
    # Get the current state
    current_state = thread.get_state()
    
    # Update the state with human review decision
    updated_state = current_state.model_copy(deep=True)
    updated_state.human_approval = request.approved
    
    if not request.approved and request.feedback:
        updated_state.user_feedback = request.feedback
    
    # Continue the thread with the updated state
    thread.update_state(updated_state)
    result = thread.continue_async()
    
    # Get the updated state
    state = thread.get_state()
    
    return IntentResponse(
        thread_id=request.thread_id,
        state=state.model_dump(),
        needs_human_review=state.needs_human_review,
        intent_spec=state.current_intent_spec.model_dump() if state.current_intent_spec else None
    )


@app.get("/threads/{thread_id}", response_model=IntentResponse)
async def get_thread_state(thread_id: str):
    """
    Get the current state of a thread.
    
    This endpoint returns the current state of an intent inference thread.
    """
    if thread_id not in threads:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    thread = threads[thread_id]
    state = thread.get_state()
    
    return IntentResponse(
        thread_id=thread_id,
        state=state.model_dump(),
        needs_human_review=state.needs_human_review,
        intent_spec=state.current_intent_spec.model_dump() if state.current_intent_spec else None
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("intent_inference.main:app", host="0.0.0.0", port=8000, reload=True)
