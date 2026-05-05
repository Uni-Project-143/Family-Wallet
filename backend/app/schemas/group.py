from pydantic import BaseModel

class GroupResponse(BaseModel):
    id: str
    name: str
    role: str
