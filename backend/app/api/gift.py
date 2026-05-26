from fastapi import APIRouter, Depends, HTTPException, status
from app.api.auth import get_current_user
from app.models.user import User
from app.models.group_membership import GroupMembership
from app.models.gift_event import GiftEvent, GiftStatus
from app.schemas.gift import CreateGiftRequest, CreateGiftResponse
from beanie import PydanticObjectId

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

    # 3. Перевірка, чи Target User є учасником групи (BE-02)
    target_membership = await GroupMembership.find_one({
        "user_id": target_oid,
        "group_id": group_oid
    })
    if not target_membership:
        raise HTTPException(status_code=400, detail="The recipient is not a member of this group.")

    # 4. Створення події (BE-01)
    new_gift = GiftEvent(
        name=request.name,
        organizer_id=str(current_user.id),
        target_user_id=request.target_user_id,
        group_id=request.group_id,
        unlock_date=request.unlock_date,
        status=GiftStatus.ACTIVE
    )
    await new_gift.insert()

    # Повертаємо 201 Created (вказано в декораторі) + gift_id
    return CreateGiftResponse(status="success", gift_id=str(new_gift.id))
