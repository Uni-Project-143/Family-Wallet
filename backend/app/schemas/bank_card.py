from pydantic import BaseModel, Field
from typing import List, Optional
from decimal import Decimal

class BankCardResponse(BaseModel):
    id: str
    user_id: str
    group_id: str
    account_id: str
    masked_pan: str
    balance: Decimal
    effective_balance: Decimal
    # Кешований баланс із урахуванням віртуальних переказів — фронт показує саме його.
    # Optional як захист: якщо в БД ще None (картка до ініціалізації) — не падаємо 500,
    # фронт у цьому разі відкочується на effective_balance.
    virtual_balance: Optional[Decimal] = None
    status: str
    transaction_ids: List[str] = Field(default_factory=list)
    owner_full_name: Optional[str] = None

    class Config:
        from_attributes = True
