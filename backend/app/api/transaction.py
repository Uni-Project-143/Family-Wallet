from fastapi import APIRouter, Depends, HTTPException, Request, status
from beanie import PydanticObjectId
from app.api.auth import get_current_user
from app.core.limiter import limiter
from app.models.user import User
from app.models.bank_card import BankCard
from app.models.group_membership import GroupMembership # Додали імпорт
from app.schemas.transaction import (
    TransactionFilterParams,
    TransactionPaginatedResponse,
    TransferRequest,
    TransferResponse,
)
from app.services.transaction_service import TransactionService

router = APIRouter()

# ЗМІНЕНО: Тепер приймаємо group_id у шляху
@router.get("/group/{group_id}", response_model=TransactionPaginatedResponse, status_code=status.HTTP_200_OK)
async def get_group_transactions(
    group_id: str,
    filters: TransactionFilterParams = Depends(),
    current_user: User = Depends(get_current_user)
):
    """
    Отримання всіх транзакцій групи (по всіх картках учасників).
    """
    # 1. Валідація ID групи
    try:
        group_oid = PydanticObjectId(group_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Некоректний формат ID групи")

    # 2. БЕЗПЕКА: Перевіряємо, чи є юзер учасником цієї групи
    is_member = await GroupMembership.find_one({
        "user_id": current_user.id,
        "group_id": group_oid
    })

    if not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ заборонено: ви не є учасником цієї групи"
        )

    # 3. Шукаємо ВСІ картки, які прив'язані до цієї групи
    group_cards = await BankCard.find({"group_id": group_id}).to_list()
    card_ids = [str(card.id) for card in group_cards]

    # 4. Якщо в групі ще немає жодної картки - повертаємо порожній список
    if not card_ids:
        return {"items": [], "total": 0, "page": filters.page, "size": filters.size, "pages": 1}

    # 5. Передаємо всі зібрані ID карток у наш сервіс (фільтри залишаються працювати як раніше!)
    return await TransactionService.get_transactions(
        card_ids=card_ids,
        filters=filters
    )


@router.post(
    "/transfer",
    response_model=TransferResponse,
    status_code=status.HTTP_200_OK,
)
@limiter.limit("30/minute")
async def create_transfer(
    request: Request,
    payload: TransferRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Створює віртуальний переказ між картками сімейної групи.
    Дві immutable транзакції з is_virtual=True та однаковим transfer_id.
    Не торкається реальних коштів — змінюється лише ефективний баланс.
    """
    return await TransactionService.create_transfer(
        payload=payload,
        current_user_id=str(current_user.id),
    )
