"""
Feedback processing chain for intent inference.

This module provides an LLM-based chain for processing user feedback
on existing intent specifications.
"""
import os
import json
from typing import Dict, Any, Optional, cast, List
from pathlib import Path

from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain.chains import LLMChain

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


class FeedbackChain:
    """Chain for processing feedback on intent specifications."""
    
    def __init__(self, llm: BaseChatModel):
        """
        Initialize the feedback chain.
        
        Args:
            llm: Language model to use for processing
        """
        self.llm = llm
        self.prompt_template = load_feedback_prompt()
        
        # Create the prompt
        prompt = PromptTemplate.from_template(self.prompt_template)
        
        # Create the chain
        self.chain = LLMChain(
            llm=llm,
            prompt=prompt,
            output_parser=JsonOutputParser(),
            verbose=True
        )
    
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
        
        # Run the chain
        result = self.chain.run(
            original_query=original_query,
            current_spec=current_spec_json,
            user_feedback=user_feedback
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
