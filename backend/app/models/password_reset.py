from beanie import Document
from pydantic import Field
from datetime import datetime, timedelta, timezone
import uuid

class PasswordResetToken(Document):
    email: str
    token: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    expires_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(hours=1))

    class Settings:
        name = "password_reset_tokens"
