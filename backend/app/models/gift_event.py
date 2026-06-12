from beanie import Document
from pydantic import Field
from datetime import datetime, timezone
from enum import Enum
import pymongo

class GiftStatus(str, Enum):
    ACTIVE = "ACTIVE"
    REVEALED = "REVEALED"
    CANCELLED = "CANCELLED"

class GiftEvent(Document):
    name: str
    organizer_id: str
    target_user_id: str
    group_id: str
    goal_amount: float
    unlock_date: datetime
    status: GiftStatus = GiftStatus.ACTIVE
    secret_mode: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "gift_events"
        indexes = [
            pymongo.IndexModel([("group_id", pymongo.ASCENDING)]),
            pymongo.IndexModel([("target_user_id", pymongo.ASCENDING), ("status", pymongo.ASCENDING)])
        ]
