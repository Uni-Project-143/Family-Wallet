from pydantic import BaseModel
from typing import List
from datetime import datetime

class FeedTransactionItem(BaseModel):
    id: str
    amount: float
    currency: str
    description: str
    timestamp: datetime
    display_name: str  # Ім'я власника картки
    avatar: str | None # Аватар власника
    card_masked_pan: str

class FeedResponse(BaseModel):
    items: List[FeedTransactionItem]
    total: int
    page: int
    limit: int
    has_more: bool
