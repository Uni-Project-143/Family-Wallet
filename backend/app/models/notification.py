from beanie import Document
from pydantic import Field
from datetime import datetime, timezone
from pymongo import IndexModel, ASCENDING

class NotificationLog(Document):
    user_id: str
    gift_id: str
    notification_type: str
    idempotency_key: str = Field(..., description="Унікальний ключ для захисту від дублів")
    is_read: bool = Field(default=False, description="Чи прочитане сповіщення")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "notifications"
        indexes = [
            IndexModel([("idempotency_key", ASCENDING)], unique=True),
            IndexModel([("user_id", ASCENDING), ("created_at", ASCENDING)])
        ]
