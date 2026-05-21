from pydantic import BaseModel, Field
from decimal import Decimal
class Category(BaseModel):
    name: str
    icon: str

# Схеми для отримання списку карток (Крок 2-5)
class ClientInfoRequest(BaseModel):
    personal_token: str


class CardInfoResponse(BaseModel):
    account_id: str
    masked_pan: str
    type: str  # 'black', 'white', 'platinum' тощо
    balance: Decimal
    currency: int


class ConnectMonobankRequest(BaseModel):
    group_id: str
    personal_token: str
    account_id: str
    masked_pan: str  # Фронт передає нам ці дані з попереднього кроку
    balance: Decimal

class ConnectMonobankResponse(BaseModel):
    id: str
    masked_pan: str
    status: str
    message: str

class StatementItem(BaseModel):
    id: str
    time: int
    description: str
    mcc: int
    amount: int  # Монобанк присилає в копійках!
    operationAmount: int
    currencyCode: int
    balance: int

class WebhookData(BaseModel):
    account: str
    statementItem: StatementItem

class MonobankWebhookRequest(BaseModel):
    type: str
    data: WebhookData
