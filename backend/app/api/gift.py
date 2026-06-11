from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime, timezone
from beanie import PydanticObjectId
from decimal import Decimal
from pydantic import BaseModel
import uuid

from beanie.odm.operators.update.general import Inc
from app.api.auth import get_current_user
from app.models.user import User
from app.models.group_membership import GroupMembership
from app.models.transaction import Transaction
from app.models.bank_card import BankCard
from app.models.gift_event import GiftEvent, GiftStatus
# ---> ДОДАНО ІМПОРТ JoinGiftRequest <---
from app.schemas.gift import CreateGiftRequest, CreateGiftResponse, JoinGiftRequest
from app.models.gift_invite import GiftInvite

router = APIRouter(prefix="/api/v1/gift", tags=["Secret Gift"])

@router.post("/create", status_code=status.HTTP_201_CREATED, response_model=CreateGiftResponse)
async def create_gift_event(
    request: CreateGiftRequest,
    current_user: User = Depends(get_current_user)
):
    try:
        group_oid = PydanticObjectId(request.group_id)
        target_oid = PydanticObjectId(request.target_user_id)
        current_user_oid = PydanticObjectId(str(current_user.id))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    if str(current_user.id) == request.target_user_id:
        raise HTTPException(status_code=400, detail="You cannot be the recipient of a gift.")

    organizer_membership = await GroupMembership.find_one({
        "user_id": current_user_oid,
        "group_id": group_oid
    })
    if not organizer_membership:
        raise HTTPException(status_code=403, detail="You are not a member of this group.")

    target_membership = await GroupMembership.find_one({
        "user_id": target_oid,
        "group_id": group_oid
    })
    if not target_membership:
        raise HTTPException(status_code=400, detail="The recipient is not a member of this group.")

    new_gift = GiftEvent(
        name=request.name,
        organizer_id=str(current_user.id),
        target_user_id=request.target_user_id,
        group_id=request.group_id,
        goal_amount=request.goal_amount,
        unlock_date=request.unlock_date,
        status=GiftStatus.ACTIVE
    )
    await new_gift.insert()

    return CreateGiftResponse(status="success", gift_id=str(new_gift.id))

@router.get("/{gift_id}/details", status_code=status.HTTP_200_OK)
async def get_gift_details(gift_id: str, current_user: User = Depends(get_current_user)):
    try:
        gift_oid = PydanticObjectId(gift_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Невалідний формат ID")

    gift = await GiftEvent.get(gift_oid)

    if not gift or gift.status == GiftStatus.CANCELLED:
        raise HTTPException(status_code=404, detail="Подарунок не значено")

    is_target_user = gift.target_user_id == str(current_user.id)
    now_utc = datetime.now(timezone.utc).replace(tzinfo=None)
    gift_unlock_date = gift.unlock_date.replace(tzinfo=None)

    is_locked = now_utc < gift_unlock_date

    if is_target_user and is_locked:
        raise HTTPException(status_code=403, detail="Сюрприз! Ви поки не можете бачити цю сторінку.")

    gift_transactions = await Transaction.find(Transaction.gift_id == str(gift.id)).to_list()

    collected_amount = Decimal("0.0")
    donor_user_ids = set()

    for tx in gift_transactions:
        collected_amount += abs(tx.amount)
        if tx.card_id:
            try:
                card = await BankCard.get(PydanticObjectId(tx.card_id))
                if card and card.user_id:
                    donor_user_ids.add(card.user_id)
            except Exception:
                continue

    donors_list = []
    for donor_id in donor_user_ids:
        try:
            donor = await User.get(PydanticObjectId(donor_id))
            if donor:
                donors_list.append({
                    "id": str(donor.id),
                    "name": donor.full_name or getattr(donor, 'email', None) or "Без імені",
                    "avatar": getattr(donor, 'avatar_url', None)
                })
        except Exception:
            continue

    target_user = await User.get(PydanticObjectId(gift.target_user_id))
    organizer = await User.get(PydanticObjectId(gift.organizer_id))

    target_name = target_user.full_name or getattr(target_user, 'email', None) or "Без імені" if target_user else "Невідомий"
    organizer_name = organizer.full_name or getattr(organizer, 'email', None) or "Без імені" if organizer else "Невідомий"

    return {
        "id": str(gift.id),
        "name": gift.name,
        "target_user_id": gift.target_user_id,
        "target_user_name": target_name,
        "organizer_id": gift.organizer_id,
        "organizer_name": organizer_name,
        "unlock_date": gift.unlock_date,
        "status": gift.status,
        "goal_amount": getattr(gift, 'goal_amount', 0),
        "collected_amount": float(collected_amount),
        "donors": donors_list
    }


# ==========================================
# PROJ-59: Генерація invite-лінку (ОНОВЛЕНО)
# ==========================================
@router.post("/{gift_id}/invite", status_code=status.HTTP_200_OK)
async def generate_gift_invite(gift_id: str, current_user: User = Depends(get_current_user)):
    try:
        gift_oid = PydanticObjectId(gift_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Невалідний формат ID")

    gift = await GiftEvent.get(gift_oid)
    if not gift or gift.status == GiftStatus.CANCELLED:
        raise HTTPException(status_code=404, detail="Подарунок не знайдено")

    if gift.organizer_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Тільки організатор може генерувати запрошення")

    now_utc = datetime.now(timezone.utc)
    existing_invite = await GiftInvite.find_one({
        "gift_id": str(gift.id),
        "expires_at": {"$gt": now_utc}
    })

    if existing_invite:
        token = existing_invite.token
    else:
        token = str(uuid.uuid4())
        new_invite = GiftInvite(
            gift_id=str(gift.id),
            organizer_id=str(current_user.id),
            token=token
        )
        await new_invite.insert()

    # Формуємо URL так само, як group-invite (https://family-wallet.com).
    invite_link = f"https://family-wallet.com/gift/join/{token}"

    return {
        "invite_link": invite_link,
        "token": token
    }

@router.post("/join", status_code=status.HTTP_200_OK)
async def join_gift_by_invite(request: JoinGiftRequest, current_user: User = Depends(get_current_user)):
    token = request.invite_link.strip("/").split("/")[-1]

# ==========================================
# ОНОВЛЕНО: Тепер приймає JSON з лінкою, а не токен в URL
# ==========================================
@router.post("/join", status_code=status.HTTP_200_OK)
async def join_gift_by_invite(request: JoinGiftRequest, current_user: User = Depends(get_current_user)):
    """
    Ендпоінт для переходу за запрошенням на Secret Gift.
    Витягує токен з лінки, валідує його та ізолює іменинника.
    """
    # 1. Екстракція токена з лінки (напр. https://family-wallet.com/gift/join/abc-123 -> abc-123)
    token = request.invite_link.strip("/").split("/")[-1]

    # 2. Шукаємо активний токен в базі
    now_utc = datetime.now(timezone.utc)
    invite = await GiftInvite.find_one({
        "token": token,
        "expires_at": {"$gt": now_utc}
    })

    if not invite:
        raise HTTPException(
            status_code=404,
            detail="Запрошення не знайдено або його термін дії минув"
        )

    # 3. Шукаємо сам подарунок
    try:
        gift_oid = PydanticObjectId(invite.gift_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Пошкоджений ID подарунка в токені")

    gift = await GiftEvent.get(gift_oid)
    if not gift or gift.status == GiftStatus.CANCELLED:
        raise HTTPException(status_code=404, detail="Подарунок не знайдено або збір скасовано")

    # 4. PROJ-58: Ізоляція іменинника
    if str(current_user.id) == gift.target_user_id:
        raise HTTPException(
            status_code=403,
            detail="Сюрприз! Ви не можете підглядати за власним подарунком 🎁"
        )

    # 5. Перевірка: чи є юзер учасником сім'ї/групи
    membership = await GroupMembership.find_one({
        "user_id": PydanticObjectId(str(current_user.id)),
        "group_id": PydanticObjectId(gift.group_id)
    })

    if not membership:
        raise HTTPException(
            status_code=403,
            detail="Тільки учасники цієї групи можуть долучитися до подарунка"
        )

    return {
        "message": "Успішно звадільовано",
        "gift_id": str(gift.id),
        "group_id": gift.group_id,
        "gift_name": gift.name
    }


@router.get("/group/{group_id}", status_code=status.HTTP_200_OK)
async def get_group_gifts(group_id: str, current_user: User = Depends(get_current_user)):
    try:
        group_oid = PydanticObjectId(group_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Невалідний формат ID")

    membership = await GroupMembership.find_one({"user_id": PydanticObjectId(str(current_user.id)), "group_id": group_oid})
    if not membership:
        raise HTTPException(status_code=403, detail="Ви не є учасником цієї групи")

    gifts = await GiftEvent.find({
        "group_id": group_id,
        "status": {"$in": [GiftStatus.ACTIVE.value, GiftStatus.REVEALED.value]}
    }).to_list()

    response_data = []

    for gift in gifts:
        if gift.status == GiftStatus.ACTIVE and gift.target_user_id == str(current_user.id):
            continue

        target_user = await User.get(PydanticObjectId(gift.target_user_id))
        target_name = target_user.full_name or getattr(target_user, 'email', None) or "Без імені" if target_user else "Невідомий"

        gift_txs = await Transaction.find(Transaction.gift_id == str(gift.id)).to_list()
        collected_amount = sum(abs(tx.amount) for tx in gift_txs)

        response_data.append({
            "id": str(gift.id),
            "name": gift.name,
            "target_user_id": gift.target_user_id,
            "target_user_name": target_name,
            "unlock_date": gift.unlock_date,
            "goal_amount": getattr(gift, 'goal_amount', 0),
            "collected_amount": float(collected_amount),
            "status": gift.status
        })

    return response_data


from pydantic import BaseModel
class ContributeRequest(BaseModel):
    amount: float
    card_id: str

@router.post("/{gift_id}/contribute", status_code=status.HTTP_200_OK)
async def contribute_to_gift(
    gift_id: str,
    request: ContributeRequest,
    current_user: User = Depends(get_current_user)
):
    try:
        gift_oid = PydanticObjectId(gift_id)
        card_oid = PydanticObjectId(request.card_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Невалідний формат ID")

    gift = await GiftEvent.get(gift_oid)
    if not gift:
        raise HTTPException(status_code=404, detail="Подарунок не знайдено")

    if gift.status != GiftStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Збір вже закрито")

    now_utc = datetime.now(timezone.utc).replace(tzinfo=None)
    if now_utc >= gift.unlock_date.replace(tzinfo=None):
        raise HTTPException(status_code=400, detail="Час збору вже минув")

    if str(current_user.id) == gift.target_user_id:
        raise HTTPException(status_code=400, detail="Ви не можете донатити на свій же сюрприз")

    if request.amount <= 0 or request.amount > 100000:
        raise HTTPException(status_code=400, detail="Невалідна сума внеску")

    membership = await GroupMembership.find_one({
        "user_id": PydanticObjectId(str(current_user.id)),
        "group_id": PydanticObjectId(gift.group_id)
    })
    if not membership:
        raise HTTPException(status_code=403, detail="Ви не у цій групі")

    card = await BankCard.get(card_oid)
    if not card or card.user_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Картка вам не належить")

    tx = Transaction(
        card_id=request.card_id,
        amount=Decimal(str(-request.amount)),
        group_id=gift.group_id,
        category_id="gift_contribution",
        description=f"Внесок до Secret Gift: {gift.name}",
        is_secret_gift=True,
        target_user_id=gift.target_user_id,
        gift_id=str(gift.id)
    )
    await tx.insert()

    # Атомарне списання грошей з картки донатера
    await card.update(Inc({BankCard.virtual_balance: -float(request.amount)}))

    gift_txs = await Transaction.find(Transaction.gift_id == str(gift.id)).to_list()
    new_collected = sum(abs(t.amount) for t in gift_txs)

    return {"success": True, "new_collected_amount": float(new_collected)}
