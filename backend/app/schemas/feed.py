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
    avatar: Optional[str] = None  # Використовуємо Optional для узгодженості
    card_masked_pan: str

    # --- ДОДАНО НА ВИМОГУ ФРОНТЕНДУ ---
    author_id: Optional[str] = None  # Для фільтрації по автору (filter chips)
    category_name: Optional[str] = None  # Для відображення назви категорії
    category_emoji: Optional[str] = None  # Для іконки категорії
    category_code: Optional[str] = None  # slug категорії (groceries/fast_food/...) для мапінгу на фронті
    is_secret_gift: bool = False  # Для приховування подарунків
    # Реакції: згруповані лічильники {"👍": 2, "❤️": 1} + емодзі поточного юзера (або None).
    reactions: dict = Field(default_factory=dict)
    my_reaction: Optional[str] = None


class FeedResponse(BaseModel):
    items: List[FeedTransactionItem]
    total: int
    page: int
    limit: int
    has_more: bool
