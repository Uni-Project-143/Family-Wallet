from beanie import Document, PydanticObjectId
from pydantic import Field
from datetime import datetime, timezone, timedelta
import uuid

class GiftInvite(Document):
    gift_id: str
    organizer_id: str
    token: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc) + timedelta(days=7))

    class Settings:
        name = "gift_invites"
