import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from bson import ObjectId
from bson.errors import InvalidId
from beanie.odm.operators.update.general import Inc

from app.api.auth import get_current_user
from app.models.user import User
from app.models.money_request import MoneyRequest, RequestStatus
from app.models.group_membership import GroupMembership
from app.models.bank_card import BankCard
from app.models.transaction import Transaction
from app.repositories.transaction_repository import TransactionRepository
from app.schemas.money_request import CreateMoneyRequestDto, UpdateMoneyRequestDto
from app.core.websockets import ws_manager

router = APIRouter(prefix="/api/v1/requests", tags=["Money Requests"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_money_request(
    payload: CreateMoneyRequestDto,
    current_user: User = Depends(get_current_user)
):
    requester_id = str(current_user.id)

    if requester_id == payload.recipient_id:
        raise HTTPException(status_code=400, detail="Не можна надіслати запит самому собі")

    requester_membership = await GroupMembership.find_one(
        GroupMembership.user_id == ObjectId(requester_id)
    )
    if not requester_membership:
        raise HTTPException(status_code=403, detail="Ви не є учасником жодної групи")

    group_id = str(requester_membership.group_id)

    recipient_membership = await GroupMembership.find_one({
        "user_id": ObjectId(payload.recipient_id),
        "group_id": ObjectId(group_id)
    })

    if not recipient_membership:
        raise HTTPException(status_code=403, detail="Отримувач не є учасником вашої групи")

    new_request = MoneyRequest(
        requester_id=requester_id,
        recipient_id=payload.recipient_id,
        group_id=group_id,
        amount=payload.amount,
        description=payload.description
    )
    await new_request.insert()

    ws_payload = {
        "event": "new_request",
        "data": {
            "request_id": str(new_request.id),
            "amount": float(new_request.amount),
            "from_user": requester_id,
            "description": new_request.description
        }
    }
    await ws_manager.broadcast_to_group(group_id, ws_payload)

    return {
        "status": "success",
        "request_id": str(new_request.id),
        "message": "Запит успішно надіслано"
    }


@router.get("/incoming", response_model=List[MoneyRequest])
async def get_incoming_requests(
    status: RequestStatus = RequestStatus.PENDING,
    current_user: User = Depends(get_current_user)
):
    return await MoneyRequest.find(
        MoneyRequest.recipient_id == str(current_user.id),
        MoneyRequest.status == status
    ).to_list()


@router.patch("/{request_id}")
async def update_money_request(
    request_id: str,
    payload: UpdateMoneyRequestDto,
    current_user: User = Depends(get_current_user)
):
    try:
        req_oid = ObjectId(request_id)
    except (InvalidId, TypeError):
        raise HTTPException(status_code=404, detail="Запит не знайдено (невірний ID)")

    money_request = await MoneyRequest.get(req_oid)
    if not money_request:
        raise HTTPException(status_code=404, detail="Запит не знайдено")

    if money_request.recipient_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Ви не можете відповідати на чужий запит")

    if money_request.status != RequestStatus.PENDING:
        raise HTTPException(status_code=409, detail="Запит вже вирішено")

    if payload.status == RequestStatus.ACCEPTED:
        # Перевірка, чи фронтенд надіслав ID картки
        if not payload.from_card_id:
            raise HTTPException(status_code=400, detail="Необхідно вибрати картку для оплати")

        try:
            from_card_oid = ObjectId(payload.from_card_id)
        except Exception:
            raise HTTPException(status_code=400, detail="Невалідний ID картки")

        # Шукаємо САМЕ ТУ картку, яку вибрав користувач
        from_card = await BankCard.find_one(
            BankCard.id == from_card_oid,
            BankCard.user_id == money_request.recipient_id,
            BankCard.status == "ACTIVE"
        )

        to_card = await BankCard.find_one(
            BankCard.user_id == money_request.requester_id,
            BankCard.group_id == money_request.group_id,
            BankCard.status == "ACTIVE"
        )

        if not from_card:
            raise HTTPException(status_code=400, detail="Вибрана картка не знайдена або неактивна")
        if not to_card:
            raise HTTPException(status_code=400, detail="У отримувача немає активної картки")

        if from_card.virtual_balance < money_request.amount:
            raise HTTPException(status_code=400, detail="Недостатньо коштів на вибраній картці")

        transfer_id = str(uuid.uuid4())
        debit_amount = -abs(money_request.amount)
        credit_amount = +abs(money_request.amount)

        debit = Transaction(
            card_id=str(from_card.id),
            amount=debit_amount,
            currency="UAH",
            description=f"Запит виконано: {money_request.description or 'Без опису'}",
            group_id=money_request.group_id,
            is_virtual=True,
            transfer_id=transfer_id
        )
        credit = Transaction(
            card_id=str(to_card.id),
            amount=credit_amount,
            currency="UAH",
            description=f"Запит виконано: {money_request.description or 'Без опису'}",
            group_id=money_request.group_id,
            is_virtual=True,
            transfer_id=transfer_id
        )

        await TransactionRepository.create_paired_virtual_transactions(debit, credit)

        # Атомарне оновлення балансів
        await from_card.update(Inc({BankCard.virtual_balance: float(debit_amount)}))
        await to_card.update(Inc({BankCard.virtual_balance: float(credit_amount)}))

    money_request.status = payload.status
    await money_request.save()

    ws_payload = {
        "event": "request_updated",
        "data": {
            "request_id": str(money_request.id),
            "status": money_request.status
        }
    }
    await ws_manager.broadcast_to_group(money_request.group_id, ws_payload)

    return {
        "status": "success",
        "message": "Запит успішно оброблено"
    }
