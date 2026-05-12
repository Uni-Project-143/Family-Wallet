from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from enum import Enum


class TransactionType(str, Enum):
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"


class TransactionFilterParams(BaseModel):
    category_id: Optional[str] = None
    tx_type: Optional[TransactionType] = None
    min_amount: Optional[Decimal] = None
    max_amount: Optional[Decimal] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    sort_by: str = "timestamp"
    sort_order: str = "desc"

    page: int = Field(1, ge=1)
    size: int = Field(20, ge=1, le=100)


class TransactionResponse(BaseModel):
    id: str
    card_id: str
    amount: Decimal
    currency: str
    category_id: str
    description: Optional[str]
    timestamp: datetime
    reactions: List[dict]


class PaginatedTransactionResponse(BaseModel):
    items: List[TransactionResponse]
    total: int
    page: int
    size: int
    pages: int
