from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


# Перелічення для зручності Swagger'а
class TransactionType(str, Enum):
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"


class SortField(str, Enum):
    TIME = "time"
    AMOUNT = "amount"
    CATEGORY = "category"


class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"


# Клас параметрів, які ми будемо чекати в URL
class TransactionFilterParams(BaseModel):
    category: Optional[str] = Field(None, description="Фільтр по категорії")
    tx_type: Optional[TransactionType] = Field(None, description="INCOME або EXPENSE")
    min_amount: Optional[float] = Field(None, description="Мінімальна сума")
    max_amount: Optional[float] = Field(None, description="Максимальна сума")
    start_date: Optional[datetime] = Field(None, description="Початкова дата (ISO 8601)")
    end_date: Optional[datetime] = Field(None, description="Кінцева дата (ISO 8601)")

    sort_by: SortField = Field(SortField.TIME, description="Поле для сортування")
    sort_order: SortOrder = Field(SortOrder.DESC, description="Напрямок сортування")

    page: int = Field(1, ge=1, description="Номер сторінки")
    size: int = Field(20, ge=1, le=100, description="Кількість записів на сторінку")


# Схема для відповіді фронтенду
class TransactionPaginatedResponse(BaseModel):
    items: List[dict]  # Тут потім заміниш dict на схему TransactionResponse
    total: int
    page: int
    size: int
    pages: int
