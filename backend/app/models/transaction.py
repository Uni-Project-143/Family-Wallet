from beanie import Document
from pydantic import Field, field_validator, BaseModel
from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional
from bson.decimal128 import Decimal128
from pymongo import IndexModel, ASCENDING
import pymongo


# ---> КРОК 1: Переносимо модель Reaction сюди, ДО класу Transaction <---
class Reaction(BaseModel):
    user_id: str
    emoji: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Transaction(Document):
    card_id: str
    amount: Decimal
    currency: str = "UAH"
    category_id: Optional[str] = None
    description: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # ---> КРОК 1: Змінюємо List[dict] на List[Reaction] <---
    reactions: List[Reaction] = Field(default_factory=list)

    group_id: str = Field(..., description="ID групи для швидкої фільтрації стрічки")
    is_secret_gift: bool = Field(default=False, description="Чи є це секретним подарунком")
    target_user_id: Optional[str] = Field(default=None,
                                          description="ID того, кому призначений подарунок")
    gift_id: Optional[str] = Field(default=None,
                                   description="ID конкретної події Secret Gift")
    mono_id: Optional[str] = None
    mcc: Optional[int] = None
    is_virtual: bool = Field(default=False, description="Внутрішня фейкова транзакція")
    transfer_id: Optional[str] = Field(
        default=None,
        description="ID парної транзакції для переказу між картками сім'ї",
    )

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
            IndexModel([("group_id", pymongo.ASCENDING), ("timestamp", pymongo.DESCENDING)]),

            # ---> ВИПРАВЛЕНИЙ ІНДЕКС <---
            IndexModel(
                [("mono_id", pymongo.ASCENDING)],
                unique=True,
                partialFilterExpression={"mono_id": {"$type": "string"}}
            ),

            IndexModel([("card_id", pymongo.ASCENDING), ("is_virtual", pymongo.ASCENDING)]),
            IndexModel([("transfer_id", pymongo.ASCENDING)], sparse=True)
        ]
