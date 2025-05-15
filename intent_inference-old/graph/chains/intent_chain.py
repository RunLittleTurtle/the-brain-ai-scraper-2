"""
Intent extraction chain for intent inference.

This module provides an LLM-based chain for extracting structured 
intent specifications from user queries.
"""
import os
import json
from typing import Dict, Any, List, Optional
from pathlib import Path

from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.messages import SystemMessage, HumanMessage

from intent_inference.graph.state import LLMIntentSpecSchema, DataField


def load_intent_prompt() -> str:
    """
    Load intent prompt template from file.
    
    Returns:
        Content of the intent prompt template
    """
    # Get the directory of the current file
    current_dir = Path(__file__).parent.parent.parent
    prompt_path = current_dir / "prompts" / "intent_prompt.txt"
    
    with open(prompt_path, "r") as f:
        return f.read()

def create_chat_prompt():
    """
    Create a properly structured ChatPromptTemplate with explicit message templates.
    
    Returns:
        A ChatPromptTemplate with system instructions and user query format
    """
    # Get the prompt content
    template_content = load_intent_prompt()
    
    # Split the content - assuming everything before "USER QUERY:" is system instructions
    parts = template_content.split("USER QUERY:")
    system_instructions = parts[0].strip()
    
    # Create explicit message templates with proper HumanMessagePromptTemplate
    return ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(system_instructions),
        HumanMessagePromptTemplate.from_template("USER QUERY: {user_query}")
    ])


class IntentChain:
    """Chain for extracting intent from user queries."""
    
    def __init__(self, llm: BaseChatModel):
        """
        Initialize the intent chain.
        
        Args:
            llm: Language model to use for extraction
        """
        self.llm = llm
        
        # Create a properly structured chat prompt template
        chat_prompt = create_chat_prompt()
        
        # Create the chain with proper variable handling for LCEL
        parser = JsonOutputParser()
        
        # Create a more explicit chain with proper message formatting
        self.chain = (
            # Handle variable binding before template rendering
            RunnableLambda(lambda x: {"user_query": x})
            | chat_prompt 
            | llm 
            | parser
        )
        
        # Store the prompt for debugging
        self.prompt = chat_prompt
    
    def run(self, user_query: str) -> LLMIntentSpecSchema:
        """
        Extract intent from user query.
        
        Args:
            user_query: User's query text
            
        Returns:
            Structured intent specification
        """
        try:
            # Run the chain with proper error handling
            # Print detailed debug info to verify message formatting
            print(f"Processing user query: {user_query[:50]}{'...' if len(user_query) > 50 else ''}")
            
            # Debug the actual messages going to the LLM
            formatted_messages = self.prompt.invoke({"user_query": user_query})
            print(f"Sending messages to LLM: {formatted_messages}")
            
            # Now invoke the chain with the user query
            result = self.chain.invoke(user_query)
            
            # Parse the result with better error handling
            if isinstance(result, str):
                result_dict = json.loads(result)
            else:
                result_dict = result
                
            print(f"Intent extraction successful from query: {user_query[:30]}...")
                
        except Exception as e:
            error_msg = f"Error in IntentChain: {str(e)}"
            print(error_msg)
            
            # Provide a fallback simple result for debugging
            result_dict = {
                "target_urls_or_sites": ["example.com"],
                "data_to_extract": [{"field_name": "error", "description": f"Error occurred: {str(e)}"}],
                "constraints": {},
                "reasoning": f"Error in processing: {str(e)}"
            }
        
        # Convert data_to_extract to DataField objects
        data_fields: List[DataField] = []
        for field in result_dict.get("data_to_extract", []):
            data_fields.append(
                DataField(
                    field_name=field["field_name"],
                    description=field["description"]
                )
            )
        
        # Create LLMIntentSpecSchema
        return LLMIntentSpecSchema(
            target_urls_or_sites=result_dict.get("target_urls_or_sites", []),
            data_to_extract=data_fields,
            constraints=result_dict.get("constraints", {}),
            reasoning=result_dict.get("reasoning", "")
        )
