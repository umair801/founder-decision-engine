# backend/app/tools/supabase_client.py

import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in .env")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)


def upsert_founder_session(session_id: str, stage: str, idea_summary: str = None):
    """Create or update a founder session row."""
    data = {
        "session_id": session_id,
        "current_stage": stage,
    }
    if idea_summary:
        data["idea_summary"] = idea_summary

    supabase.table("founder_sessions").upsert(data, on_conflict="session_id").execute()


def save_stage_result(
    session_id: str,
    stage_name: str,
    input_payload: dict,
    output_payload: dict,
    total_score: int = None,
    score_breakdown: dict = None,
    verdict: str = None,
    next_action: str = None,
    supervisor_passed: bool = True,
    supervisor_feedback: str = None,
):
    """Insert or update a stage result row."""
    data = {
        "session_id": session_id,
        "stage_name": stage_name,
        "input_payload": input_payload,
        "output_payload": output_payload,
        "total_score": total_score,
        "score_breakdown": score_breakdown,
        "verdict": verdict,
        "next_action": next_action,
        "supervisor_passed": supervisor_passed,
        "supervisor_feedback": supervisor_feedback,
    }

    supabase.table("founder_stage_results").upsert(
        data, on_conflict="session_id,stage_name"
    ).execute()


def save_chat_message(
    session_id: str,
    role: str,
    content: str,
    stage_name: str = None,
    metadata: dict = None,
):
    """Append a chat message to founder_chat_messages."""
    data = {
        "session_id": session_id,
        "role": role,
        "content": content,
        "stage_name": stage_name,
        "metadata": metadata,
    }

    supabase.table("founder_chat_messages").insert(data).execute()


def get_session_progress(session_id: str) -> dict:
    """Return full session state including all completed stages."""
    session = (
        supabase.table("founder_sessions")
        .select("*")
        .eq("session_id", session_id)
        .single()
        .execute()
    )

    stages = (
        supabase.table("founder_stage_results")
        .select("stage_name, total_score, verdict, next_action, created_at")
        .eq("session_id", session_id)
        .execute()
    )

    return {
        "session": session.data,
        "completed_stages": stages.data,
    }