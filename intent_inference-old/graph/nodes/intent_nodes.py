import json
from langchain_core.language_models import BaseChatModel
from intent_inference.graph.chains.intent_chain import IntentChain
from intent_inference.state import GraphState, IntentSpec
from intent_inference.utils.visualization import add_system_message, add_assistant_message


def process_new_intent(state: GraphState, llm: BaseChatModel) -> dict[str, GraphState]:
    """
    Node: Extract or refine an intent specification using the IntentChain.
    """
    messages = state.messages or []

    # Run the intent extraction/refinement chain
    chain = IntentChain(llm)
    schema = chain.run(state.context.user_query)

    # Build or revise the IntentSpec model
    if state.current_intent_spec is None:
        spec = IntentSpec.create_new(
            user_query=state.context.user_query,
            target_urls_or_sites=schema.target_urls_or_sites,
            data_to_extract=schema.data_to_extract,
            constraints=schema.constraints
        )
    else:
        spec = state.current_intent_spec.create_revision(
            target_urls_or_sites=schema.target_urls_or_sites,
            data_to_extract=schema.data_to_extract,
            constraints=schema.constraints
        )

    # Add messages for visualization
    messages = add_system_message(messages, "🤖 Intent spec generated/refined.")
    messages = add_assistant_message(messages, json.dumps(spec.model_dump(), indent=2), metadata={"spec_id": spec.spec_id})

    # Return the updated state
    new_state = state.model_copy(update={
        "current_intent_spec": spec,
        "messages": messages,
        "needs_human_review": False,
        "human_approval": None,
    })
    return {"state": new_state}
