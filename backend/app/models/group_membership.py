from beanie import Document, PydanticObjectId
from pydantic import Field
from datetime import datetime

class GroupMembership(Document):
    user_id: PydanticObjectId
    group_id: PydanticObjectId
    role: str = Field(..., description="Роль користувача: ADMIN або MEMBER")
    joined_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "group_memberships"
