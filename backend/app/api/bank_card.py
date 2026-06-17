from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from beanie import PydanticObjectId
from app.api.auth import get_current_user
from app.models.user import User
from app.models.bank_card import BankCard
from app.models.group_membership import GroupMembership
from app.repositories.bank_card_repository import BankCardRepository
from app.schemas.bank_card import BankCardResponse

bank_card_router = APIRouter(prefix="/api/v1/bank-cards", tags=["Bank Cards"])

@bank_card_router.get("/group/{group_id}", response_model=List[BankCardResponse])
async def get_cards_by_group(
    group_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Отримання всіх карток групи. Доступно будь-якому учаснику цієї групи.
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

    cards = await BankCard.find({"group_id": group_id}).to_list()
    card_ids = [str(c.id) for c in cards]
    deltas = await BankCardRepository.get_virtual_deltas_by_card_ids(card_ids)

    response_cards = []
    for card in cards:
        owner = None
        if card.user_id:
            try:
                owner = await User.get(PydanticObjectId(card.user_id))
            except Exception:
                pass

        delta = deltas.get(str(card.id), Decimal("0"))
        effective_balance = card.balance + delta

        response_cards.append(
            BankCardResponse(
                id=str(card.id),
                user_id=str(card.user_id),
                group_id=str(card.group_id),
                account_id=card.account_id,
                masked_pan=card.masked_pan,
                balance=card.balance,
                effective_balance=effective_balance,
                virtual_balance=card.virtual_balance,
                status=card.status,
                transaction_ids=[str(tid) for tid in card.transaction_ids],
                owner_full_name=owner.full_name if owner else "Невідомий власник"
            )
        )

    return response_cards
