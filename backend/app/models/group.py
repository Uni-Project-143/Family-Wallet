from beanie import Document, PydanticObjectId
from pydantic import Field
from datetime import datetime

class Group(Document):
    name: str
    created_by: PydanticObjectId
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "groups"
