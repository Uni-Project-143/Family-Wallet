from datetime import datetime
from beanie import Document
from pydantic import Field
import pymongo

class BlacklistedToken(Document):
    token: str
    added_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "blacklisted_tokens"
        indexes = [
            pymongo.IndexModel(
                [("added_at", pymongo.ASCENDING)],
                expireAfterSeconds=604800
            )
        ]
