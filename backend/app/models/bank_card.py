from decimal import Decimal
from typing import List, Any, Optional
from beanie import Document
from pydantic import field_validator, Field
from bson import Decimal128

class BankCard(Document):
    user_id: str
    group_id: str
    encrypted_token: str
    account_id: str
    masked_pan: str
    balance: Decimal = Decimal("0.00")
    virtual_balance: Decimal = Field(default_factory=lambda: Decimal("0.00"))
    status: str = "ACTIVE"
    transaction_ids: List[str] = []
    owner_full_name: Optional[str] = None

    # Додаємо цей валідатор, щоб Pydantic розумів числа з MongoDB
    @field_validator("balance", "virtual_balance", mode="before")
    @classmethod
    def parse_decimal128(cls, value):
        """Конвертує MongoDB Decimal128 у стандартний Python Decimal"""
        if isinstance(value, Decimal128):
            return value.to_decimal()
        return value

    class Settings:
        name = "bank_cards"
