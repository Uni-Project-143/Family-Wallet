from decimal import Decimal
from typing import List, Optional
from beanie import Document
from pydantic import field_validator, Field
from bson import Decimal128
import pymongo

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

    @field_validator("balance", "virtual_balance", mode="before")
    @classmethod
    def parse_decimal128(cls, value):
        if isinstance(value, Decimal128):
            return value.to_decimal()
        return value

    class Settings:
        name = "bank_cards"
        indexes = [
            pymongo.IndexModel([("account_id", pymongo.ASCENDING)], unique=True, sparse=True),
            pymongo.IndexModel([("group_id", pymongo.ASCENDING)]),
            pymongo.IndexModel([("user_id", pymongo.ASCENDING)])
        ]
