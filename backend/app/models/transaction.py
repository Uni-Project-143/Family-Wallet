from beanie import Document
from pydantic import Field, field_validator
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from bson.decimal128 import Decimal128

class Transaction(Document):
    card_id: str
    amount: Decimal
    currency: str = "UAH"
    category_id: str
    description: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    reactions: List[dict] = []

    # Рятівний валідатор для MongoDB Decimal128
    @field_validator('amount', mode='before')
    @classmethod
    def convert_decimal128(cls, v):
        if isinstance(v, Decimal128):
            return v.to_decimal()
        return v

    class Settings:
        name = "transactions"
