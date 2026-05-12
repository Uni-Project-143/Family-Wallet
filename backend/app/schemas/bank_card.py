from pydantic import BaseModel, Field
from typing import List
from decimal import Decimal

class BankCardResponse(BaseModel):
    id: str
    user_id: str
    group_id: str
    account_id: str
    masked_pan: str
    balance: Decimal
    status: str
    transaction_ids: List[str] = Field(default_factory=list)

    class Config:
        from_attributes = True
