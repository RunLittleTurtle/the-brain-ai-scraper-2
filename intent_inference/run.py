"""
Run script for intent inference graph.

This script provides a simple CLI for running the intent inference graph
and interacting with LangGraph Studio for visualization.
"""
import os
import sys
import json
import argparse
from typing import Dict, Any

from langchain_openai import ChatOpenAI
from langgraph.checkpoint import MemorySaver

from intent_inference.graph.workflow import create_intent_inference_graph, create_initial_state
from intent_inference.graph.state import GraphState, ContextStore, IntentSpec


def main():
    """Run the intent inference graph."""
    parser = argparse.ArgumentParser(description="Run intent inference graph")
    parser.add_argument("query", nargs="?", help="User query to process")
    parser.add_argument("--studio", action="store_true", help="Start LangGraph Studio server")
    args = parser.parse_args()
    
    if args.studio:
        # This is handled by the langgraph CLI
        print("Use 'langgraph dev' to start the LangGraph Studio server")
        sys.exit(0)
    
    if not args.query:
        print("Please provide a user query to process")
        sys.exit(1)
    
    # Create the graph
    llm = ChatOpenAI(
        model="gpt-4", 
        temperature=0
    )
    
    graph = create_intent_inference_graph(llm)
    
    # Create initial state
    initial_state = create_initial_state(args.query)
    
    # Run the graph
    print(f"Processing query: {args.query}")
    
    # Initialize memory saver for thread
    memory_saver = MemorySaver()
    
    # Start the graph with initial state
    thread = graph.start_with_state(initial_state, config={"configurable": {}})
    
    # Continue until human review is needed or graph completes
    while True:
        # Get the current state
        state = thread.get_state()
        
        # Print current state info
        print(f"\nCurrent state:")
        print(f"- Iteration: {state.context.iteration_count}")
        print(f"- Input type: {state.context.input_type}")
        
        if state.current_intent_spec:
            print(f"- Current intent spec: {state.current_intent_spec.spec_id}")
            print(f"  - Target URLs: {state.current_intent_spec.target_urls_or_sites}")
            print(f"  - Data fields: {[f.field_name for f in state.current_intent_spec.data_to_extract]}")
        
        if state.validation_result:
            print(f"- Validation: {'✓ Valid' if state.validation_result.is_valid else '✗ Invalid'}")
            if state.validation_result.issues:
                print(f"  - Issues: {state.validation_result.issues}")
        
        # If the graph is waiting for human review, ask for input
        if state.needs_human_review:
            print("\n🔍 Intent specification needs human review:")
            if state.current_intent_spec:
                print(f"\nIntent Specification ({state.current_intent_spec.spec_id}):")
                print(f"Original Query: {state.current_intent_spec.original_user_query}")
                print("\nTarget URLs/Sites:")
                for url in state.current_intent_spec.target_urls_or_sites:
                    health = state.current_intent_spec.url_health_status.get(url, "unknown")
                    print(f"- {url} ({'✓' if health == 'healthy' else '✗' if health == 'unhealthy' else '?'})")
                
                print("\nData to Extract:")
                for field in state.current_intent_spec.data_to_extract:
                    print(f"- {field.field_name}: {field.description}")
                
                if state.current_intent_spec.constraints:
                    print("\nConstraints:")
                    for k, v in state.current_intent_spec.constraints.items():
                        print(f"- {k}: {v}")
            
            # Ask for approval
            while True:
                response = input("\nApprove this intent specification? (y/n): ").lower()
                if response in ["y", "yes"]:
                    # Approve
                    feedback = input("Any additional notes (optional): ")
                    updated_state = state.model_copy(deep=True)
                    updated_state.human_approval = True
                    if feedback:
                        updated_state.user_feedback = feedback
                    thread.update_state(updated_state)
                    break
                elif response in ["n", "no"]:
                    # Reject
                    feedback = input("Please provide feedback for rejection: ")
                    updated_state = state.model_copy(deep=True)
                    updated_state.human_approval = False
                    updated_state.user_feedback = feedback
                    thread.update_state(updated_state)
                    break
                else:
                    print("Please enter 'y' or 'n'")
            
            # Continue the thread
            thread.continue_()
        elif thread.is_running():
            # If the thread is still running but not waiting for human input, continue
            thread.continue_()
        else:
            # If the thread has ended, get the final state and break
            final_state = thread.get_state()
            print("\n✓ Intent inference completed!")
            
            if final_state.current_intent_spec:
                print(f"\nFinal Intent Specification ({final_state.current_intent_spec.spec_id}):")
                print(json.dumps(final_state.current_intent_spec.model_dump(), indent=2))
            
            break


if __name__ == "__main__":
    main()
