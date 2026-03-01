"""
In-memory store for goals (demo only). Replace with DB later.
"""
import uuid
from typing import Any, Dict, List

# userId -> list of goal dicts (GoalOut shape: id, type, targetAmount, deadline, priority, currentSavings)
_user_goals: Dict[str, List[Dict[str, Any]]] = {}


def get_goals(user_id: str) -> List[Dict[str, Any]]:
    return _user_goals.get(user_id, [])


def add_goal(
    user_id: str,
    *,
    target_amount: float,
    deadline: str,
    goal_type: str = "savings",
    priority: int = 1,
    current_savings: float = 0,
) -> Dict[str, Any]:
    goal = {
        "id": str(uuid.uuid4()),
        "type": goal_type,
        "targetAmount": float(target_amount),
        "deadline": deadline,
        "priority": priority,
        "currentSavings": current_savings,
    }
    if user_id not in _user_goals:
        _user_goals[user_id] = []
    _user_goals[user_id].append(goal)
    return goal


def update_goal_savings(user_id: str, goal_id: str, current_savings: float) -> None:
    for g in _user_goals.get(user_id, []):
        if g["id"] == goal_id:
            g["currentSavings"] = current_savings
            break
