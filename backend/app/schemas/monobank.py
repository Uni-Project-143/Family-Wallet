from pydantic import BaseModel, Field

class ConnectMonobankRequest(BaseModel):
    group_id: str = Field(..., description="ID of the group to which the card is connected")
    personal_token: str = Field(..., description="Personal Token from Monobank API")

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
