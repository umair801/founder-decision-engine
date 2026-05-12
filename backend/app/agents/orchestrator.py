import logging
from langgraph.graph import StateGraph, END
from app.schemas.models import FounderState
from app.agents.idea_clarity_agent import idea_clarity_agent
from app.agents.customer_discovery_agent import customer_discovery_agent
from app.agents.validation_agent import validation_agent
from app.agents.financial_reality_agent import financial_reality_agent
from app.agents.weekly_execution_agent import weekly_execution_agent
from app.agents.supervisor_agent import run_supervisor_validation

logger = logging.getLogger(__name__)


# ── Supervisor wrapper nodes ─────────────────────────────────────────────────
# Each agent node is followed by a supervisor node that validates its output.
# If supervisor fails, execution_status is set to "supervisor_failed" and
# the graph routes to END with the failure details in final_output.

def _wrap_with_supervisor(agent_fn, stage: str):
    """
    Returns a LangGraph node function that:
    1. Runs the agent
    2. Runs supervisor validation on its output
    3. Writes result into state
    """
    def node(state: FounderState) -> FounderState:
        # Run the agent
        state = agent_fn(state)

        # Get the output for this stage
        output_key = f"{stage}_output"
        agent_output = state.get(output_key, {})

        # Run supervisor validation
        validation = run_supervisor_validation(stage, agent_output)
        state["supervisor_validation"] = validation.model_dump()

        if not validation.passed:
            logger.warning(f"Supervisor failed for stage '{stage}': {validation.override_reason}")
            state["execution_status"] = "supervisor_failed"
            state["final_output"] = {
                "stage": stage,
                "error": "Output quality validation failed.",
                "supervisor": validation.model_dump(),
                "agent_output": agent_output
            }
        else:
            logger.info(f"Supervisor passed for stage '{stage}'.")

        return state

    node.__name__ = f"{stage}_node"
    return node


# ── Gate check node ──────────────────────────────────────────────────────────

def gate_check_node(state: FounderState) -> FounderState:
    """
    Enforces the customer discovery hard gate.
    If gate not passed, sets blocked = True and writes final_output.
    """
    if not state.get("gate_passed", False):
        cd_output = state.get("customer_discovery_output", {})
        state["blocked"] = True
        state["execution_status"] = "blocked"
        state["final_output"] = {
            "stage": "customer_discovery",
            "blocked": True,
            "blocking_message": state.get(
                "blocking_message",
                "Customer discovery score below 60. Complete required actions before proceeding."
            ),
            "required_actions": cd_output.get("required_actions", []),
            "readiness_score": cd_output.get("readiness_score", 0),
            "discovery_questions": cd_output.get("discovery_questions", [])
        }
        logger.warning("Hard gate: customer discovery blocked. Progression halted.")
    return state


# ── Routing functions ────────────────────────────────────────────────────────

def route_by_stage(state: FounderState) -> str:
    """
    Entry router: directs founder input to the correct agent node
    based on the current_stage field.
    """
    stage = state.get("current_stage", "idea_clarity")
    valid_stages = [
        "idea_clarity",
        "customer_discovery",
        "validation",
        "financial_reality",
        "weekly_execution"
    ]
    if stage not in valid_stages:
        logger.warning(f"Unknown stage '{stage}', defaulting to idea_clarity.")
        return "idea_clarity"
    return stage


def route_after_supervisor(state: FounderState) -> str:
    """
    After every agent + supervisor pair:
    - If supervisor failed: END
    - If blocked by gate: END
    - Otherwise: END (each stage is a single-turn operation)
    """
    if state.get("execution_status") in ("supervisor_failed", "blocked"):
        return END
    return END


def route_after_gate(state: FounderState) -> str:
    """
    After customer discovery gate check:
    - If blocked: END
    - If passed: END (validation is a separate stage, triggered by next founder input)
    """
    if state.get("blocked", False):
        return END
    return END


# ── Build the LangGraph graph ────────────────────────────────────────────────

def build_founder_graph() -> StateGraph:
    graph = StateGraph(FounderState)

    # Add agent nodes (each wrapped with supervisor)
    graph.add_node(
        "idea_clarity",
        _wrap_with_supervisor(idea_clarity_agent, "idea_clarity")
    )
    graph.add_node(
        "customer_discovery",
        _wrap_with_supervisor(customer_discovery_agent, "customer_discovery")
    )
    graph.add_node(
        "gate_check",
        gate_check_node
    )
    graph.add_node(
        "validation",
        _wrap_with_supervisor(validation_agent, "validation")
    )
    graph.add_node(
        "financial_reality",
        _wrap_with_supervisor(financial_reality_agent, "financial_reality")
    )
    graph.add_node(
        "weekly_execution",
        _wrap_with_supervisor(weekly_execution_agent, "weekly_execution")
    )

    # Entry point: route by stage
    graph.set_conditional_entry_point(
        route_by_stage,
        {
            "idea_clarity": "idea_clarity",
            "customer_discovery": "customer_discovery",
            "validation": "validation",
            "financial_reality": "financial_reality",
            "weekly_execution": "weekly_execution",
        }
    )

    # After customer discovery: always run gate check
    graph.add_edge("customer_discovery", "gate_check")

    # After gate check: route based on gate result
    graph.add_conditional_edges(
        "gate_check",
        route_after_gate,
        {END: END}
    )

    # All other stages: go to END after supervisor
    graph.add_conditional_edges(
        "idea_clarity",
        route_after_supervisor,
        {END: END}
    )
    graph.add_conditional_edges(
        "validation",
        route_after_supervisor,
        {END: END}
    )
    graph.add_conditional_edges(
        "financial_reality",
        route_after_supervisor,
        {END: END}
    )
    graph.add_conditional_edges(
        "weekly_execution",
        route_after_supervisor,
        {END: END}
    )

    return graph.compile()


# ── Compiled graph singleton ─────────────────────────────────────────────────
founder_graph = build_founder_graph()
