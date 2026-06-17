from beanie import Document, PydanticObjectId
from pydantic import Field
from datetime import datetime, timedelta
import uuid
from pymongo import IndexModel, ASCENDING

def get_expiration_date():
    return datetime.utcnow() + timedelta(hours=48)

class InviteToken(Document):
    group_id: PydanticObjectId
    token: str = Field(default_factory=lambda: uuid.uuid4().hex)
    created_by: PydanticObjectId
    expires_at: datetime = Field(default_factory=get_expiration_date)
    used_at: datetime | None = None

    class Settings:
        name = "invite_tokens"
        indexes = [
            IndexModel([("expires_at", ASCENDING)], expireAfterSeconds=0)
        ]
