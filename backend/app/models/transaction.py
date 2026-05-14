from beanie import Document
from pydantic import Field, field_validator
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from bson.decimal128 import Decimal128
import pymongo

class Transaction(Document):
    card_id: str
    amount: Decimal
    currency: str = "UAH"
    category_id: str
    description: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    reactions: List[dict] = []
    group_id: str = Field(..., description="ID групи для швидкої фільтрації стрічки")
    is_secret_gift: bool = Field(default=False, description="Чи є це секретним подарунком")
    target_user_id: Optional[str] = Field(default=None,
                                          description="ID того, кому призначений подарунок")

    # ----------------

    # Рятівний валідатор для MongoDB Decimal128
    @field_validator('amount', mode='before')
    @classmethod
    def convert_decimal128(cls, v):
        if isinstance(v, Decimal128):
            return v.to_decimal()
        return v

    class Settings:
        name = "transactions"
        indexes = [
            [
                ("group_id", pymongo.ASCENDING),
                ("timestamp", pymongo.DESCENDING)
            ]
        ]
