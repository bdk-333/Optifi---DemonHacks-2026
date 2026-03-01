from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Any, Dict, Tuple

from app.agents.goal_agent import format_goal_response
from app.schemas.chat import StructuredResponse
from app.services.goal_service import plan_goal
from app.services.llm_service import classify_intent

# Keyword routing: intent -> set of lowercase keywords (any match assigns that intent).
# Order of checks: budget, goal, loan (first match wins).
INTENT_KEYWORDS: Dict[str, Tuple[str, ...]] = {
    "budget": ("budget", "spent", "overspend", "limit", "spending", "category"),
    "goal": ("goal", "save", "savings", "deadline", "target", "reach", "amount"),
    "loan": ("loan", "interest", "tenure", "payoff", "emi", "principal", "debt"),
}

# Intents we support with keyword routing; LLM can return any of these or "general".
KEYWORD_INTENTS = frozenset(INTENT_KEYWORDS.keys())

# If no keyword matches, use LLM; if LLM confidence is below this, treat as general.
LLM_CONFIDENCE = 0.7


@dataclass
class RoutingResult:
    intent: str
    confidence: float


def route_intent(message: str) -> RoutingResult:
    """
    Route user message to an intent using keyword matching first, then LLM fallback.
    """
    text = (message or "").strip().lower()
    if not text:
        return RoutingResult(intent="general", confidence=0.0)

    # Keyword routing: first matching intent wins.
    for intent, keywords in INTENT_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            return RoutingResult(intent=intent, confidence=1.0)

    # Fallback: LLM classifier.
    label = classify_intent(message)
    return RoutingResult(intent=label, confidence=LLM_CONFIDENCE)

# dummy route_intent function
def route_intent_dummy(message: str) -> str:
    """
    Route user message to an intent using keyword matching first, then LLM fallback.
    """
    text = (message or "").strip().lower()
    if not text:
        return "No intent found, as I'm not using LLM for intent classification"

    # Keyword routing: first matching intent wins.
    for intent, keywords in INTENT_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            # return RoutingResult(intent=intent, confidence=1.0)
            return intent

    return "No intent found, as I'm not using LLM for intent classification"


def run_intent(
    intent: str,
    context: Dict[str, Any],
    message: str,
) -> StructuredResponse:
    """
    Run the appropriate agent for the intent and return a structured response.
    """
    if intent == "goal":
        return _run_goal(context, message)
    if intent == "budget":
        return _run_budget_placeholder(context, message)
    if intent == "loan":
        return _run_loan_placeholder(context, message)
    return _run_general_placeholder(message)


def _run_goal(context: Dict[str, Any], message: str) -> StructuredResponse:
    """Run goal agent using GoalService and format via GoalAgent."""
    target_amount = context.get("target_amount")
    deadline = context.get("deadline")
    current_savings = context.get("current_savings") or Decimal("0")
    monthly_surplus = context.get("monthly_surplus") or Decimal("0")

    if target_amount is None or deadline is None:
        return StructuredResponse(
            summary="I can help you plan for a goal.",
            analysis="To run the numbers I need: target amount and deadline. You can also share current savings and monthly surplus for a feasibility check.",
            action_plan=[
                "Add a goal with a target amount and deadline in the app.",
                "Tell me the target amount and deadline (e.g. $12,000 by August 2026).",
            ],
            calculations=[],
            next_questions=[
                "What's your target amount and deadline?",
                "Do you already have savings set aside for this goal?",
            ],
            disclaimer="This is not financial advice.",
        )

    if not isinstance(target_amount, Decimal):
        target_amount = Decimal(str(target_amount))
    if current_savings is None or not isinstance(current_savings, Decimal):
        current_savings = Decimal(str(current_savings or 0))
    if monthly_surplus is None or not isinstance(monthly_surplus, Decimal):
        monthly_surplus = Decimal(str(monthly_surplus or 0))
    if isinstance(deadline, str):
        deadline = date.fromisoformat(deadline)

    plan = plan_goal(
        target_amount=target_amount,
        deadline=deadline,
        current_savings=current_savings,
        monthly_surplus=monthly_surplus,
    )
    return format_goal_response(plan)


def _run_budget_placeholder(context: Dict[str, Any], message: str) -> StructuredResponse:
    return StructuredResponse(
        summary="Budget support is not implemented yet.",
        analysis="The Budget Agent will use your budgets and transactions to show spending vs limits and alerts.",
        action_plan=[],
        calculations=[],
        next_questions=["Ask about goals or loans in the meantime."],
        disclaimer="",
    )


def _run_loan_placeholder(context: Dict[str, Any], message: str) -> StructuredResponse:
    return StructuredResponse(
        summary="Loan support is not implemented yet.",
        analysis="The Loan Agent will compute payoff strategies and interest saved.",
        action_plan=[],
        calculations=[],
        next_questions=["Ask about goals or budgets in the meantime."],
        disclaimer="",
    )


def _run_general_placeholder(message: str) -> StructuredResponse:
    return StructuredResponse(
        summary="I'm your financial assistant.",
        analysis="You can ask about goals (savings, targets, deadlines), budgets (spending, limits), or loans (payoff, interest).",
        action_plan=["Try: 'How much do I need to save monthly for a $12k goal by next year?'"],
        calculations=[],
        next_questions=[
            "Do you have a savings goal in mind?",
            "Want to set up or review a budget?",
        ],
        disclaimer="This is not financial advice.",
    )


def format_response(
    tool_output: StructuredResponse,
    message: str,
    context: Dict[str, Any],
) -> StructuredResponse:
    """
    Ensure the reply is in the standard response format.
    If tool_output is already StructuredResponse, return it; otherwise wrap.
    """
    if isinstance(tool_output, StructuredResponse):
        return tool_output
    return StructuredResponse(
        summary=str(tool_output)[:500],
        analysis="",
        action_plan=[],
        calculations=[],
        next_questions=[],
        disclaimer="",
    )


if __name__ == "__main__":
    print(route_intent_dummy("I want to save $1000 by next month"))