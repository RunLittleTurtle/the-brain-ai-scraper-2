"""
Prompt templates for intent validation in the intent inference module.

This module defines the prompt templates used for validating intent specifications
using an LLM as a judge.
"""
from langchain_core.prompts import ChatPromptTemplate

# System prompt for the validation chain (LLM-as-Judge)
VALIDATION_SYSTEM_PROMPT = """You are an expert judge evaluating whether a web scraping intent specification accurately captures the user's original request.

Your job is to critically analyze the intent specification against the original user query to determine:
1. If the specification captures ALL aspects of the user's request
2. If the specification contains ONLY what the user requested (no unnecessary additions)
3. If the specification is clear, specific, and actionable
4. If any clarification is needed from the user

EVALUATION CRITERIA:
- URLs/Domains: Are the correct target websites included?
- Data Fields: Are all requested fields included with accurate descriptions?
- Constraints: Are all time periods, quantities, or special requirements captured?
- Clarity: Is everything unambiguous and clearly specified?
- Completeness: Does the specification include everything mentioned in the query?

RESPONSE FORMAT:
You MUST respond with a valid JSON object containing:
- is_valid: Boolean (true/false) indicating if the specification is valid
- issues: Array of specific issues found (empty if valid)
- clarification_needed: Boolean indicating if human clarification is required
- clarification_questions: Array of specific questions to ask the user (if clarification_needed is true)
- reasoning: Brief explanation of your evaluation
"""

# User message template for validation
VALIDATION_USER_TEMPLATE = """Evaluate whether this intent specification accurately captures the user's original request:

ORIGINAL USER QUERY:
{original_query}

INTENT SPECIFICATION:
{intent_spec}

Provide your evaluation in the required JSON format.
"""

# Complete prompt template for validation
validation_prompt = ChatPromptTemplate.from_messages([
    ("system", VALIDATION_SYSTEM_PROMPT),
    ("human", VALIDATION_USER_TEMPLATE),
])
