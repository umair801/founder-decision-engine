from app.prompts.financial_reality import FINANCIAL_REALITY_PROMPT
from app.schemas.models import FinancialRealityOutput, FounderState
from app.tools.llm import get_openai_client


def financial_reality_agent(state: FounderState) -> FounderState:
    client = get_openai_client()

    user_message = f"""
Idea Description: {state.get("idea_description", "")}
Problem Statement: {state.get("problem_statement", "")}
Target Customer: {state.get("target_customer", "")}
Validation Output: {state.get("validation_output", "None provided")}
Time Available Per Week (hours): {state.get("time_available_hours_per_week", "Not provided")}
Capital Available (USD): {state.get("capital_available_usd", "Not provided")}
Runway (months): {state.get("runway_months", "Not provided")}
"""

    response = client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": FINANCIAL_REALITY_PROMPT},
            {"role": "user", "content": user_message}
        ],
        response_format=FinancialRealityOutput,
        temperature=0.2
    )

    output: FinancialRealityOutput = response.choices[0].message.parsed

    state["financial_reality_output"] = output.model_dump()
    state["current_stage"] = "financial_reality"
    state["execution_status"] = "completed"

    return state
