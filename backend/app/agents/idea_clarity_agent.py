import json
from app.prompts.idea_clarity import IDEA_CLARITY_PROMPT
from app.schemas.models import IdeaClarityOutput, FounderState
from app.tools.llm import get_openai_client


def idea_clarity_agent(state: FounderState) -> FounderState:
    client = get_openai_client()

    user_message = f"""
Idea Description: {state.get("idea_description", "")}
Problem Statement: {state.get("problem_statement", "")}
Target Customer: {state.get("target_customer", "")}
"""

    response = client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": IDEA_CLARITY_PROMPT},
            {"role": "user", "content": user_message}
        ],
        response_format=IdeaClarityOutput,
        temperature=0.2
    )

    output: IdeaClarityOutput = response.choices[0].message.parsed

    state["idea_clarity_output"] = output.model_dump()
    state["current_stage"] = "idea_clarity"
    state["execution_status"] = "completed"

    return state
