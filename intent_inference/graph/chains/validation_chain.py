"""
Validation chain for intent inference.

This module provides an LLM-based chain for validating intent specifications
using the LLM-as-judge pattern.
"""
import os
import json
from typing import Dict, Any, Optional, cast
from pathlib import Path

from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain.chains import LLMChain

from intent_inference.graph.state import ValidationResult, IntentSpec


def load_validation_prompt() -> str:
    """
    Load validation prompt template from file.
    
    Returns:
        Content of the validation prompt template
    """
    # Get the directory of the current file
    current_dir = Path(__file__).parent.parent.parent
    prompt_path = current_dir / "prompts" / "validation_prompt.txt"
    
    with open(prompt_path, "r") as f:
        return f.read()


class ValidationChain:
    """Chain for validating intent specifications."""
    
    def __init__(self, llm: BaseChatModel):
        """
        Initialize the validation chain.
        
        Args:
            llm: Language model to use for validation
        """
        self.llm = llm
        self.prompt_template = load_validation_prompt()
        
        # Create the prompt
        prompt = PromptTemplate.from_template(self.prompt_template)
        
        # Create the chain
        self.chain = LLMChain(
            llm=llm,
            prompt=prompt,
            output_parser=JsonOutputParser(),
            verbose=True
        )
    
    def run(self, user_query: str, intent_spec: IntentSpec, url_health_results: Dict[str, str]) -> ValidationResult:
        """
        Validate an intent specification.
        
        Args:
            user_query: Original user query
            intent_spec: Intent specification to validate
            url_health_results: Results of URL health checks
            
        Returns:
            Validation result with issues if any
        """
        # Format the intent spec as JSON string
        intent_spec_json = intent_spec.model_dump_json(indent=2)
        
        # Format URL health results
        url_health_json = json.dumps(url_health_results, indent=2)
        
        # Run the chain
        result = self.chain.run(
            user_query=user_query,
            intent_spec=intent_spec_json,
            url_health_results=url_health_json
        )
        
        # Parse the result
        if isinstance(result, str):
            result_dict = json.loads(result)
        else:
            result_dict = result
        
        # Create ValidationResult
        return ValidationResult(
            is_valid=result_dict.get("is_valid", False),
            issues=result_dict.get("issues", [])
        )
