from typing import List, Optional

from pydantic import BaseModel


class GoalOut(BaseModel):
    id: str
    type: str
    targetAmount: float
    deadline: str
    priority: int
    currentSavings: Optional[float] = None


class GoalsResponse(BaseModel):
    goals: List[GoalOut]
