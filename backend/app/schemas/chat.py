from typing import List

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    userId: str
    message: str


class CalculationItem(BaseModel):
    """Single calculation row for the response."""

    label: str
    value: str


class StructuredResponse(BaseModel):
    """Contract for all agent responses (Summary, Analysis, Action Plan, Calculations)."""

    summary: str = Field(description="Brief summary of the response")
    analysis: str = Field(default="", description="Deeper analysis or context")
    action_plan: List[str] = Field(default_factory=list, description="Recommended actions")
    calculations: List[CalculationItem] = Field(
        default_factory=list, description="Key numbers (label, value)"
    )
    next_questions: List[str] = Field(
        default_factory=list, description="Suggested follow-up questions"
    )
    disclaimer: str = Field(default="", description="Legal or safety disclaimer")
