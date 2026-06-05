from pydantic import BaseModel, Field, model_validator
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Literal

AllowedEmoji = Literal["👍", "❤️", "😂", "🔥", "😮"]

class ReactionRequest(BaseModel):
    emoji: AllowedEmoji = Field(..., description="Емодзі-реакція")


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
    category_id: Optional[str] = None
    description: Optional[str] = None
    timestamp: datetime
    reactions: List[dict] = []
    is_virtual: bool = False
    transfer_id: Optional[str] = None


class TransactionPaginatedResponse(BaseModel):
    items: List[TransactionResponse]
    total: int
    page: int
    size: int
    pages: int


class TransferRequest(BaseModel):
    from_card_id: str
    to_card_id: str
    amount: Decimal = Field(..., gt=0, decimal_places=2, max_digits=14)
    description: Optional[str] = Field(None, max_length=500)
    category_id: Optional[str] = None

    @model_validator(mode="after")
    def reject_same_card(self) -> "TransferRequest":
        if self.from_card_id == self.to_card_id:
            raise ValueError("from_card_id must differ from to_card_id")
        return self


class TransferResponse(BaseModel):
    transfer_id: str
    debit_transaction_id: str
    credit_transaction_id: str
    amount: Decimal
    from_effective_balance: Decimal
    to_effective_balance: Decimal
