"""
Validation nodes for intent inference graph.

This module provides nodes for validating intent specifications
and handling validation results.
"""
from typing import Dict, Any, List, Optional

from langchain_core.language_models import BaseChatModel

from intent_inference.graph.state import GraphState, IntentSpec, ValidationResult, ValidationStatus
from intent_inference.graph.chains.validation_chain import ValidationChain
from intent_inference.graph.tools.url_health import check_urls_health_sync
from intent_inference.utils.visualization import add_assistant_message, add_system_message


def validate_intent(state: GraphState, llm: BaseChatModel) -> Dict[str, Any]:
    """
    Validate an intent specification using LLM-as-judge and URL health checks.
    
    Args:
        state: Current graph state
        llm: Language model to use for validation
        
    Returns:
        Updated graph state
    """
    print("========== VALIDATION NODE ENTRY ==========")
    print(f"LLM being used: {llm.__class__.__name__}, model={getattr(llm, 'model_name', 'unknown')}")
    print(f"STATE: current_intent_spec exists: {state.current_intent_spec is not None}")
    print(f"STATE: context.user_query: {state.context.user_query[:50]}...")
    messages = state.messages
    
    # Check if we have a spec to validate
    if state.current_intent_spec is None:
        error_message = "Cannot validate without an intent specification"
        messages = add_system_message(messages, f"❌ {error_message}")
        
        return {
            "state": GraphState(
                context=state.context,
                error_message=error_message,
                messages=messages
            )
        }
    
    try:
        # Add system message for validation start
        messages = add_system_message(
            messages, 
            "🔍 Validating intent specification..."
        )
        
        # Check URL health
        urls = state.current_intent_spec.target_urls_or_sites
        url_health_results = check_urls_health_sync(urls)
        
        # Update the intent spec with URL health results
        updated_spec = state.current_intent_spec.model_copy(deep=True)
        updated_spec.url_health_status = url_health_results
        
        # Add URL health results to messages
        url_messages = ["URL Health Check Results:"]
        unhealthy_urls = []
        for url, status in url_health_results.items():
            status_emoji = "✅" if status == "healthy" else "❓" if status == "unknown" else "❌"
            url_messages.append(f"- {url}: {status} {status_emoji}")
            if status != "healthy":
                unhealthy_urls.append(url)
        
        messages = add_system_message(
            messages,
            "\n".join(url_messages)
        )
        
        # Quick check for URL health issues - fail fast if all URLs are bad
        if unhealthy_urls and len(unhealthy_urls) == len(urls):
            url_issues = [f"URL {url} is inaccessible or unhealthy" for url in unhealthy_urls]
            validation_result = ValidationResult(
                is_valid=False,
                status=ValidationStatus.URL_ISSUE,
                issues=url_issues
            )
            
            # Update context with validation history
            updated_context = state.context.add_validation_history(
                validation_result, 
                spec_id=updated_spec.spec_id
            )
            
            # Add validation message
            validation_message = "❌ All target URLs are inaccessible or unhealthy:"
            for issue in validation_result.issues:
                validation_message += f"\n- {issue}"
                
            messages = add_assistant_message(
                messages,
                validation_message,
                metadata={"validation_result": validation_result.model_dump()}
            )
            
            # Return updated state with URL validation failure
            return {
                "state": GraphState(
                    context=updated_context,
                    current_intent_spec=updated_spec,
                    validation_result=validation_result,
                    messages=messages
                )
            }
        
        # Test LLM before validation to ensure it's working
        try:
            print("Testing LLM with a simple message to verify functionality...")
            test_response = llm.invoke("This is a test message. Respond with 'LLM is working' if you receive this.")
            print(f"LLM test response: {test_response}")
        except Exception as e:
            print(f"LLM TEST FAILED: {e}")
        
        # Initialize validation chain
        print("Creating ValidationChain instance...")
        validation_chain = ValidationChain(llm)
        
        # Debug the intent spec
        intent_spec_dict = updated_spec.model_dump()
        print(f"Intent spec keys: {list(intent_spec_dict.keys())}")
        print(f"Intent targets: {updated_spec.target_urls_or_sites}")
        
        # Run validation
        print("Calling ValidationChain.run()...")
        validation_result = validation_chain.run(
            user_query=state.context.user_query,
            intent_spec=updated_spec,
            url_health_results=url_health_results
        )
        print(f"ValidationChain.run() completed, result is_valid={validation_result.is_valid}")
        
        # Determine the appropriate validation status based on LLM output
        if validation_result.is_valid:
            validation_result.status = ValidationStatus.VALID
        else:
            # Analyze the issues to determine more specific status
            issues_text = ' '.join(validation_result.issues).lower()
            
            if any(word in issues_text for word in ['ambiguous', 'vague', 'unclear', 'specify', 'clarify', 'more detail']):
                validation_result.status = ValidationStatus.NEEDS_CLARIFICATION
            elif unhealthy_urls:
                validation_result.status = ValidationStatus.URL_ISSUE
            elif any(word in issues_text for word in ['missing', 'required', 'must have', 'mandatory', 'lacking']):
                validation_result.status = ValidationStatus.MISSING_DATA
            else:
                validation_result.status = ValidationStatus.INVALID
        
        # Update context with validation history
        updated_context = state.context.add_validation_history(
            validation_result, 
            spec_id=updated_spec.spec_id
        )
        
        # Add validation result to messages
        if validation_result.is_valid:
            validation_message = "✅ Intent specification is valid!"
        else:
            # Customize message based on status
            status_prefixes = {
                ValidationStatus.NEEDS_CLARIFICATION: "❓ Intent specification needs clarification:",
                ValidationStatus.URL_ISSUE: "🔗 Intent specification has URL issues:",
                ValidationStatus.MISSING_DATA: "📝 Intent specification is missing critical data:",
                ValidationStatus.INVALID: "❌ Intent specification validation failed with issues:"
            }
            validation_message = status_prefixes.get(validation_result.status, "❌ Intent specification validation failed:")
            
            for issue in validation_result.issues:
                validation_message += f"\n- {issue}"
        
        messages = add_assistant_message(
            messages,
            validation_message,
            metadata={"validation_result": validation_result.model_dump()}
        )
        
        # Return updated state
        print("========== VALIDATION NODE EXIT ==========")
        print(f"Final validation result: is_valid={validation_result.is_valid}, status={validation_result.status}")
        return {
            "state": GraphState(
                context=updated_context,  # Using updated context with history
                current_intent_spec=updated_spec,
                validation_result=validation_result,
                messages=messages
            )
        }
    
    except Exception as e:
        # Handle errors
        error_message = f"Error validating intent: {str(e)}"
        messages = add_system_message(messages, f"❌ {error_message}")
        
        return {
            "state": GraphState(
                context=state.context,
                current_intent_spec=state.current_intent_spec,
                error_message=error_message,
                messages=messages
            )
        }


def revise_with_critique(state: GraphState) -> Dict[str, Any]:
    """
    Update context with critique information.
    
    Args:
        state: Current graph state
        
    Returns:
        Updated graph state with critique hints
    """
    messages = state.messages
    
    # Check if we have validation results
    if state.validation_result is None:
        error_message = "Cannot revise without validation results"
        messages = add_system_message(messages, f"❌ {error_message}")
        
        return {
            "state": GraphState(
                context=state.context,
                current_intent_spec=state.current_intent_spec,
                error_message=error_message,
                messages=messages
            )
        }
    
    # Extract critique hints from validation issues
    critique_hints = state.validation_result.issues
    
    # Update context with critique hints
    updated_context = state.context.add_critique_hints(critique_hints)
    updated_context = updated_context.increment_iteration()
    
    # Add system message about revision
    messages = add_system_message(
        messages,
        f"🔄 Revising intent based on {len(critique_hints)} critique points (iteration {updated_context.iteration_count})"
    )
    
    # Maximum iteration check to prevent infinite recursion (termination condition)
    MAX_ITERATIONS = 5
    if updated_context.iteration_count >= MAX_ITERATIONS:
        messages = add_system_message(
            messages,
            f"⚠️ Reached maximum iterations ({MAX_ITERATIONS}). Preparing for human review despite validation issues."
        )
        
        # Set needs_human_review to true to force the graph to progress to human review
        return {
            "state": GraphState(
                context=updated_context,
                current_intent_spec=state.current_intent_spec,
                validation_result=state.validation_result,
                messages=messages,
                needs_human_review=True  # Force human review after max iterations
            )
        }
    
    # Return updated state for normal case
    return {
        "state": GraphState(
            context=updated_context,
            current_intent_spec=state.current_intent_spec,
            validation_result=state.validation_result,
            messages=messages
        )
    }
