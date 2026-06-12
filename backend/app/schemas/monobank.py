from pydantic import BaseModel
from decimal import Decimal

class Category(BaseModel):
    name: str
    icon: str

class ClientInfoRequest(BaseModel):
    personal_token: str

class CardInfoResponse(BaseModel):
    account_id: str
    masked_pan: str
    type: str
    balance: Decimal
    currency: int

class ConnectMonobankRequest(BaseModel):
    group_id: str
    personal_token: str
    account_id: str
    masked_pan: str
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
    amount: int
    operationAmount: int
    currencyCode: int
    balance: int

class WebhookData(BaseModel):
    account: str
    statementItem: StatementItem

class MonobankWebhookRequest(BaseModel):
    type: str
    data: WebhookData
