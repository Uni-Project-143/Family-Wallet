from pydantic import BaseModel, Field

class ConnectMonobankRequest(BaseModel):
    group_id: str = Field(..., description="ID of the group to which the card is connected")
    personal_token: str = Field(..., description="Personal Token from Monobank API")
