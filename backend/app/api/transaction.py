from fastapi import APIRouter, Depends, HTTPException, Request, status
from beanie import PydanticObjectId
from app.api.auth import get_current_user
from app.core.limiter import limiter
from app.models.user import User
from app.models.bank_card import BankCard
from app.models.group_membership import GroupMembership
from app.schemas.transaction import (
    TransactionFilterParams,
    TransactionPaginatedResponse,
    TransferRequest,
    TransferResponse,
)
from app.services.transaction_service import TransactionService
from app.schemas.transaction import ReactionRequest

router = APIRouter()

@router.get("/group/{group_id}", response_model=TransactionPaginatedResponse, status_code=status.HTTP_200_OK)
async def get_group_transactions(
    group_id: str,
    filters: TransactionFilterParams = Depends(),
    current_user: User = Depends(get_current_user)
):
    """
    Отримання всіх транзакцій групи (по всіх картках учасників).
    """
    try:
        group_oid = PydanticObjectId(group_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Некоректний формат ID групи")

    is_member = await GroupMembership.find_one({
        "user_id": current_user.id,
        "group_id": group_oid
    })

    if not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ заборонено: ви не є учасником цієї групи"
        )

    group_cards = await BankCard.find({"group_id": group_id}).to_list()
    card_ids = [str(card.id) for card in group_cards]

    if not card_ids:
        return {"items": [], "total": 0, "page": filters.page, "size": filters.size, "pages": 1}

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

@router.post("/{transaction_id}/react", status_code=status.HTTP_200_OK)
async def react_to_transaction(
    transaction_id: str,
    payload: ReactionRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Додає або оновлює емодзі-реакцію користувача на транзакцію.
    Автоматично розсилає оновлення по WebSocket всім учасникам групи.
    """
    result = await TransactionService.react_to_transaction(
        transaction_id=transaction_id,
        user_id=str(current_user.id),
        emoji=payload.emoji
    )
    return result
