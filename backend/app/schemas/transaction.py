from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal
from enum import Enum


class TransactionType(str, Enum):
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"


class SortByField(str, Enum):
    AMOUNT = "amount"
    TIMESTAMP = "timestamp"
    CATEGORY = "category_id"


class SortOrderType(str, Enum):
    ASC = "asc"
    DESC = "desc"


class TransactionFilterParams(BaseModel):
    category_id: Optional[str] = Field(None, description="ID категорії ('None' якщо без категорії)")
    tx_type: Optional[TransactionType] = Field(None, description="Тип транзакції")
    min_amount: Optional[float] = Field(None,
                                        description="Мінімальна сума (по модулю, наприклад 100)")
    max_amount: Optional[float] = Field(None,
                                        description="Максимальна сума (по модулю, наприклад 5000)")

    start_date: Optional[date] = Field(None, description="Від",
                                       json_schema_extra={"format": "date"})
    end_date: Optional[date] = Field(None, description="До", json_schema_extra={"format": "date"})

    sort_by: SortByField = Field(SortByField.TIMESTAMP)
    sort_order: SortOrderType = Field(SortOrderType.DESC)

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


class TransactionPaginatedResponse(BaseModel):
    items: List[TransactionResponse]
    total: int
    page: int
    size: int
    pages: int
