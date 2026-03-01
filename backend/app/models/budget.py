import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlmodel import Field, SQLModel


class Budget(SQLModel, table=True):
    __tablename__ = "budgets"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    category: str = Field(index=True)
    monthly_limit: Decimal = Field(max_digits=18, decimal_places=2)
    created_at: datetime = Field(default_factory=datetime.utcnow)
