from beanie import Document
from pydantic import Field, field_validator
from decimal import Decimal
from datetime import datetime, timezone
from typing import Optional
from enum import Enum
import pymongo
from pymongo import IndexModel
from bson.decimal128 import Decimal128

class RequestStatus(str, Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    DECLINED = "DECLINED"

class MoneyRequest(Document):
    requester_id: str
    recipient_id: str
    group_id: str
    amount: Decimal
    description: Optional[str] = None
    status: RequestStatus = Field(default=RequestStatus.PENDING)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Рятівний валідатор для конвертації MongoDB Decimal128 у Python Decimal
    @field_validator('amount', mode='before')
    @classmethod
    def convert_decimal128(cls, v):
        if isinstance(v, Decimal128):
            return v.to_decimal()
        return v

    class Settings:
        name = "money_requests"
        indexes = [
            IndexModel([("group_id", pymongo.ASCENDING)]),
            IndexModel([("requester_id", pymongo.ASCENDING)]),
            IndexModel([("recipient_id", pymongo.ASCENDING)])
        ]
