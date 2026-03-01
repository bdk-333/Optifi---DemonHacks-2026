import uuid
from datetime import date, datetime
from decimal import Decimal
from sqlmodel import Field, SQLModel


class Goal(SQLModel, table=True):
    __tablename__ = "goals"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    type: str = Field(index=True)
    target_amount: Decimal = Field(max_digits=18, decimal_places=2)
    deadline: date = Field(index=True)
    priority: int = Field(default=1, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
