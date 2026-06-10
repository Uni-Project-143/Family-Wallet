from pydantic import BaseModel, Field
from decimal import Decimal
from typing import Optional
from app.models.money_request import RequestStatus

class CreateMoneyRequestDto(BaseModel):
    recipient_id: str
    amount: Decimal = Field(gt=0, description="Сума має бути більшою за 0")
    description: Optional[str] = None

class UpdateMoneyRequestDto(BaseModel):
    status: RequestStatus
