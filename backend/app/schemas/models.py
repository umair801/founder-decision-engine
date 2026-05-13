from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from typing_extensions import TypedDict


# ============================================================
# MODULE 1 — Idea Clarity Agent Schemas
# ============================================================

class IdeaClarityScores(BaseModel):
    problem_clarity: int = Field(..., ge=0, le=25, description="How clearly the problem is defined")
    target_customer: int = Field(..., ge=0, le=25, description="How specific the target customer is")
    differentiation: int = Field(..., ge=0, le=25, description="How differentiated the solution is")
    founder_market_fit: int = Field(..., ge=0, le=25, description="How well the founder fits the market")

class IdeaClarityOutput(BaseModel):
    scores: IdeaClarityScores
    total_score: int = Field(..., ge=0, le=100)
    verdict: Literal["strong", "needs_work", "weak"]
    gap_analysis: List[str] = Field(..., min_length=1, description="List of specific gaps found")
    required_next_action: str = Field(..., description="One concrete actionable task, never vague")


# ============================================================
# MODULE 2 — Customer Discovery Agent Schemas
# ============================================================

class DiscoveryQuestion(BaseModel):
    question_number: int = Field(..., ge=1, le=5)
    question: str
    purpose: str = Field(..., description="Why this question matters for validation")

class CustomerDiscoveryOutput(BaseModel):
    discovery_questions: List[DiscoveryQuestion] = Field(..., min_length=5, max_length=5)
    readiness_score: int = Field(..., ge=0, le=100)
    gate_passed: bool = Field(..., description="True if score >= 60, False blocks progression")
    blocking_reason: Optional[str] = Field(None, description="Required if gate_passed is False")
    required_actions: List[str] = Field(default_factory=list, description="Actions required if gate not passed")


# ============================================================
# MODULE 3 — Validation and Scoring Agent Schemas
# ============================================================

class ValidationScores(BaseModel):
    problem_confirmation: int = Field(..., ge=0, le=25, description="Evidence that the problem is real")
    willingness_to_pay: int = Field(..., ge=0, le=25, description="Evidence customers will pay")
    competitive_landscape: int = Field(..., ge=0, le=25, description="Clarity on competition")
    tam_estimate: int = Field(..., ge=0, le=25, description="Total addressable market size estimate")

class ValidationOutput(BaseModel):
    scores: ValidationScores
    total_score: int = Field(..., ge=0, le=100)
    verdict: Literal["validated", "not_validated", "needs_more_data"]
    confidence_score: int = Field(..., ge=0, le=100)
    recommended_next_step: str = Field(..., description="One concrete next step, never vague")


# ============================================================
# MODULE 4 — Financial Reality Agent Schemas
# ============================================================

class FinancialEstimates(BaseModel):
    estimated_build_cost_usd: int = Field(..., description="Estimated cost to build MVP in USD")
    estimated_time_to_first_revenue_weeks: int = Field(..., description="Weeks until first dollar of revenue")
    break_even_estimate_months: int = Field(..., description="Months to break even")

class FinancialRealityOutput(BaseModel):
    estimates: FinancialEstimates
    viability_score: int = Field(..., ge=0, le=100)
    recommendation: Literal["go", "no_go", "pivot"]
    reasoning: str = Field(..., description="Explicit reasoning for the recommendation, not vague")
    pivot_suggestion: Optional[str] = Field(None, description="Required if recommendation is pivot")


# ============================================================
# MODULE 5 — Weekly Execution Agent Schemas
# ============================================================

class WeeklyAction(BaseModel):
    action_number: int = Field(..., ge=1, le=5)
    task: str = Field(..., description="Direct task instruction, no motivational language")
    priority: int = Field(..., ge=1, le=5, description="1 = highest priority, 5 = lowest")
    time_estimate_hours: float = Field(..., description="Estimated hours to complete")
    success_criterion: str = Field(..., description="Measurable definition of done")

class WeeklyExecutionOutput(BaseModel):
    week_number: int
    actions: List[WeeklyAction] = Field(..., min_length=5, max_length=5)
    total_estimated_hours: float
    week_focus: str = Field(..., description="One-line summary of the week's primary objective")


# ============================================================
# SUPERVISOR — Output Quality Validation Schema
# ============================================================

class SupervisorValidation(BaseModel):
    passed: bool
    vague_outputs_found: List[str] = Field(default_factory=list, description="List of vague phrases detected")
    missing_fields: List[str] = Field(default_factory=list, description="Required fields that are empty or missing")
    override_reason: Optional[str] = Field(None, description="If failed, reason for rejection")


# ============================================================
# API REQUEST / RESPONSE MODELS
# ============================================================

class FounderInput(BaseModel):
    session_id: Optional[str] = None
    stage: Literal["idea_clarity", "customer_discovery", "validation", "financial_reality", "weekly_execution"]
    idea_description: Optional[str] = None
    problem_statement: Optional[str] = None
    target_customer: Optional[str] = None
    discovery_notes: Optional[str] = None
    time_available_hours_per_week: Optional[int] = None
    capital_available_usd: Optional[int] = None
    runway_months: Optional[int] = None
    current_week_number: Optional[int] = None
    weekly_goals: Optional[str] = None

class FounderResponse(BaseModel):
    session_id: str
    stage: str
    output: dict
    supervisor_validation: SupervisorValidation
    next_stage: Optional[str] = None
    blocked: bool = False
    blocking_message: Optional[str] = None


# ============================================================
# LANGGRAPH STATE — Shared across all 5 agent nodes
# ============================================================

class FounderState(TypedDict, total=False):
    # Session
    session_id: str
    current_stage: str

    # Founder inputs
    idea_description: str
    problem_statement: str
    target_customer: str
    discovery_notes: str
    time_available_hours_per_week: int
    capital_available_usd: int
    runway_months: int
    current_week_number: int
    weekly_goals: str

    # Agent outputs (one per module)
    idea_clarity_output: dict
    customer_discovery_output: dict
    validation_output: dict
    financial_reality_output: dict
    weekly_execution_output: dict

    # Gate control
    gate_passed: bool
    blocked: bool
    blocking_message: str

    # Supervisor
    supervisor_validation: dict

    # Routing
    next_stage: str

    # Error handling
    errors: list
    retry_count: int

    # Final
    final_output: dict
    execution_status: str
