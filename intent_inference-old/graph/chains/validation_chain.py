"""
Validation chain for intent inference.

This module provides an LLM-based chain for validating intent specifications
using the LLM-as-judge pattern.
"""
import json
from pathlib import Path
from typing import Dict, Any, Optional, List

from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnableLambda

from intent_inference.graph.state import ValidationResult, ValidationStatus, IntentSpec


def load_validation_prompt() -> str:
    """
    Load validation prompt template from file.
    
    Returns:
        Content of the validation prompt template
    """
    path = Path(__file__).parent.parent.parent / "prompts" / "validation_prompt.txt"
    with open(path, "r") as f:
        return f.read()


def create_validation_chat_prompt() -> ChatPromptTemplate:
    """
    Create a properly structured ChatPromptTemplate for validation.
    
    Returns:
        A ChatPromptTemplate with system instructions and validation inputs
    """
    raw = load_validation_prompt()
    print(f"Loaded validation prompt: {len(raw)} characters")
    print(f"Prompt first 50 chars: {raw[:50]}")
    print(f"Prompt last 50 chars: {raw[-50:]}")
    print(f"Contains 'Now, evaluate': {'Now, evaluate' in raw}")
    
    # We'll assume the file has markers for insertion
    try:
        system_part, rest = raw.split("Now, evaluate", 1)
        system_part = system_part.strip()
        print("Successfully split prompt at 'Now, evaluate'")
    except ValueError as e:
        print(f"ERROR: Could not split prompt: {e}")
        print("Falling back to default split at 'Example:'")
        # Fallback splitting strategy
        parts = raw.split("Example:", 1)
        system_part = parts[0].strip()
        rest = f"Example:{parts[1]}" if len(parts) > 1 else ""
    
    # Build a single HumanMessage template that covers all inputs
    human_tpl = (
        "USER QUERY: {user_query}\n\n" +
        "INTENT SPECIFICATION:\n{intent_spec}\n\n" +
        "URL HEALTH RESULTS:\n{url_health_results}\n\n" +
        "Now, evaluate the above specification."
    )
    
    return ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(system_part),
        HumanMessagePromptTemplate.from_template(human_tpl),
    ])


class ValidationChain:
    """Chain for validating intent specifications."""
    
    def __init__(self, llm: BaseChatModel):
        """
        Initialize the validation chain.
        
        Args:
            llm: Language model to use for validation
        """
        self.llm = llm
        self.prompt = create_validation_chat_prompt()
        self.parser = JsonOutputParser()
        
        # Map our three inputs into the chat prompt
        self.chain = (
            RunnableLambda(lambda inputs: {
                "user_query": inputs["user_query"],
                "intent_spec": inputs["intent_spec"],
                "url_health_results": inputs["url_health_results"],
            })
            | self.prompt
            | llm
            | self.parser
        )
    
    def run(
        self,
        user_query: str,
        intent_spec: IntentSpec,
        url_health_results: Dict[str, str],
    ) -> ValidationResult:
        """
        Validate an intent specification.
        
        Args:
            user_query: Original user query
            intent_spec: Intent specification to validate
            url_health_results: Results of URL health checks
            
        Returns:
            Validation result with issues if any
        """
        print("========== VALIDATION CHAIN RUN ==========")
        print(f"Received user_query: {user_query[:50]}...")
        print(f"Intent spec type: {type(intent_spec)}, ID: {intent_spec.spec_id}")
        print(f"URL health results: {url_health_results}")
        
        # Serialize inputs
        try:
            intent_spec_json = intent_spec.model_dump_json(indent=2)
            url_health_json = json.dumps(url_health_results, indent=2)
            print(f"Successfully serialized intent_spec ({len(intent_spec_json)} chars)")
            print(f"Successfully serialized url_health_results ({len(url_health_json)} chars)")
        except Exception as e:
            print(f"ERROR during serialization: {e}")
            return ValidationResult(
                is_valid=False,
                status=ValidationStatus.INVALID,
                issues=[f"Serialization error: {e}"],
            )
            
        inputs = {
            "user_query": user_query,
            "intent_spec": intent_spec_json,
            "url_health_results": url_health_json,
        }
        
        try:
            # Check the prompt template first
            try:
                formatted_messages = self.prompt.invoke(inputs)
                print(f"Prompt generated {len(formatted_messages)} messages")
                for i, msg in enumerate(formatted_messages):
                    print(f"Message {i+1}: type={msg.type}, content_length={len(msg.content)}")
            except Exception as prompt_error:
                print(f"ERROR during prompt formatting: {prompt_error}")
                raise prompt_error
                
            # This will truly send messages to the LLM
            print(f"Invoking LLM with prompt: {self.llm.__class__.__name__}")
            llm_output = self.chain.invoke(inputs)
            print(f"Received LLM output: {llm_output}")
        except Exception as e:
            print(f"ERROR in ValidationChain: {str(e)}")
            import traceback
            traceback.print_exc()
            return ValidationResult(
                is_valid=False,
                status=ValidationStatus.INVALID,
                issues=[f"LLM error: {e}"],
            )
        
        # llm_output is already a dict thanks to JsonOutputParser
        print(f"Parsing LLM output: {llm_output}")
        is_valid = llm_output.get("is_valid", False)
        issues = llm_output.get("issues", [])
        print(f"Extracted is_valid={is_valid}, issues_count={len(issues)}")
        
        # Determine status based on the validation result
        if is_valid:
            status = ValidationStatus.VALID
            print("Validation SUCCEEDED - status: VALID")
        else:
            # Analyze issues to determine more specific validation status
            issues_text = " ".join(issues).lower() if issues else ""
            print(f"Issues text: {issues_text[:100]}...")
            
            if any(word in issues_text for word in ['ambiguous', 'vague', 'unclear', 'specify', 'clarify', 'more detail']):
                status = ValidationStatus.NEEDS_CLARIFICATION
                print("Determined status: NEEDS_CLARIFICATION")
            elif any(word in issues_text for word in ['url', 'link', 'website', 'site', 'access']):
                status = ValidationStatus.URL_ISSUE
                print("Determined status: URL_ISSUE")
            elif any(word in issues_text for word in ['missing', 'required', 'must have', 'mandatory', 'lacking']):
                status = ValidationStatus.MISSING_DATA
                print("Determined status: MISSING_DATA")
            else:
                status = ValidationStatus.INVALID
                print("Determined status: INVALID")
        
        print(f"Validation result: valid={is_valid}, status={status}, issues_count={len(issues)}")
        print("========== VALIDATION CHAIN END ==========")
        return ValidationResult(is_valid=is_valid, status=status, issues=issues)
