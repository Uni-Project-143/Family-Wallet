from fastapi import APIRouter, Depends, status
from app.services.monobank_service import MonobankService

# АДАПТУЙ: імпортуй свою функцію отримання поточного юзера та модель User
from app.api.auth import get_current_user
from app.models.user import User
from app.schemas.monobank import ConnectMonobankRequest, ConnectMonobankResponse
router = APIRouter(prefix="/api/v1/monobank", tags=["Monobank Integration"])


@router.get("/webhook", status_code=status.HTTP_200_OK)
async def verify_monobank_webhook():
    """
    Ендпоінт для підтвердження вебхука від Монобанку.
    При реєстрації вебхука Монобанк відправляє GET-запит,
    щоб перевірити, чи сервер доступний і готовий приймати дані.
    """
    return {"message": "Webhook is ready"}

@router.post("/connect", status_code=status.HTTP_200_OK, response_model=ConnectMonobankResponse)
async def connect_monobank_card(
    request: ConnectMonobankRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Підключення картки Monobank через особистий API-токен.
    """
    # Сервіс тепер поверне словник з id, який FastAPI автоматично
    # перевірить на відповідність ConnectMonobankResponse
    return await MonobankService.connect_card(
        user_id=str(current_user.id),
        group_id=request.group_id,
        personal_token=request.personal_token
    )


@router.delete("/card/{card_id}", status_code=status.HTTP_200_OK)
async def disconnect_monobank_card(
    card_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Disconnect Monobank card (Soft delete).
    Transaction history remains intact.
    """
    result = await MonobankService.disconnect_card(
        card_id=card_id,
        user_id=str(current_user.id)
    )
    return result

