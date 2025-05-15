"""
Feedback processing chain for intent inference.

This module provides an LLM-based chain for processing user feedback
on existing intent specifications.
"""
import os
import json
from typing import Dict, Any, Optional, List
from pathlib import Path

from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.messages import SystemMessage, HumanMessage

from intent_inference.graph.state import LLMFeedbackSchema, DataField, IntentSpec


def load_feedback_prompt() -> str:
    """
    Load feedback prompt template from file.
    
    Returns:
        Content of the feedback prompt template
    """
    # Get the directory of the current file
    current_dir = Path(__file__).parent.parent.parent
    prompt_path = current_dir / "prompts" / "feedback_prompt.txt"
    
    with open(prompt_path, "r") as f:
        return f.read()

def create_feedback_chat_prompt():
    """
    Create a properly structured ChatPromptTemplate for feedback processing.
    
    Returns:
        A ChatPromptTemplate with system instructions and feedback inputs
    """
    # Get the basic feedback instructions
    template_content = load_feedback_prompt()
    
    # Split at the point where user inputs start
    if "CURRENT SPECIFICATION:" in template_content:
        parts = template_content.split("CURRENT SPECIFICATION:")
        system_instructions = parts[0].strip()
        
        # Create the actual feedback query format
        user_query_template = (
            "CURRENT SPECIFICATION:\n{current_spec}\n\n" +
            "USER FEEDBACK: {user_feedback}"
        )
    else:
        # Fallback if the format is different
        system_instructions = template_content
        user_query_template = (
            "ORIGINAL QUERY: {original_query}\n\n" +
            "CURRENT SPECIFICATION:\n{current_spec}\n\n" +
            "USER FEEDBACK: {user_feedback}"
        )
    
    # Create explicit message templates with proper HumanMessagePromptTemplate
    return ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(system_instructions),
        HumanMessagePromptTemplate.from_template(user_query_template)
    ])


class FeedbackChain:
    """Chain for processing feedback on intent specifications."""
    
    def __init__(self, llm: BaseChatModel):
        """
        Initialize the feedback chain.
        
        Args:
            llm: Language model to use for processing
        """
        self.llm = llm
        
        # Create a properly structured chat prompt template
        chat_prompt = create_feedback_chat_prompt()
        
        # Create the chain with proper variable handling for LCEL
        parser = JsonOutputParser()
        
        # Map inputs directly to expected template variables with chat formatting
        self.chain = (
            # Use RunnableLambda for creating the dict with expected variables
            RunnableLambda(lambda inputs: {
                "original_query": inputs["original_query"],
                "current_spec": inputs["current_spec"],
                "user_feedback": inputs["user_feedback"]
            })
            | chat_prompt 
            | llm 
            | parser
        )
        
        # Store the prompt for debugging
        self.prompt = chat_prompt
    
    def run(self, original_query: str, current_spec: IntentSpec, user_feedback: str) -> LLMFeedbackSchema:
        """
        Process feedback on an intent specification.
        
        Args:
            original_query: Original user query
            current_spec: Current intent specification
            user_feedback: User's feedback text
            
        Returns:
            Processed feedback with updates to the specification
        """
        # Format the current spec as JSON string
        current_spec_json = current_spec.model_dump_json(indent=2)
        
        try:
            # Prepare inputs
            inputs = {
                "original_query": original_query,
                "current_spec": current_spec_json,
                "user_feedback": user_feedback
            }
            
            # Debug the actual messages going to the LLM
            formatted_messages = self.prompt.invoke(inputs)
            print(f"Sending feedback messages to LLM: {len(formatted_messages)} messages")
            
            # Run the chain with proper error handling
            result = self.chain.invoke(inputs)
        except Exception as e:
            print(f"Error in FeedbackChain: {str(e)}")
            # Provide a fallback result for debugging
            return LLMFeedbackSchema(
                reasoning=f"Error in processing feedback: {str(e)}"
            )
        
        # Parse the result
        if isinstance(result, str):
            result_dict = json.loads(result)
        else:
            result_dict = result
            
        # Process updated data fields if present
        updated_data_fields = None
        if "updated_data_fields" in result_dict and result_dict["updated_data_fields"]:
            updated_data_fields = []
            for field in result_dict["updated_data_fields"]:
                updated_data_fields.append(
                    DataField(
                        field_name=field["field_name"],
                        description=field["description"]
                    )
                )
        
        # Create LLMFeedbackSchema
        return LLMFeedbackSchema(
            updated_target_urls=result_dict.get("updated_target_urls"),
            updated_data_fields=updated_data_fields,
            updated_constraints=result_dict.get("updated_constraints"),
            reasoning=result_dict.get("reasoning", ""),
            requires_revalidation=result_dict.get("requires_revalidation", True)
        )
