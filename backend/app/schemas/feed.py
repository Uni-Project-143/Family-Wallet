from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class FeedTransactionItem(BaseModel):
    id: str
    amount: float
    currency: str
    description: str
    timestamp: datetime
    display_name: str
    avatar: Optional[str] = None
    card_masked_pan: str
    author_id: Optional[str] = None
    category_name: Optional[str] = None
    category_emoji: Optional[str] = None
    category_code: Optional[str] = None
    is_secret_gift: bool = False
    reactions: dict = Field(default_factory=dict)
    my_reaction: Optional[str] = None

class FeedResponse(BaseModel):
    items: List[FeedTransactionItem]
    total: int
    page: int
    limit: int
    has_more: bool
