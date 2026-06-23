from beanie import Document, PydanticObjectId
from pydantic import Field
from datetime import datetime, timezone
import pymongo

class GroupMembership(Document):
    user_id: PydanticObjectId
    group_id: PydanticObjectId
    role: str = Field(..., description="Роль користувача: ADMIN або MEMBER")
    joined_at: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "group_memberships"
        indexes = [
            pymongo.IndexModel([("user_id", pymongo.ASCENDING), ("group_id", pymongo.ASCENDING)], unique=True),
            pymongo.IndexModel([("group_id", pymongo.ASCENDING)])
        ]
