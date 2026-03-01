import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlmodel import Field, SQLModel


class Transaction(SQLModel, table=True):
    __tablename__ = "transactions"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    date: date = Field(index=True)
    merchant: str = Field(index=True)
    category: str = Field(index=True)
    amount: Decimal = Field(max_digits=18, decimal_places=2)
    raw_description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
