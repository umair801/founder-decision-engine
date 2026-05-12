import os
import json
import logging
from openai import OpenAI
from app.schemas.models import SupervisorValidation

logger = logging.getLogger(__name__)


def _get_client():
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ── AgAI_26: Vague output detection ─────────────────────────────────────────
# These phrases are hard failure conditions in the Founder Decision Engine.
# Any agent output containing these phrases fails supervisor validation.

VAGUE_PHRASES = [
    "it depends",
    "consider exploring",
    "you might want to",
    "think about",
    "could potentially",
    "may or may not",
    "it's hard to say",
    "further research",
    "gather more information",
    "it varies",
    "depends on the situation",
    "there are many factors",
    "it is possible that",
    "you should explore",
    "worth considering",
]

REQUIRED_ACTION_VERBS = [
    "interview", "research", "define", "build", "test",
    "write", "send", "contact", "launch", "record",
    "publish", "validate", "measure", "schedule", "create", "conduct", "analyze", "draft", "identify", "estimate"
]

# ── AgAI_24 baseline: GPT-4o supervisor prompt ───────────────────────────────
SUPERVISOR_SYSTEM_PROMPT = """You are a strict quality supervisor for the Founder Decision Engine.
You will receive:
1. The agent type that produced the output
2. The original task given to that agent
3. The output the agent produced

Your job is to evaluate the output and return a JSON object with exactly these keys:
{
  "score": <float between 0.0 and 1.0>,
  "verdict": <"approved" | "retry" | "escalate">,
  "reason": <one sentence explaining your verdict>,
  "suggestions": <one sentence on how to improve, or empty string if approved>
}

Scoring guide:
- 0.9 - 1.0: Output fully answers the task, no gaps, all fields populated
- 0.7 - 0.89: Output mostly answers the task, minor gaps
- 0.5 - 0.69: Output partially answers the task, significant gaps
- 0.0 - 0.49: Output fails to answer the task, is empty, or contains vague advice

Verdict rules:
- score >= 0.65: verdict = "approved"
- 0.35 <= score < 0.65: verdict = "retry"
- score < 0.35: verdict = "escalate"

Founder Decision Engine specific rules:
- Any output containing vague phrases ("it depends", "consider exploring") must score below 0.5
- Any output missing a numeric score must score below 0.5
- Any output missing a concrete next action must score below 0.5
- Motivational language in execution plans must score below 0.5

Return ONLY the JSON object. No markdown, no explanation, no backticks."""

CONFIDENCE_THRESHOLD = 0.65


def _detect_vague_outputs(output_str: str) -> list[str]:
    """
    Scan output string for forbidden vague phrases.
    Returns list of vague phrases found.
    """
    output_lower = output_str.lower()
    return [phrase for phrase in VAGUE_PHRASES if phrase in output_lower]


def _detect_missing_fields(output: dict, stage: str) -> list[str]:
    """
    Check required fields are present and non-empty per stage.
    Returns list of missing field names.
    """
    required_fields = {
        "idea_clarity": ["total_score", "verdict", "gap_analysis", "required_next_action"],
        "customer_discovery": ["discovery_questions", "readiness_score", "gate_passed"],
        "validation": ["total_score", "verdict", "confidence_score", "recommended_next_step"],
        "financial_reality": ["estimates", "viability_score", "recommendation", "reasoning"],
        "weekly_execution": ["actions", "week_focus", "total_estimated_hours"],
    }

    fields = required_fields.get(stage, [])
    missing = []
    for field in fields:
        value = output.get(field)
        if value is None or value == "" or value == []:
            missing.append(field)
    return missing


def _validate_action_verb(action_text: str) -> bool:
    """
    Check that a required next action starts with an approved action verb.
    """
    first_word = action_text.strip().lower().split()[0] if action_text.strip() else ""
    return first_word in REQUIRED_ACTION_VERBS


def run_supervisor_validation(
    stage: str,
    output: dict,
) -> SupervisorValidation:
    """
    AgAI_26 primary supervisor function.
    Runs two layers of validation:
      Layer 1: Rule-based vague output and missing field detection (instant, no API call)
      Layer 2: GPT-4o quality scoring (catches issues Layer 1 misses)

    Args:
        stage:  The agent stage that produced the output.
        output: The structured dict output from the agent.

    Returns:
        SupervisorValidation Pydantic object.
    """
    output_str = json.dumps(output)

    # ── Layer 1: Rule-based checks ───────────────────────────────────────────
    vague_found = _detect_vague_outputs(output_str)
    missing_fields = _detect_missing_fields(output, stage)

    # Check action verb on relevant stages
    if stage == "idea_clarity":
        action = output.get("required_next_action", "")
        if action and not _validate_action_verb(action):
            vague_found.append(f"required_next_action does not start with an action verb: '{action[:60]}'")

    if stage == "validation":
        step = output.get("recommended_next_step", "")
        if step and not _validate_action_verb(step):
            vague_found.append(f"recommended_next_step does not start with an action verb: '{step[:60]}'")

    # Hard fail on Layer 1
    if vague_found or missing_fields:
        reason_parts = []
        if vague_found:
            reason_parts.append(f"Vague phrases detected: {vague_found}")
        if missing_fields:
            reason_parts.append(f"Missing required fields: {missing_fields}")

        logger.warning(f"Supervisor Layer 1 FAILED for stage '{stage}': {reason_parts}")

        return SupervisorValidation(
            passed=False,
            vague_outputs_found=vague_found,
            missing_fields=missing_fields,
            override_reason=" | ".join(reason_parts)
        )

    # ── Layer 2: GPT-4o quality scoring ─────────────────────────────────────
    try:
        prompt = (
            f"Agent stage: {stage}\n\n"
            f"Agent output:\n{output_str}"
        )

        response = _get_client().chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SUPERVISOR_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0,
            max_tokens=300,
        )

        raw = response.choices[0].message.content
        cleaned = raw.strip().strip("```json").strip("```").strip()
        verdict_data = json.loads(cleaned)
        score = float(verdict_data.get("score", 0.0))

        if score >= CONFIDENCE_THRESHOLD:
            logger.info(f"Supervisor Layer 2 PASSED for stage '{stage}' (score={score:.2f})")
            return SupervisorValidation(
                passed=True,
                vague_outputs_found=[],
                missing_fields=[],
                override_reason=None
            )
        else:
            reason = verdict_data.get("reason", "Output quality below threshold.")
            logger.warning(f"Supervisor Layer 2 FAILED for stage '{stage}' (score={score:.2f}): {reason}")
            return SupervisorValidation(
                passed=False,
                vague_outputs_found=[],
                missing_fields=[],
                override_reason=f"GPT-4o quality score {score:.2f} below threshold {CONFIDENCE_THRESHOLD}: {reason}"
            )

    except Exception as e:
        logger.error(f"Supervisor Layer 2 error for stage '{stage}': {str(e)}")
        return SupervisorValidation(
            passed=False,
            vague_outputs_found=[],
            missing_fields=[],
            override_reason=f"Supervisor Layer 2 internal error: {str(e)}"
        )

