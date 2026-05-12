from fastapi import APIRouter, Depends, status
from app.api.auth import get_current_user
from app.models.user import User
from app.models.bank_card import BankCard
from app.schemas.transaction import TransactionFilterParams, TransactionPaginatedResponse
from app.services.transaction_service import TransactionService

router = APIRouter()

@router.get("/", response_model=TransactionPaginatedResponse, status_code=status.HTTP_200_OK)
async def get_my_transactions(
    filters: TransactionFilterParams = Depends(),
    current_user: User = Depends(get_current_user)
):
    # Шукаємо всі картки юзера
    user_cards = await BankCard.find({"user_id": str(current_user.id)}).to_list()
    card_ids = [str(card.id) for card in user_cards]

    # Якщо карток немає - транзакцій теж немає
    if not card_ids:
        return {"items": [], "total": 0, "page": filters.page, "size": filters.size, "pages": 1}

    return await TransactionService.get_transactions(
        card_ids=card_ids,
        filters=filters
    )
