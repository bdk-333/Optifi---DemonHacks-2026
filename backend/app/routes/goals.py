from app.schemas.goal import GoalOut, GoalsResponse
from app.store import get_goals
from fastapi import APIRouter

router = APIRouter(tags=["goals"])


@router.get("/goals", response_model=GoalsResponse)
def get_goals_route(userId: str) -> GoalsResponse:
    """Return goals for the user (from in-memory store; add goals via chat)."""
    goals = get_goals(userId)
    return GoalsResponse(
        goals=[GoalOut(
            id=g["id"],
            type=g["type"],
            targetAmount=g["targetAmount"],
            deadline=g["deadline"],
            priority=g["priority"],
            currentSavings=g.get("currentSavings"),
        ) for g in goals]
    )
