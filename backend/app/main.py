import os
import pathlib
from dotenv import load_dotenv

# Absolute path to .env — resolves correctly regardless of working directory
_ENV_PATH = pathlib.Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=_ENV_PATH, override=True)

# Verify key loaded — will log on startup
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
_key_check = os.getenv("OPENAI_API_KEY", "")
logger.info(f"OPENAI_API_KEY loaded: {'YES - ' + _key_check[:8] if _key_check else 'NO - MISSING'}")

import uuid
from fastapi import FastAPI, HTTPException
from app.tools.supabase_client import (
    upsert_founder_session,
    save_stage_result,
    save_chat_message,
)
from fastapi.middleware.cors import CORSMiddleware
from app.schemas.models import FounderInput, FounderResponse, SupervisorValidation
from app.agents.orchestrator import founder_graph

app = FastAPI(
    title="Founder Decision Engine",
    description="AI-powered operating system for early-stage founders. Structured decisions, numeric scoring, zero vague advice.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STAGE_SEQUENCE = [
    "idea_clarity",
    "customer_discovery",
    "validation",
    "financial_reality",
    "weekly_execution"
]


def _get_next_stage(current_stage: str) -> str | None:
    try:
        idx = STAGE_SEQUENCE.index(current_stage)
        return STAGE_SEQUENCE[idx + 1] if idx + 1 < len(STAGE_SEQUENCE) else None
    except ValueError:
        return None


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "Founder Decision Engine",
        "version": "1.0.0",
        "stages": STAGE_SEQUENCE
    }


@app.post("/api/founder/run", response_model=FounderResponse)
def run_founder_stage(input: FounderInput):
    session_id = input.session_id or str(uuid.uuid4())

    state = {
        "session_id": session_id,
        "current_stage": input.stage,
        "idea_description": input.idea_description or "",
        "problem_statement": input.problem_statement or "",
        "target_customer": input.target_customer or "",
        "discovery_notes": input.discovery_notes or "",
        "time_available_hours_per_week": input.time_available_hours_per_week or 10,
        "capital_available_usd": input.capital_available_usd or 0,
        "runway_months": input.runway_months or 0,
        "current_week_number": input.current_week_number or 1,
        "weekly_goals": input.weekly_goals or "",
        "errors": [],
        "retry_count": 0,
        "execution_status": "running",
        "blocked": False,
    }

    try:
        result = founder_graph.invoke(state)
    except Exception as e:
        logger.error(f"Graph execution failed for session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {str(e)}")

    output_key = f"{input.stage}_output"
    agent_output = result.get(output_key, result.get("final_output", {}))

    sv_raw = result.get("supervisor_validation", {})
    supervisor = SupervisorValidation(
        passed=sv_raw.get("passed", False),
        vague_outputs_found=sv_raw.get("vague_outputs_found", []),
        missing_fields=sv_raw.get("missing_fields", []),
        override_reason=sv_raw.get("override_reason", None)
    )

    blocked = result.get("blocked", False)
    blocking_message = result.get("blocking_message", None)
    next_stage = None if blocked else _get_next_stage(input.stage)

    # Persist session and stage result to Supabase
    try:
        upsert_founder_session(
            session_id=session_id,
            stage=input.stage,
            idea_summary=input.idea_description or input.problem_statement or None,
        )

        save_stage_result(
            session_id=session_id,
            stage_name=input.stage,
            input_payload=input.model_dump(),
            output_payload=agent_output if isinstance(agent_output, dict) else {},
            total_score=agent_output.get("total_score") if isinstance(agent_output, dict) else None,
            score_breakdown=agent_output.get("score_breakdown") if isinstance(agent_output, dict) else None,
            verdict=agent_output.get("verdict") if isinstance(agent_output, dict) else None,
            next_action=agent_output.get("next_action") if isinstance(agent_output, dict) else None,
            supervisor_passed=supervisor.passed,
            supervisor_feedback=str(supervisor.vague_outputs_found) if supervisor.vague_outputs_found else None,
        )

        save_chat_message(
            session_id=session_id,
            role="assistant",
            content=str(agent_output),
            stage_name=input.stage,
            metadata={"blocked": blocked, "supervisor_passed": supervisor.passed},
        )

    except Exception as db_error:
        logger.warning(f"Supabase write failed for session {session_id}: {str(db_error)}")
        # Do not raise — DB failure must not break the API response

    return FounderResponse(
        session_id=session_id,
        stage=input.stage,
        output=agent_output,
        supervisor_validation=supervisor,
        next_stage=next_stage,
        blocked=blocked,
        blocking_message=blocking_message
    )


@app.get("/api/stages")
def list_stages():
    return {
        "stages": [
            {"stage": "idea_clarity", "description": "Score your idea across 4 dimensions"},
            {"stage": "customer_discovery", "description": "Generate discovery questions and check readiness gate"},
            {"stage": "validation", "description": "Score market validation from discovery notes"},
            {"stage": "financial_reality", "description": "Calculate build cost, time to revenue, break-even"},
            {"stage": "weekly_execution", "description": "Get a structured 5-item weekly action plan"}
        ]
    }
