from app.prompts.validation import VALIDATION_PROMPT
from app.schemas.models import ValidationOutput, FounderState
from app.tools.llm import get_openai_client


def validation_agent(state: FounderState) -> FounderState:
    client = get_openai_client()

    user_message = f"""
Idea Description: {state.get("idea_description", "")}
Problem Statement: {state.get("problem_statement", "")}
Target Customer: {state.get("target_customer", "")}
Customer Discovery Notes: {state.get("discovery_notes", "None provided")}
"""

    response = client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": VALIDATION_PROMPT},
            {"role": "user", "content": user_message}
        ],
        response_format=ValidationOutput,
        temperature=0.2
    )

    output: ValidationOutput = response.choices[0].message.parsed

    state["validation_output"] = output.model_dump()
    state["current_stage"] = "validation"
    state["execution_status"] = "completed"

    return state
