from app.prompts.weekly_execution import WEEKLY_EXECUTION_PROMPT
from app.schemas.models import WeeklyExecutionOutput, FounderState
from app.tools.llm import get_openai_client


def weekly_execution_agent(state: FounderState) -> FounderState:
    client = get_openai_client()

    user_message = f"""
Idea Description: {state.get("idea_description", "")}
Validation Output: {state.get("validation_output", "None provided")}
Financial Reality Output: {state.get("financial_reality_output", "None provided")}
Current Week Number: {state.get("current_week_number", 1)}
Weekly Goals: {state.get("weekly_goals", "Not provided")}
Time Available Per Week (hours): {state.get("time_available_hours_per_week", 10)}
"""

    response = client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": WEEKLY_EXECUTION_PROMPT},
            {"role": "user", "content": user_message}
        ],
        response_format=WeeklyExecutionOutput,
        temperature=0.2
    )

    output: WeeklyExecutionOutput = response.choices[0].message.parsed

    state["weekly_execution_output"] = output.model_dump()
    state["current_stage"] = "weekly_execution"
    state["execution_status"] = "completed"

    return state
