from app.prompts.customer_discovery import CUSTOMER_DISCOVERY_PROMPT
from app.schemas.models import CustomerDiscoveryOutput, FounderState
from app.tools.llm import get_openai_client


def customer_discovery_agent(state: FounderState) -> FounderState:
    client = get_openai_client()

    user_message = f"""
Idea Description: {state.get("idea_description", "")}
Problem Statement: {state.get("problem_statement", "")}
Target Customer: {state.get("target_customer", "")}
Discovery Notes (if any): {state.get("discovery_notes", "None provided")}
"""

    response = client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": CUSTOMER_DISCOVERY_PROMPT},
            {"role": "user", "content": user_message}
        ],
        response_format=CustomerDiscoveryOutput,
        temperature=0.2
    )

    output: CustomerDiscoveryOutput = response.choices[0].message.parsed

    state["customer_discovery_output"] = output.model_dump()
    state["current_stage"] = "customer_discovery"
    state["gate_passed"] = output.gate_passed
    state["execution_status"] = "completed"

    if not output.gate_passed:
        state["blocked"] = True
        state["blocking_message"] = output.blocking_reason or "Customer discovery score below 60. Complete required actions before proceeding."
    else:
        state["blocked"] = False
        state["blocking_message"] = None

    return state
