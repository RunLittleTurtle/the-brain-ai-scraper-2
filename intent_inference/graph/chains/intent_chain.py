"""
Intent extraction chain for intent inference.

This module provides an LLM-based chain for extracting structured 
intent specifications from user queries.
"""
import os
import json
from typing import Dict, Any, Optional, cast, List
from pathlib import Path

from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain

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


class IntentChain:
    """Chain for extracting intent from user queries."""
    
    def __init__(self, llm: BaseChatModel):
        """
        Initialize the intent chain.
        
        Args:
            llm: Language model to use for extraction
        """
        self.llm = llm
        self.prompt_template = load_intent_prompt()
        
        # Create the prompt
        prompt = PromptTemplate.from_template(self.prompt_template)
        
        # Create the chain
        self.chain = LLMChain(
            llm=llm,
            prompt=prompt,
            output_parser=JsonOutputParser(),
            verbose=True
        )
    
    def run(self, user_query: str) -> LLMIntentSpecSchema:
        """
        Extract intent from user query.
        
        Args:
            user_query: User's query text
            
        Returns:
            Structured intent specification
        """
        # Run the chain
        result = self.chain.run(user_query=user_query)
        
        # Parse the result
        if isinstance(result, str):
            result_dict = json.loads(result)
        else:
            result_dict = result
        
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
