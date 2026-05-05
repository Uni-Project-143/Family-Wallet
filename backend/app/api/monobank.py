from fastapi import APIRouter, Depends, status
from app.schemas.monobank import ConnectMonobankRequest
from app.services.monobank_service import MonobankService

# АДАПТУЙ: імпортуй свою функцію отримання поточного юзера та модель User
from app.api.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/v1/monobank", tags=["Monobank Integration"])

@router.post("/connect", status_code=status.HTTP_200_OK)
async def connect_monobank_card(
    request: ConnectMonobankRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Підключення картки Monobank через особистий API-токен.
    """
    result = await MonobankService.connect_card(
        user_id=str(current_user.id),
        group_id=request.group_id,
        personal_token=request.personal_token
    )
    return result
