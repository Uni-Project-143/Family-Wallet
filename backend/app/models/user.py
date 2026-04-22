from beanie import Document
from pydantic import EmailStr, Field
from datetime import datetime

class User(Document):
    full_name: str
    email: EmailStr = Field(unique=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "users"
