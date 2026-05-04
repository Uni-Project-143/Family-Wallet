from decimal import Decimal
from typing import List
from beanie import Document

class BankCard(Document):
    user_id: str
    group_id: str
    encrypted_token: str
    account_id: str
    masked_pan: str
    balance: Decimal = Decimal("0.00")
    status: str = "ACTIVE"
    transaction_ids: List[str] = []

    class Settings:
        name = "bank_cards"
