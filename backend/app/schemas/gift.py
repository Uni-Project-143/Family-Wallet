from pydantic import BaseModel, Field, field_validator
from datetime import datetime, timezone

class CreateGiftRequest(BaseModel):
    name: str = Field(..., min_length=1, description="Name is required")
    goal_amount: float
    target_user_id: str
    group_id: str
    unlock_date: datetime

    @field_validator('unlock_date')
    @classmethod
    def date_must_be_in_future(cls, v):
        if v <= datetime.now(timezone.utc):
            raise ValueError('UnlockDate should be in the future')
        return v

class CreateGiftResponse(BaseModel):
    status: str
    gift_id: str

class JoinGiftRequest(BaseModel):
    invite_link: str
