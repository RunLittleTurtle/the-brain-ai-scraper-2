# How to code the graph

# Revised Implementation Plan for Intent Inference Graph with LangGraph 0.4

This plan outlines the architecture, state management, and implementation details for building a robust intent inference module using LangGraph 0.4, Pydantic v2, and FastAPI, with focus on best practices for graph structure and visualization.

## 1. Architecture Overview

```
intent_inference/
├── __init__.py
├── graph/
│   ├── __init__.py
│   ├── state.py           # Pydantic v2 state models
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── validation_router.py  # Valid/Invalid decision
│   │   └── human_router.py       # Human approval decision
│   ├── chains/
│   │   ├── __init__.py
│   │   ├── intent_chain.py       # New intent extraction
│   │   └── validation_chain.py   # Judge chain for validation
│   ├── nodes/
│   │   ├── __init__.py
│   │   ├── intent_nodes.py       # Intent processing nodes
│   │   ├── human_nodes.py      # Human review nodes
│   │   └── validation_nodes.py   # Validation nodes
│   ├── tools/
│   │   ├── __init__.py
│   │   └── url_health.py         # URL health check tool
│   └── graph.py          # Graph construction
├── prompts/
│   ├── __init__.py
│   ├── intent_prompt.txt
│   └── validation_prompt.txt
└── utils/
    ├── __init__.py
    └── visualization.py     # Visualization helpers for LangGraph Studio
```

## 2. State Management with Pydantic v2

The `state.py` will define our models with proper state management:

```python
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field
from enum import Enum
import uuid
from datetime import datetime


class DataField(BaseModel):
    """Data field to extract from websites."""
    field_name: str
    description: str


class IntentSpec(BaseModel):
    """Intent specification model."""
    spec_id: str
    original_user_query: str
    target_urls_or_sites: List[str]
    data_to_extract: List[DataField]
    constraints: Dict[str, Any] = Field(default_factory=dict)
    url_health_status: Dict[str, str] = Field(default_factory=dict)
    validation_status: str = "pending"
    critique_history: Optional[List[str]] = None

    @classmethod
    def create_new(cls, user_query: str, **kwargs):
        """Create a new spec with a unique ID."""
        spec_id = f"intent_{uuid.uuid4().hex[:8]}"
        return cls(
            spec_id=spec_id,
            original_user_query=user_query,
            **kwargs
        )

    def create_revision(self, **updates):
        """Create a revision of this spec."""
        new_spec = self.model_copy(deep=True)

        # Update spec ID to indicate revision
        if "_rev" in new_spec.spec_id:
            base, rev_num = new_spec.spec_id.rsplit("_rev", 1)
            rev_num = int(rev_num) + 1
            new_spec.spec_id = f"{base}_rev{rev_num}"
        else:
            new_spec.spec_id = f"{new_spec.spec_id}_rev1"

        # Apply updates
        for key, value in updates.items():
            if hasattr(new_spec, key):
                setattr(new_spec, key, value)

        return new_spec


class LLMIntentSpecSchema(BaseModel):
    """Raw LLM output for new intent processing."""
    target_urls_or_sites: List[str]
    data_to_extract: List[DataField]
    constraints: Dict[str, Any] = Field(default_factory=dict)
    reasoning: str


class LLMFeedbackSchema(BaseModel):
    """Raw LLM output for feedback processing."""
    updated_target_urls: Optional[List[str]] = None
    updated_data_fields: Optional[List[DataField]] = None
    updated_constraints: Optional[Dict[str, Any]] = None
    reasoning: str
    requires_revalidation: bool = True


class InputType(str, Enum):
    NEW_INTENT = "new_intent"
    FEEDBACK = "feedback"


class ContextStore(BaseModel):
    """Context management for conversations."""
    user_query: str
    input_type: InputType = InputType.NEW_INTENT
    critique_hints: List[str] = Field(default_factory=list)
    last_spec: Optional[IntentSpec] = None
    iteration_count: int = 0
    conversation_id: str = Field(default_factory=lambda: f"conv_{uuid.uuid4().hex[:8]}")

    def increment_iteration(self):
        """Increment the iteration counter."""
        updated = self.model_copy(deep=True)
        updated.iteration_count += 1
        return updated

    def add_critique_hints(self, new_hints: List[str]):
        """Add critique hints to the context."""
        updated = self.model_copy(deep=True)
        if not updated.critique_hints:
            updated.critique_hints = []
        updated.critique_hints.extend(new_hints)
        return updated

    def update_last_spec(self, spec: IntentSpec):
        """Update the last spec in the context."""
        updated = self.model_copy(deep=True)
        updated.last_spec = spec
        return updated

    def convert_to_feedback(self, feedback_query: str):
        """Convert this context to handle feedback."""
        updated = self.model_copy(deep=True)
        updated.user_query = feedback_query
        updated.input_type = InputType.FEEDBACK
        return updated


class ValidationResult(BaseModel):
    """Validation result from the judge chain."""
    is_valid: bool
    issues: List[str] = Field(default_factory=list)


class Message(BaseModel):
    """Message for visualization."""
    role: str
    content: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    id: str = Field(default_factory=lambda: f"msg_{uuid.uuid4().hex[:8]}")
    metadata: Optional[Dict[str, Any]] = None


class GraphState(BaseModel):
    """Main state for the inference graph."""
    context: ContextStore
    current_intent_spec: Optional[IntentSpec] = None
    validation_result: Optional[ValidationResult] = None
    user_feedback: Optional[str] = None
    needs_human_review: bool = False
    human_approval: Optional[bool] = None
    error_message: Optional[str] = None

    # For LangGraph Studio visualization
    key_messages: List[Message] = Field(default_factory=list)

    # Private state for sharing between nodes
    _private: Dict[str, Any] = Field(default_factory=dict)
```

## 3. Visualization Helpers

```python
# utils/visualization.py
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
from ..graph.state import Message


def create_message(
    role: str,
    content: str,
    metadata: Optional[Dict[str, Any]] = None
) -> Message:
    """
    Create a message for visualization.

    Args:
        role: Role of the message sender (user, system, assistant, etc.)
        content: Content of the message
        metadata: Optional metadata for the message

    Returns:
        Message object for visualization
    """
    return Message(
        role=role,
        content=content,
        timestamp=datetime.now().isoformat(),
        id=f"msg_{uuid.uuid4().hex[:8]}",
        metadata=metadata
    )


def add_user_message(key_messages: List[Message], user_query: str, metadata: Optional[Dict[str, Any]] = None) -> List[Message]:
    """
    Add a user message to the key messages list.

    Args:
        key_messages: List of existing messages
        user_query: User query content
        metadata: Optional metadata

    Returns:
        Updated list of messages
    """
    new_messages = key_messages.copy()
    new_messages.append(
        create_message(
            role="user",
            content=user_query,
            metadata=metadata or {}
        )
    )
    return new_messages


def add_system_message(key_messages: List[Message], content: str, metadata: Optional[Dict[str, Any]] = None) -> List[Message]:
    """
    Add a system message to the key messages list.

    Args:
        key_messages: List of existing messages
        content: System message content
        metadata: Optional metadata

    Returns:
        Updated list of messages
    """
    new_messages = key_messages.copy()
    new_messages.append(
        create_message(
            role="system",
            content=content,
            metadata=metadata or {}
        )
    )
    return new_messages


def add_assistant_message(key_messages: List[Message], content: str, metadata: Optional[Dict[str, Any]] = None) -> List[Message]:
    """
    Add an assistant message to the key messages list.

    Args:
        key_messages: List of existing messages
        content: Assistant message content
        metadata: Optional metadata

    Returns:
        Updated list of messages
    """
    new_messages = key_messages.copy()
    new_messages.append(
        create_message(
            role="assistant",
            content=content,
            metadata=metadata or {}
        )
    )
    return new_messages
```

## 4. Router Implementation

The routers are pure decision functions that don't modify state.

### input_router.py
```python
from typing import Literal
from ..state import GraphState, InputType

def route_input(state: GraphState) -> Literal["process_new_intent", "process_feedback"]:
    """
    Routes input between new intent and feedback processing.

    This implements the "BranchLogic" decision node in the diagram.
    """
    if state.context.input_type == InputType.NEW_INTENT:
        return "process_new_intent"
    else:
        return "process_feedback"
```

### validation_router.py
```python
from typing import Literal
from ..state import GraphState

def validation_decision(state: GraphState) -> Literal["human_review", "add_critique"]:
    """
    Decides whether to proceed to human review or add critique.

    This implements the "Decision{Spec Valid & URLs OK?}" node.
    """
    if state.validation_result and state.validation_result.is_valid:
        return "human_review"
    else:
        return "add_critique"
```

### human_router.py
```python
from typing import Literal
from ..state import GraphState

def human_decision(state: GraphState) -> Literal["return_spec", "handle_feedback"]:
    """
    Routes based on human review decision.

    This corresponds to the "HumanDecision{Approved?}" node in the diagram.
    """
    if state.human_approval:
        return "return_spec"
    else:
        return "handle_feedback"
```

## 5. Message Nodes for Visualization

```python
# graph/nodes/message_nodes.py
from typing import Dict, Any
from ..state import GraphState
from ...utils.visualization import add_system_message

def log_route_decision(state: GraphState) -> Dict[str, Any]:
    """
    Log a routing decision for visualization.

    This node should be placed before a router to document the decision point.
    """
    route_type = "New Intent" if state.context.input_type == "new_intent" else "Feedback"

    new_messages = add_system_message(
        state.key_messages,
        f"Routing: {route_type} processing",
        metadata={
            "node": "input_router",
            "decision": state.context.input_type,
            "iteration": state.context.iteration_count
        }
    )

    return {"key_messages": new_messages}


def log_validation_decision(state: GraphState) -> Dict[str, Any]:
    """
    Log a validation decision for visualization.

    This node should be placed before a validation router to document the decision.
    """
    is_valid = state.validation_result and state.validation_result.is_valid
    decision = "human_review" if is_valid else "add_critique"

    new_messages = add_system_message(
        state.key_messages,
        f"Validation {'passed' if is_valid else 'failed'}",
        metadata={
            "node": "validation_decision",
            "decision": decision,
            "issues": state.validation_result.issues if not is_valid and state.validation_result else []
        }
    )

    return {"key_messages": new_messages}


def log_human_decision(state: GraphState) -> Dict[str, Any]:
    """
    Log a human review decision for visualization.

    This node should be placed before a human decision router.
    """
    decision = "return_spec" if state.human_approval else "handle_feedback"

    new_messages = add_system_message(
        state.key_messages,
        f"Human review: {'Approved' if state.human_approval else 'Rejected'}",
        metadata={
            "node": "human_decision",
            "decision": decision
        }
    )

    return {"key_messages": new_messages}
```

## 6. Node Implementation

### intent_nodes.py
```python
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from ..state import GraphState, IntentSpec, DataField
from ..chains.intent_chain import create_intent_chain
from ...utils.visualization import add_user_message, add_system_message, add_assistant_message


def process_new_intent(state: GraphState, llm: ChatOpenAI) -> Dict[str, Any]:
    """
    Process a new intent using the IntentLLMProcessing chain.

    Extracts structured information from user query and normalizes to IntentSpec.
    """
    # Create the intent chain
    intent_chain = create_intent_chain(llm)

    # Prepare critique hints if any
    critique_hints_text = ""
    if state.context.critique_hints:
        critique_hints_text = "Consider these feedback points:\n" + "\n".join([
            f"- {hint}" for hint in state.context.critique_hints
        ])

    # Update key messages with user query and processing info
    new_messages = add_user_message(
        state.key_messages,
        state.context.user_query,
        metadata={"node": "input", "iteration": state.context.iteration_count}
    )

    new_messages = add_system_message(
        new_messages,
        f"Processing intent: {state.context.user_query[:50]}...",
        metadata={"node": "process_new_intent", "hint_count": len(state.context.critique_hints)}
    )

    # Get both structured and text outputs for visualization
    try:
        llm_structured = intent_chain["json_chain"].invoke({
            "user_query": state.context.user_query,
            "critique_hints_text": critique_hints_text
        })

        llm_text = intent_chain["text_chain"].invoke({
            "user_query": state.context.user_query,
            "critique_hints_text": critique_hints_text
        })

        # Add LLM reasoning to key messages
        new_messages = add_assistant_message(
            new_messages,
            llm_text,
            metadata={"node": "intent_llm", "type": "reasoning"}
        )

        # Create the intent spec
        intent_spec = IntentSpec.create_new(
            user_query=state.context.user_query,
            target_urls_or_sites=llm_structured.get("target_urls_or_sites", []),
            data_to_extract=llm_structured.get("data_to_extract", []),
            constraints=llm_structured.get("constraints", {}),
            url_health_status={},
            validation_status="pending",
            critique_history=state.context.critique_hints.copy() if state.context.critique_hints else None
        )

        # Log the created spec
        new_messages = add_system_message(
            new_messages,
            f"Created intent spec: {intent_spec.spec_id}",
            metadata={"node": "process_new_intent", "spec_id": intent_spec.spec_id}
        )

        # Update context iteration
        updated_context = state.context.increment_iteration()

        # Return updated state fields
        return {
            "context": updated_context,
            "current_intent_spec": intent_spec,
            "key_messages": new_messages
        }

    except Exception as e:
        # Handle errors
        error_msg = f"Error processing intent: {str(e)}"
        new_messages = add_system_message(
            new_messages,
            error_msg,
            metadata={"node": "process_new_intent", "error": True}
        )

        return {
            "key_messages": new_messages,
            "error_message": error_msg
        }
```

### context_nodes.py
```python
from typing import Dict, Any
from ..state import GraphState, ContextStore, InputType
from ...utils.visualization import add_system_message


def update_context_with_spec(state: GraphState) -> Dict[str, Any]:
    """
    Update context with the latest intent spec.

    Implements the "Update Context.last_spec" node.
    """
    if not state.current_intent_spec:
        return {}

    # Create new key messages
    new_messages = add_system_message(
        state.key_messages,
        f"Updating context with spec: {state.current_intent_spec.spec_id}",
        metadata={"node": "update_context"}
    )

    # Update context with the current spec
    updated_context = state.context.update_last_spec(state.current_intent_spec)

    # Return updated state fields
    return {
        "context": updated_context,
        "key_messages": new_messages
    }


def update_context_with_critique(state: GraphState) -> Dict[str, Any]:
    """
    Update context with critique information.

    Implements the "Add Critique to Context" and "Update Context.critique_hints" nodes.
    """
    # Extract issues from validation result
    issues = state.validation_result.issues if state.validation_result else []

    if not issues:
        return {}

    # Create new key messages
    new_messages = add_system_message(
        state.key_messages,
        f"Adding {len(issues)} critiques to context",
        metadata={"node": "add_critique", "issues": issues}
    )

    # Update context with new critique hints
    updated_context = state.context.add_critique_hints(issues)

    # Return updated state fields
    return {
        "context": updated_context,
        "key_messages": new_messages
    }
```

### validation_nodes.py
```python
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from ..state import GraphState, ValidationResult, IntentSpec
from ..chains.validation_chain import create_validation_chain
from ..tools.url_health import URLHealthChecker
from ...utils.visualization import add_system_message, add_assistant_message


def validate_intent(state: GraphState, llm: ChatOpenAI) -> Dict[str, Any]:
    """
    Validates an intent specification using LLM-as-judge and URL health checks.

    Implements the "ValidationChain" subgraph including "JudgePrompt",
    "JudgeLLM", "JudgeParser", and "URLHealth" nodes.
    """
    if not state.current_intent_spec:
        # Handle missing spec
        validation_result = ValidationResult(is_valid=False, issues=["No intent specification to validate"])

        new_messages = add_system_message(
            state.key_messages,
            "Validation failed: No intent specification provided",
            metadata={"node": "validation", "validation_result": validation_result.model_dump()}
        )

        return {
            "validation_result": validation_result,
            "key_messages": new_messages
        }

    # Add validation start message
    new_messages = add_system_message(
        state.key_messages,
        f"Validating spec {state.current_intent_spec.spec_id}",
        metadata={"node": "validation"}
    )

    try:
        # Create and run validation chain (LLM-as-judge)
        validation_chain = create_validation_chain(llm)
        validation_result = validation_chain.invoke({
            "intent_spec": state.current_intent_spec.model_dump()
        })

        # Add LLM judge decision to key messages
        new_messages = add_assistant_message(
            new_messages,
            f"Validation result: {'Valid' if validation_result.is_valid else 'Invalid'}" +
                    (f" - Issues: {', '.join(validation_result.issues)}" if validation_result.issues else ""),
            metadata={"node": "judge_llm", "validation_result": validation_result.model_dump()}
        )

        # Check URL health
        url_checker = URLHealthChecker()
        urls = state.current_intent_spec.target_urls_or_sites
        url_health = url_checker.check(urls)

        # Add URL health check results to key messages
        new_messages = add_system_message(
            new_messages,
            f"URL health check results: {', '.join([f'{url}: {status}' for url, status in url_health.items()])}",
            metadata={"node": "url_health", "url_results": url_health}
        )

        # Copy and update the current spec
        updated_spec = state.current_intent_spec.model_copy(deep=True)

        # Update URL health status in spec
        updated_spec.url_health_status = url_health

        # Determine overall validation status
        url_valid = all(status == "healthy" for status in url_health.values())
        is_valid = validation_result.is_valid and url_valid

        # Collect all issues
        all_issues = validation_result.issues.copy()
        url_issues = [f"URL issue with {url}: {status}" for url, status in url_health.items() if status != "healthy"]
        all_issues.extend(url_issues)

        # Update validation status in spec
        if is_valid:
            updated_spec.validation_status = "validated"
        else:
            updated_spec.validation_status = "needs_improvement"

            # Add issues to critique history
            if not updated_spec.critique_history:
                updated_spec.critique_history = []
            updated_spec.critique_history.extend(all_issues)

        # Create final validation result
        final_validation_result = ValidationResult(
            is_valid=is_valid,
            issues=all_issues
        )

        # Return updated state fields
        return {
            "current_intent_spec": updated_spec,
            "validation_result": final_validation_result,
            "key_messages": new_messages
        }

    except Exception as e:
        # Handle errors
        error_msg = f"Error during validation: {str(e)}"
        new_messages = add_system_message(
            new_messages,
            error_msg,
            metadata={"node": "validation", "error": True}
        )

        return {
            "validation_result": ValidationResult(is_valid=False, issues=[error_msg]),
            "key_messages": new_messages,
            "error_message": error_msg
        }
```

## 7. LLM Chains Implementation

### intent_chain.py
```python
import os
from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_openai import ChatOpenAI
from ..state import LLMIntentSpecSchema


def load_prompt():
    """Load the intent prompt template from file."""
    dir_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    prompt_path = os.path.join(dir_path, "prompts", "intent_prompt.txt")

    with open(prompt_path, "r") as file:
        return file.read()


def create_intent_chain(llm: ChatOpenAI):
    """
    Create an LLM chain for processing new intents.

    Returns both structured JSON output and text output for visualization.
    """
    # Load the system prompt
    system_prompt = load_prompt()

    # Create the human message template
    human_template = """
    User Query: {user_query}

    {critique_hints_text}

    Extract the user's intent following the format requirements.
    """

    # Create the prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", human_template)
    ])

    # Create the output parsers
    json_parser = JsonOutputParser(pydantic_object=LLMIntentSpecSchema)
    text_parser = StrOutputParser()

    # Create and return the chains
    return {
        "json_chain": prompt | llm | json_parser,
        "text_chain": prompt | llm | text_parser
    }
```

### validation_chain.py
```python
import os
from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from ..state import ValidationResult


def load_prompt():
    """Load the validation prompt template from file."""
    dir_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    prompt_path = os.path.join(dir_path, "prompts", "validation_prompt.txt")

    with open(prompt_path, "r") as file:
        return file.read()


def create_validation_chain(llm: ChatOpenAI):
    """
    Create an LLM chain for validating intent specifications.

    This corresponds to the "JudgePrompt" and "JudgeLLM" nodes in the diagram.
    """
    # Load the system prompt
    system_prompt = load_prompt()

    # Create the human message template
    human_template = """
    Intent Specification to validate:

    {intent_spec}

    Evaluate whether this intent specification is valid, complete, and actionable.
    """

    # Create the prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", human_template)
    ])

    # Create the output parser
    parser = PydanticOutputParser(pydantic_object=ValidationResult)

    # Create and return the chain
    return prompt | llm | parser
```

## 8. URL Health Checker Tool

```python
from typing import List, Dict
import httpx


class URLHealthChecker:
    """
    Tool for checking the health of URLs.

    Implements the "URLHealth" node in the diagram.
    """

    def __init__(self, timeout: float = 5.0):
        """Initialize with configurable timeout."""
        self.timeout = timeout

    def check(self, urls: List[str]) -> Dict[str, str]:
        """
        Check if URLs are accessible.

        Args:
            urls: List of URLs to check

        Returns:
            Dictionary mapping URLs to their health status
        """
        results = {}
        for url in urls:
            # Add http schema if not present
            if not url.startswith(("http://", "https://")):
                url_to_check = f"https://{url}"
            else:
                url_to_check = url

            try:
                with httpx.Client(follow_redirects=True, timeout=self.timeout) as client:
                    response = client.head(url_to_check)
                    if 200 <= response.status_code < 300:
                        results[url] = "healthy"
                    else:
                        results[url] = f"unhealthy (status: {response.status_code})"
            except Exception as e:
                results[url] = f"error ({str(e)})"

        return results
```

## 9. Main Graph Assembly

```python
from typing import Dict, Any
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI

from .state import GraphState, InputType
from .routers.input_router import route_input
from .routers.validation_router import validation_decision
from .routers.human_router import human_decision
from .nodes.intent_nodes import process_new_intent
from .nodes.feedback_nodes import process_feedback
from .nodes.context_nodes import update_context_with_spec, update_context_with_critique
from .nodes.message_nodes import log_route_decision, log_validation_decision, log_human_decision
from .nodes.validation_nodes import validate_intent
from .nodes.human_nodes import prepare_for_human_review, convert_to_feedback


def create_intent_inference_graph(llm: ChatOpenAI) -> StateGraph:
    """
    Create the complete intent inference graph.

    This assembles all components into the full graph shown in the diagram.
    """
    # Initialize the workflow graph
    workflow = StateGraph(GraphState)

    # Add message logging nodes
    workflow.add_node("log_route", log_route_decision)
    workflow.add_node("log_validation", log_validation_decision)
    workflow.add_node("log_human", log_human_decision)

    # Add routers
    workflow.add_node("route_input", route_input)
    workflow.add_node("validation_decision", validation_decision)
    workflow.add_node("human_decision", human_decision)

    # Add processing nodes
    workflow.add_node("process_new_intent", lambda state: process_new_intent(state, llm))
    workflow.add_node("process_feedback", lambda state: process_feedback(state, llm))

    # Add context management nodes
    workflow.add_node("update_context", update_context_with_spec)

    # Add validation nodes
    workflow.add_node("validation", lambda state: validate_intent(state, llm))

    # Add critique and human review nodes
    workflow.add_node("add_critique", update_context_with_critique)
    workflow.add_node("human_review", prepare_for_human_review)

    # Add human decision handling nodes
    workflow.add_node("convert_to_feedback", convert_to_feedback)
    workflow.add_node("return_final_spec", lambda state: {"needs_human_review": False})

    # Connect nodes
    # Start with logging then routing
    workflow.add_edge(START, "log_route")
    workflow.add_edge("log_route", "route_input")

    # Route input based on type
    workflow.add_conditional_edges(
        "route_input",
        {
            "process_new_intent": lambda state: state.context.input_type == InputType.NEW_INTENT,
            "process_feedback": lambda state: state.context.input_type == InputType.FEEDBACK
        }
    )

    # Connect processing nodes to context update
    workflow.add_edge("process_new_intent", "update_context")
    workflow.add_edge("process_feedback", "update_context")

    # Connect to validation
    workflow.add_edge("update_context", "validation")
    workflow.add_edge("validation", "log_validation")
    workflow.add_edge("log_validation", "validation_decision")

    # Handle validation decision
    workflow.add_conditional_edges(
        "validation_decision",
        {
            "human_review": lambda state: state.validation_result and state.validation_result.is_valid,
            "add_critique": lambda state: not state.validation_result or not state.validation_result.is_valid
        }
    )

    # Connect critique back to input router (creates refinement loop)
    workflow.add_edge("add_critique", "log_route")

    # Connect human review to decision
    workflow.add_edge("human_review", "log_human")
    workflow.add_edge("log_human", "human_decision")

    # Handle human decision
    workflow.add_conditional_edges(
        "human_decision",
        {
            "return_final_spec": lambda state: state.human_approval,
            "convert_to_feedback": lambda state: not state.human_approval
        }
    )

    # Connect feedback conversion back to input router
    workflow.add_edge("convert_to_feedback", "log_route")

    # Connect final node to END
    workflow.add_edge("return_final_spec", END)

    # Add metadata for LangGraph Studio visualization
    workflow.add_metadata({
        "title": "Intent Inference Graph",
        "description": "Graph for extracting structured intent from user queries with refinement loops",
        "version": "0.4.0",
    })

    # Compile and return the graph
    return workflow.compile()
```

## 10. FastAPI Integration

```python
from fastapi import FastAPI, HTTPException, Depends, Body
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
import os
import uuid
from datetime import datetime

from .graph.state import GraphState, ContextStore, InputType, IntentSpec, Message
from .graph.workflow import create_intent_inference_graph
from .utils.visualization import create_message
from langchain_openai import ChatOpenAI

# Initialize FastAPI app
app = FastAPI(title="Intent Inference API")

# Thread storage (in production, use a database)
threads = {}

# Create LLM and graph instances at startup
llm_instance = ChatOpenAI(
    model=os.getenv("LLM_MODEL", "gpt-4-turbo-preview"),
    temperature=float(os.getenv("LLM_TEMPERATURE", "0.0"))
)
intent_graph = create_intent_inference_graph(llm_instance)


class ThreadRequest(BaseModel):
    """Request to create a new thread."""
    pass


class MessageRequest(BaseModel):
    """Request to add a message to a thread."""
    content: str


class HumanReviewRequest(BaseModel):
    """Request for human review decision."""
    approved: bool
    feedback: Optional[str] = None


@app.post("/threads/")
async def create_thread():
    """Create a new conversation thread."""
    thread_id = f"thread_{uuid.uuid4().hex[:8]}"
    threads[thread_id] = {
        "messages": [],
        "state": None,
        "created_at": datetime.now().isoformat()
    }
    return {"thread_id": thread_id}


@app.post("/threads/{thread_id}/messages/", response_model=Dict[str, Any])
async def add_message(
    thread_id: str,
    request: MessageRequest
):
    """Add a message to a thread and process it with the graph."""
    if thread_id not in threads:
        raise HTTPException(status_code=404, detail="Thread not found")

    # Add message to thread
    threads[thread_id]["messages"].append({
        "role": "user",
        "content": request.content,
        "created_at": datetime.now().isoformat()
    })

    # Determine if this is a new intent or feedback based on thread state
    is_feedback = threads[thread_id]["state"] is not None

    # Create the appropriate initial state
    if is_feedback:
        # Get previous state
        prev_state = threads[thread_id]["state"]

        # Set up context for feedback
        context = ContextStore(
            user_query=request.content,
            input_type=InputType.FEEDBACK,
            last_spec=prev_state.current_intent_spec,
            critique_hints=prev_state.context.critique_hints,
            iteration_count=prev_state.context.iteration_count,
            conversation_id=thread_id
        )

        # Create initial state with previous key messages
        initial_state = GraphState(
            context=context,
            key_messages=prev_state.key_messages
        )
    else:
        # Create new context for a first-time intent
        context = ContextStore(
            user_query=request.content,
            input_type=InputType.NEW_INTENT,
            conversation_id=thread_id
        )

        # Create initial state with user message
        initial_state = GraphState(
            context=context,
            key_messages=[
                create_message(
                    role="user",
                    content=request.content,
                    metadata={"initial": True}
                )
            ]
        )

    # Configure tracing for LangSmith if enabled
    config = {"configurable": {"thread_id": thread_id}}

    if os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true":
        from langsmith import Client
        client = Client()
        config["callbacks"] = [client.as_callback_handler()]

    # Process with the graph
    result = intent_graph.invoke(initial_state, config)

    # Store the updated state
    threads[thread_id]["state"] = result

    # Construct response based on graph state
    if result.needs_human_review:
        return {
            "thread_id": thread_id,
            "needs_human_review": True,
            "intent_spec": result.current_intent_spec.model_dump() if result.current_intent_spec else None,
            "message_history": [msg.model_dump() for msg in result.key_messages],
            "iteration": result.context.iteration_count
        }
    elif result.current_intent_spec:
        return {
            "thread_id": thread_id,
            "intent_spec": result.current_intent_spec.model_dump(),
            "needs_human_review": False,
            "message_history": [msg.model_dump() for msg in result.key_messages],
            "iteration": result.context.iteration_count
        }
    else:
        raise HTTPException(status_code=500, detail=result.error_message or "Failed to process message")


@app.post("/threads/{thread_id}/human_review/")
async def submit_human_review(
    thread_id: str,
    request: HumanReviewRequest
):
    """Submit human review decision for an intent spec."""
    if thread_id not in threads:
        raise HTTPException(status_code=404, detail="Thread not found")

    # Get the current state
    state = threads[thread_id]["state"]

    if not state.needs_human_review:
        raise HTTPException(status_code=400, detail="This thread is not awaiting human review")

    # Update the state with human decision
    updated_state = GraphState(
        context=state.context,
        current_intent_spec=state.current_intent_spec,
        validation_result=state.validation_result,
        user_feedback=request.feedback,
        needs_human_review=False,
        human_approval=request.approved,
        key_messages=state.key_messages + [
            create_message(
                role="human",
                content=f"Human review: {'Approved' if request.approved else 'Rejected'}" +
                        (f" with feedback: {request.feedback}" if request.feedback else ""),
                metadata={"node": "human_review", "approved": request.approved}
            )
        ]
    )

    # Process with the graph
    config = {"configurable": {"thread_id": thread_id}}
    result = intent_graph.invoke(updated_state, config)

    # Store the updated state
    threads[thread_id]["state"] = result

    # Return appropriate response
    if request.approved:
        return {
            "status": "approved",
            "intent_spec": result.current_intent_spec.model_dump() if result.current_intent_spec else None,
            "message_history": [msg.model_dump() for msg in result.key_messages]
        }
    else:
        return {
            "status": "feedback_processing",
            "message_history": [msg.model_dump() for msg in result.key_messages]
        }
```

## 11. Example Implementation

To ensure our implementation can handle the examples properly, we'll include example handlers:

```python
def handle_ecommerce_example():
    """Handle example 1: E-commerce Product Information."""
    # Create user query
    user_query = "I need information about Samsung TVs on BestBuy, including prices and customer reviews."

    # Create context and initial state
    context = ContextStore(
        user_query=user_query,
        input_type=InputType.NEW_INTENT
    )

    initial_state = GraphState(
        context=context,
        key_messages=[
            create_message(
                role="user",
                content=user_query
            )
        ]
    )

    # Process with the graph
    result = intent_graph.invoke(initial_state)

    # Return processed result
    if result.current_intent_spec:
        return {
            "intent_spec": result.current_intent_spec.model_dump(),
            "messages": [msg.model_dump() for msg in result.key_messages],
            "success": True
        }
    else:
        return {
            "error": result.error_message or "Failed to process intent",
            "messages": [msg.model_dump() for msg in result.key_messages],
            "success": False
        }


def handle_vague_request_with_feedback():
    """Handle Example 3: Vague Request Requiring Clarification + Feedback."""
    # Initial vague query
    vague_query = "Get stock prices from Yahoo"

    # Create context and initial state
    context = ContextStore(
        user_query=vague_query,
        input_type=InputType.NEW_INTENT
    )

    initial_state = GraphState(
        context=context,
        key_messages=[
            create_message(
                role="user",
                content=vague_query
            )
        ]
    )

    # Process with the graph - this should fail validation
    result = intent_graph.invoke(initial_state)

    # Check if validation failed as expected
    if result.validation_result and not result.validation_result.is_valid:
        # Now provide clarification
        clarification = "I want daily closing prices for Apple, Microsoft, and Google for the past month from Yahoo Finance"

        # Create feedback context using the result from previous step
        feedback_context = ContextStore(
            user_query=clarification,
            input_type=InputType.FEEDBACK,
            last_spec=result.current_intent_spec,
            critique_hints=result.validation_result.issues,
            iteration_count=result.context.iteration_count
        )

        # Create state for feedback processing
        feedback_state = GraphState(
            context=feedback_context,
            key_messages=result.key_messages + [
                create_message(
                    role="user",
                    content=clarification
                )
            ]
        )

        # Process the feedback
        feedback_result = intent_graph.invoke(feedback_state)

        # Return both the initial result and the feedback result
        return {
            "initial_query": {
                "query": vague_query,
                "is_valid": False,
                "issues": result.validation_result.issues
            },
            "clarification": {
                "query": clarification,
                "is_valid": feedback_result.validation_result and feedback_result.validation_result.is_valid,
                "intent_spec": feedback_result.current_intent_spec.model_dump() if feedback_result.current_intent_spec else None
            },
            "messages": [msg.model_dump() for msg in feedback_result.key_messages],
            "success": feedback_result.validation_result and feedback_result.validation_result.is_valid
        }
    else:
        return {
            "error": "Expected validation to fail but it did not",
            "result": result.model_dump(),
            "success": False
        }
```

## 12. Summary

This implementation plan for the intent inference graph offers:

1. **Proper State Management with Pydantic v2**:
   - Type-safe models and clear separation of concerns
   - Helper methods for state manipulation while respecting LangGraph's partial update pattern

2. **Clean Architecture**:
   - Separation of routers, nodes, and chains
   - Pure router functions that don't modify state
   - Dedicated message nodes for visualization

3. **LangGraph Studio Integration**:
   - Structured message capturing for visualization
   - Metadata tagging for nodes and decisions
   - Proper handling for LangSmith tracing

4. **Robust Error Handling**:
   - Try/except blocks in critical nodes
   - Error message field in GraphState for tracking issues

5. **Efficient Implementation**:
   - Graph created once at app startup
   - Nodes returning only the fields they modify
   - Proper handling of message history

6. **Context Management and Iterative Refinement**:
   - Clear context updates with critique history
   - Looping back for refinement when validation fails
   - Tracking of iteration count

This implementation follows best practices for LangGraph 0.4, uses Pydantic v2 properly, provides good visualization, and handles the refinement loop effectively to process the examples provided.
