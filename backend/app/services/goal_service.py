from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import List


@dataclass
class GoalRecommendation:
    """A single recommended budget adjustment to help meet the goal."""

    action: str
    impact_monthly: Decimal


@dataclass
class GoalPlanResult:
    """Result of goal feasibility and savings plan calculation."""

    months_remaining: int
    target_amount: Decimal
    current_savings: Decimal
    monthly_required: Decimal
    feasible: bool
    recommendations: List[GoalRecommendation]


def plan_goal(
    target_amount: Decimal,
    deadline: date,
    current_savings: Decimal = Decimal("0"),
    monthly_surplus: Decimal = Decimal("0"),
) -> GoalPlanResult:
    """
    Calculate monthly required savings and feasibility for a single goal.

    Inputs:
        target_amount: Goal target amount.
        deadline: Target date to reach the goal.
        current_savings: Optional current savings toward the goal (default 0).
        monthly_surplus: Current monthly surplus (income minus expenses) available for saving.

    Outputs:
        months_remaining, monthly_required, feasible, and recommended budget adjustments.
    """
    today = date.today()
    if deadline <= today:
        months_remaining = 0
        monthly_required = Decimal("0")
    else:
        months_remaining = max(
            0,
            (deadline.year - today.year) * 12 + (deadline.month - today.month),
        )
        if months_remaining == 0:
            months_remaining = 1
        remaining_to_save = target_amount - current_savings
        if remaining_to_save <= 0:
            monthly_required = Decimal("0")
        else:
            monthly_required = (remaining_to_save / months_remaining).quantize(
                Decimal("0.01")
            )

    feasible = monthly_surplus >= monthly_required
    recommendations: List[GoalRecommendation] = []

    if not feasible and monthly_required > 0:
        shortfall = (monthly_required - monthly_surplus).quantize(Decimal("0.01"))
        recommendations.append(
            GoalRecommendation(
                action=f"Increase monthly savings by ${shortfall} (e.g. reduce spending or add income)",
                impact_monthly=shortfall,
            )
        )
        recommendations.append(
            GoalRecommendation(
                action="Or push the deadline back to lower required monthly savings",
                impact_monthly=Decimal("0"),
            )
        )

    return GoalPlanResult(
        months_remaining=months_remaining,
        target_amount=target_amount,
        current_savings=current_savings,
        monthly_required=monthly_required,
        feasible=feasible,
        recommendations=recommendations,
    )


def allocation_plan_by_priority(
    monthly_required_per_goal: List[Decimal],
    monthly_surplus: Decimal,
) -> List[Decimal]:
    """
    Split monthly surplus across multiple goals by priority (order = priority).

    monthly_required_per_goal: List of monthly_required amounts in priority order.
    monthly_surplus: Total monthly surplus to allocate.

    Returns:
        List of allocated amount per goal (same order).
    """
    remaining = monthly_surplus
    result: List[Decimal] = []
    for required in monthly_required_per_goal:
        allocated = min(required, remaining)
        remaining = remaining - allocated
        result.append(allocated)
    return result
