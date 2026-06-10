from beanie import Document
from pydantic import Field
from datetime import datetime, timezone
from pymongo import IndexModel, ASCENDING

class NotificationLog(Document):
    user_id: str
    gift_id: str
    notification_type: str  # 'REVEAL', 'REMINDER_24H', 'REMINDER_9AM'
    idempotency_key: str = Field(..., description="Унікальний ключ для захисту від дублів")
    is_read: bool = Field(default=False, description="Чи прочитане сповіщення")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "notifications"
        # Унікальний індекс на рівні БД (ON CONFLICT DO NOTHING)
        indexes = [
            IndexModel([("idempotency_key", ASCENDING)], unique=True)
        ]
