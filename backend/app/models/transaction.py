from beanie import Document
from pydantic import Field
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

class Transaction(Document):
    card_id: str
    amount: Decimal
    currency: str = "UAH"
    category_id: str
    description: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    reactions: List[dict] = []

    class Settings:
        name = "transactions"
