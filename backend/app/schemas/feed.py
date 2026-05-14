from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class FeedTransactionItem(BaseModel):
    id: str
    amount: float
    currency: str
    description: str
    timestamp: datetime
    display_name: str
    avatar: Optional[str] = None  # Використовуємо Optional для узгодженості
    card_masked_pan: str

    # --- ДОДАНО НА ВИМОГУ ФРОНТЕНДУ ---
    author_id: Optional[str] = None  # Для фільтрації по автору (filter chips)
    category_name: Optional[str] = None  # Для відображення назви категорії
    category_emoji: Optional[str] = None  # Для іконки категорії
    is_secret_gift: bool = False  # Для приховування подарунків


class FeedResponse(BaseModel):
    items: List[FeedTransactionItem]
    total: int
    page: int
    limit: int
    has_more: bool
