"""
Nodes for processing new intent specifications from user queries.

This module provides the process_new_intent node which extracts structured
intent specifications from natural language user queries.
"""
from typing import Any, Dict
import os
from pathlib import Path

from langchain_core.prompts import PromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI

from intent_inference.state import IntentSpec, DataField, Message
from intent_inference.graph.state import GraphState


def load_prompt_template(file_name: str) -> str:
    """Load a prompt template from the prompts directory."""
    prompt_dir = Path(__file__).parents[2] / "prompts"
    prompt_path = prompt_dir / file_name
    
    if not prompt_path.exists():
        # For development, return a simple template if file doesn't exist yet
        return "You are an AI that extracts intent specifications from user queries.\n\nUser query: {query}\n\n{format_instructions}"
    
    with open(prompt_path, "r") as f:
        return f.read()


def process_new_intent(state: GraphState, llm: Any = None) -> GraphState:
    """
    Process a user query to extract or refine an intent specification.
    
    Args:
        state: The current graph state
        llm: Optional LLM instance (will use OpenAI if not provided)
    
    Returns:
        Updated graph state with a new or revised intent specification
    """
    # Create a copy of the state to avoid mutations
    state = state.model_copy(deep=True)
    
    # Get the user query from context
    user_query = state.context.get("user_query", "")
    if not user_query:
        state.error_message = "No user query provided in context"
        state.messages.append(Message(
            role="system",
            content="⚠️ Error: No user query provided"
        ))
        return state
    
    # Load the prompt template
    prompt_template = load_prompt_template("intent_prompt.txt")
    
    # Create the parser with the expected schema
    parser = JsonOutputParser(pydantic_object=dict)
    
    # Initialize the LLM if not provided
    if llm is None:
        model_name = os.getenv("OPENAI_MODEL_NAME", "gpt-4o")
        llm = ChatOpenAI(model_name=model_name, temperature=0.2)
    
    # Create the prompt with format instructions
    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["query"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    
    # Create the processing chain
    chain = (
        {"query": RunnablePassthrough()}
        | prompt
        | llm
        | parser
    )
    
    # Add system message for visualization
    state.messages.append(Message(
        role="system",
        content="Processing your query to extract intent specification..."
    ))
    
    # Add the user query as a human message
    state.messages.append(Message(
        role="human",
        content=user_query
    ))
    
    try:
        # Run the chain
        result = chain.invoke(user_query)
        
        # Parse the result into our domain models
        data_fields = [
            DataField(field_name=field["field_name"], description=field["description"])
            for field in result.get("data_to_extract", [])
        ]
        
        # Create a new intent spec
        intent_spec = IntentSpec.create_new(
            user_query=user_query,
            target_urls_or_sites=result.get("target_urls_or_sites", []),
            data_to_extract=data_fields,
            constraints=result.get("constraints", {})
        )
        
        # Store the intent spec in the state
        state.current_intent_spec = intent_spec
        
        # Add assistant message for visualization
        state.messages.append(Message(
            role="assistant",
            content=f"I've identified the following intent:\n\n"
                    f"- **URLs/Sites**: {', '.join(intent_spec.target_urls_or_sites)}\n"
                    f"- **Data Fields**: {', '.join(f.field_name for f in intent_spec.data_to_extract)}\n"
                    f"- **Constraints**: {intent_spec.constraints}"
        ))
    
    except Exception as e:
        # Handle errors
        state.error_message = f"Error processing intent: {str(e)}"
        state.messages.append(Message(
            role="system",
            content=f"⚠️ Error processing your query: {str(e)}"
        ))
    
    return state
