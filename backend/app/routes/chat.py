from datetime import date

from app.agents.orchestrator import route_intent, run_intent
from app.schemas.chat import ChatRequest, StructuredResponse
from app.store import add_goal, get_goals
from app.utils.goal_parser import parse_goal_from_message
from fastapi import APIRouter

router = APIRouter(prefix="/chat", tags=["chat"])


def _build_context(user_id: str, message: str):
    """Build context for the orchestrator from stored goals and parsed message."""
    context = {}
    parsed = parse_goal_from_message(message)

    if parsed.get("target_amount") is not None and parsed.get("deadline") is not None:
        context["target_amount"] = parsed["target_amount"]
        context["deadline"] = parsed["deadline"]
        context["current_savings"] = parsed.get("current_savings")
        context["monthly_surplus"] = parsed.get("monthly_surplus")
        deadline_val = parsed["deadline"]
        if isinstance(deadline_val, date):
            deadline_str = deadline_val.isoformat()
        else:
            deadline_str = str(deadline_val)
        # Save goal so it shows in sidebar (skip if same as most recent)
        existing = get_goals(user_id)
        same = (
            existing
            and existing[-1]["targetAmount"] == float(parsed["target_amount"])
            and existing[-1]["deadline"] == deadline_str
        )
        if not same:
            add_goal(
                user_id,
                target_amount=float(parsed["target_amount"]),
                deadline=deadline_str,
                current_savings=float(parsed.get("current_savings") or 0),
            )
        return context

    # No parse from this message: use latest stored goal for context so "how am I doing?" works
    goals = get_goals(user_id)
    if goals:
        latest = goals[-1]
        context["target_amount"] = latest["targetAmount"]
        context["deadline"] = latest["deadline"]
        context["current_savings"] = latest.get("currentSavings") or 0
        # monthly_surplus not stored; leave unset so user can say it in a follow-up

    return context


@router.post("", response_model=StructuredResponse)
def post_chat(body: ChatRequest) -> StructuredResponse:
    """Handle a chat message: route intent, build context, run agent, return response."""
    result = route_intent(body.message)
    context = _build_context(body.userId, body.message)
    parsed = parse_goal_from_message(body.message)
    # If message clearly has a goal (amount + deadline), always run goal agent
    if parsed.get("target_amount") is not None and parsed.get("deadline") is not None:
        intent = "goal"
    else:
        intent = result.intent
        if intent != "goal":
            context = {}
    response = run_intent(intent, context, body.message)
    return response
