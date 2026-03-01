from decimal import Decimal

from app.schemas.chat import CalculationItem, StructuredResponse
from app.services.goal_service import GoalPlanResult
from app.services.llm_service import review_goal_plan


def _templated_summary_analysis(plan: GoalPlanResult) -> tuple[str, str, list[str]]:
    """Fallback when LLM review is not used or fails."""
    if plan.feasible:
        summary = (
            f"Your goal is on track. You need to save ${plan.monthly_required:,.2f} per month "
            f"for the next {plan.months_remaining} months."
        )
        analysis = (
            f"With your current surplus, you can meet the required ${plan.monthly_required:,.2f}/month. "
            f"Target ${plan.target_amount:,.2f} by the deadline with {plan.months_remaining} months left."
        )
    else:
        summary = (
            f"You need to save ${plan.monthly_required:,.2f} per month for {plan.months_remaining} months, "
            "but your current surplus may not be enough. See recommendations below."
        )
        analysis = (
            f"Required monthly savings is ${plan.monthly_required:,.2f}; "
            "adjust spending or income to close the gap, or consider moving the deadline."
        )
    next_questions = [
        "Do you want to add or adjust a budget to free up more savings?",
        "Should we look at your other goals and prioritize?",
    ]
    return summary, analysis, next_questions


def format_goal_response(plan: GoalPlanResult) -> StructuredResponse:
    """
    Format GoalService output into the standard response format.
    Numbers and action_plan always come from our code. Summary/analysis/next_questions
    use an LLM review when available for a more intelligent, personalized reply.
    """
    calculations = [
        CalculationItem(label="Months remaining", value=str(plan.months_remaining)),
        CalculationItem(label="Target amount", value=f"${plan.target_amount:,.2f}"),
        CalculationItem(label="Current savings", value=f"${plan.current_savings:,.2f}"),
        CalculationItem(label="Monthly required", value=f"${plan.monthly_required:,.2f}"),
        CalculationItem(label="Feasible", value="Yes" if plan.feasible else "No"),
    ]
    action_plan = [rec.action for rec in plan.recommendations]
    rec_summary = " ".join(rec.action for rec in plan.recommendations[:3]) if plan.recommendations else "None"

    # Optional LLM review: same numbers, smarter wording and next steps
    review = review_goal_plan(
        months_remaining=plan.months_remaining,
        target_amount=f"${plan.target_amount:,.2f}",
        current_savings=f"${plan.current_savings:,.2f}",
        monthly_required=f"${plan.monthly_required:,.2f}",
        feasible=plan.feasible,
        recommendation_summary=rec_summary,
    )
    if review and (review.get("summary") or review.get("analysis")):
        summary = (review.get("summary") or "").strip() or None
        analysis = (review.get("analysis") or "").strip() or None
        nq = review.get("next_questions")
        next_questions = [str(q).strip() for q in nq] if isinstance(nq, list) else []
        if summary is None or analysis is None:
            summary, analysis, next_questions = _templated_summary_analysis(plan)
        elif not next_questions:
            _, _, next_questions = _templated_summary_analysis(plan)
    else:
        summary, analysis, next_questions = _templated_summary_analysis(plan)

    return StructuredResponse(
        summary=summary,
        analysis=analysis,
        action_plan=action_plan,
        calculations=calculations,
        next_questions=next_questions,
        disclaimer="This is not financial advice. Verify numbers and consult a professional for major decisions.",
    )
