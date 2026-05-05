from pydantic import BaseModel, Field

class ConnectMonobankRequest(BaseModel):
    group_id: str = Field(..., description="ID групи, до якої підключається картка")
    personal_token: str = Field(..., description="Personal Token від Monobank API")
