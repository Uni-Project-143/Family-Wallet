from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime, timezone
from beanie import PydanticObjectId
from decimal import Decimal
from pydantic import BaseModel

from app.api.auth import get_current_user
from app.models.user import User
from app.models.group_membership import GroupMembership
from app.models.transaction import Transaction
from app.models.bank_card import BankCard
from app.models.gift_event import GiftEvent, GiftStatus
from app.schemas.gift import CreateGiftRequest, CreateGiftResponse
from app.models.gift_invite import GiftInvite
import uuid


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

    # 1. Організатор намагається обрати себе як Target User -> 400
    if str(current_user.id) == request.target_user_id:
        raise HTTPException(status_code=400, detail="You cannot be the recipient of a gift.")

    # 2. Безпека: Перевіряємо, чи сам організатор є в цій групі
    organizer_membership = await GroupMembership.find_one({
        "user_id": current_user_oid,
        "group_id": group_oid
    })
    if not organizer_membership:
        raise HTTPException(status_code=403, detail="You are not a member of this group.")

    # 3. Перевірка, чи Target User є учасником групи
    target_membership = await GroupMembership.find_one({
        "user_id": target_oid,
        "group_id": group_oid
    })
    if not target_membership:
        raise HTTPException(status_code=400, detail="The recipient is not a member of this group.")

    # 4. Створення події
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

    # 1. Negative AC: 404 для cancelled або неіснуючих
    if not gift or gift.status == GiftStatus.CANCELLED:
        raise HTTPException(status_code=404, detail="Подарунок не значено")

    # 2. PROJ-58: ІЗОЛЯЦІЯ TARGET USER
    is_target_user = gift.target_user_id == str(current_user.id)
    now_utc = datetime.now(timezone.utc).replace(tzinfo=None)
    gift_unlock_date = gift.unlock_date.replace(tzinfo=None)

    is_locked = now_utc < gift_unlock_date

    if is_target_user and is_locked:
        raise HTTPException(status_code=403, detail="Сюрприз! Ви поки не можете бачити цю сторінку.")

    # 3. БОЙОВА ЛОГІКА: Підрахунок грошей та донорів
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

    # ==========================================
    # КРИТИЧНО: Цей блок стоїть ЖОРСТКО НА ОДНОМУ РІВНІ з циклами for!
    # Навіть якщо донорів немає, Python обов'язково виконає цей код.
    # ==========================================
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
# PROJ-59: Генерація invite-лінку
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

    # Перевірка: тільки Організатор може генерувати лінк (Negative AC)
    if gift.organizer_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Тільки організатор може генерувати запрошення")

    # Перевіряємо, чи є вже активний лінк, щоб не плодити дублікати
    now_utc = datetime.now(timezone.utc)
    existing_invite = await GiftInvite.find_one(
        GiftInvite.gift_id == str(gift.id),
        GiftInvite.expires_at > now_utc
    )

    if existing_invite:
        token = existing_invite.token
    else:
        # Генеруємо новий UUID (відповідає Technical AC: 128 bit entropy)
        token = str(uuid.uuid4())
        new_invite = GiftInvite(
            gift_id=str(gift.id),
            organizer_id=str(current_user.id),
            token=token
        )
        await new_invite.insert()

    # Формуємо URL (у реальному проєкті домен береться з ENV конфігів)
    invite_url = f"https://твій-домен.com/gift/join/{token}"

    return {
        "invite_url": invite_url,
        "token": token
    }

# ==========================================
# БЛОКЕР: Отримання всіх подарунків групи для Sidebar
# ==========================================
@router.get("/group/{group_id}", status_code=status.HTTP_200_OK)
async def get_group_gifts(group_id: str, current_user: User = Depends(get_current_user)):
    try:
        group_oid = PydanticObjectId(group_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Невалідний формат ID")

    # Безпека: перевіряємо чи юзер у групі
    membership = await GroupMembership.find_one({"user_id": PydanticObjectId(str(current_user.id)), "group_id": group_oid})
    if not membership:
        raise HTTPException(status_code=403, detail="Ви не є учасником цієї групи")

    # Шукаємо всі активні подарунки групи
    active_gifts = await GiftEvent.find(
        GiftEvent.group_id == group_id,
        GiftEvent.status == GiftStatus.ACTIVE
    ).to_list()

    now_utc = datetime.now(timezone.utc).replace(tzinfo=None)
    response_data = []

    for gift in active_gifts:
        # Логіка ізоляції Target User (виключаємо, якщо час ще не настав)
        gift_unlock_naive = gift.unlock_date.replace(tzinfo=None)
        if gift.target_user_id == str(current_user.id) and now_utc < gift_unlock_naive:
            continue # Пропускаємо цей подарунок для іменинника

        # Дістаємо ім'я іменинника (для UX)
        target_user = await User.get(PydanticObjectId(gift.target_user_id))
        target_name = target_user.full_name or getattr(target_user, 'email', None) or "Без імені" if target_user else "Невідомий"

        # Рахуємо зібрану суму
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

    # Валідація з контракту
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

    # Створюємо транзакцію (amount з мінусом, бо це витрата)
    tx = Transaction(
        card_id=request.card_id,
        amount=Decimal(str(-request.amount)),
        group_id=gift.group_id,
        category_id="gift_contribution",  # або інша дефолтна категорія
        description=f"Внесок до Secret Gift: {gift.name}",
        is_secret_gift=True,
        target_user_id=gift.target_user_id,
        gift_id=str(gift.id)
    )
    await tx.insert()

    # Рахуємо нову суму для респонсу
    gift_txs = await Transaction.find(Transaction.gift_id == str(gift.id)).to_list()
    new_collected = sum(abs(t.amount) for t in gift_txs)

    return {"success": True, "new_collected_amount": float(new_collected)}
