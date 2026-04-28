from datetime import datetime
from urllib.parse import urlparse

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

# Імпортуємо залежність для перевірки авторизації (заміни на свій імпорт, якщо він інакший)
from app.core.dependencies import get_current_user

# Імпортуємо моделі
from app.models.group_membership import GroupMembership
from app.models.invite import InviteToken
from app.models.user import User

router = APIRouter()


class GroupCreateRequest(BaseModel):
    name: str


class JoinGroupRequest(BaseModel):
    invite_link: str


def _extract_token_from_link(invite_link: str) -> str:
    """Витягує токен з invite_link виду https://<host>/join/<token>."""
    try:
        parsed = urlparse(invite_link.strip())
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid invite link structure")

    parts = [p for p in parsed.path.split("/") if p]
    if len(parts) < 2 or parts[-2] != "join" or not parts[-1]:
        raise HTTPException(status_code=400, detail="Invalid invite link structure")

    return parts[-1]


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_group(request: GroupCreateRequest, current_user: User = Depends(get_current_user)):
    """Створення нової сім'ї/групи. Користувач автоматично стає ADMIN."""
    from app.models.group import Group

    # 1. Створюємо саму групу
    new_group = Group(name=request.name, created_by=current_user.id)
    await new_group.insert()

    # 2. Створюємо запис про членство з роллю ADMIN
    membership = GroupMembership(user_id=current_user.id, group_id=new_group.id, role="ADMIN")
    await membership.insert()

    return {
        "message": "Group created successfully",
        "group_id": str(new_group.id),
        "name": new_group.name,
    }


@router.get("/{group_id}/invite", status_code=status.HTTP_200_OK)
async def get_invite_link(
    group_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get an active invite link for the group.
    If a valid link already exists, returns it. If not, creates a new one.
    Available ONLY to users with the ADMIN role in this group.
    """
    try:
        group_obj_id = ObjectId(group_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid group ID format")

    # Перевірка прав доступу (тільки ADMIN)
    membership = await GroupMembership.find_one(
        GroupMembership.user_id == current_user.id,
        GroupMembership.group_id == group_obj_id
    )

    if not membership:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not a member of this group")
    if membership.role != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only an administrator can view invite links")

    now = datetime.utcnow()
    base_url = "https://family-wallet.com"

    # 1. Шукаємо вже існуючий активний токен для цієї групи
    active_invite = await InviteToken.find_one(
        # БУЛО: InviteToken.group_id == str(group_obj_id)
        InviteToken.group_id == group_obj_id,  # <--- ПРИБРАЛИ str()
        InviteToken.expires_at > now
    )

    # Якщо знайшли — просто повертаємо його (не плодимо дублікати в БД)
    if active_invite:
        return {
            "invite_link": f"{base_url}/join/{active_invite.token}",
            "token": active_invite.token,
            "expires_at": active_invite.expires_at
        }

    # 2. Якщо активного токена немає (або всі прострочені) — створюємо новий
    new_invite = InviteToken(
        group_id=str(group_obj_id),
        created_by=str(current_user.id)
    )
    await new_invite.insert()

    return {
        "invite_link": f"{base_url}/join/{new_invite.token}",
        "token": new_invite.token,
        "expires_at": new_invite.expires_at
    }


@router.post("/{group_id}/invite/regenerate", status_code=status.HTTP_200_OK)
async def regenerate_invite_link(
    group_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Invalidate all existing invite links for the group and generate a new one.
    Available ONLY to users with the ADMIN role in this group.
    """
    try:
        group_obj_id = ObjectId(group_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid group ID format")

    # Перевірка прав доступу (тільки ADMIN)
    membership = await GroupMembership.find_one(
        GroupMembership.user_id == current_user.id,
        GroupMembership.group_id == group_obj_id
    )

    if not membership:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not a member of this group")
    if membership.role != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only an administrator can regenerate invite links")

    now = datetime.utcnow()

    await InviteToken.find(

        InviteToken.group_id == group_obj_id,
        InviteToken.expires_at > now
    ).update({"$set": {"expires_at": now}})


    new_invite = InviteToken(
        group_id=group_obj_id,
        created_by=current_user.id
    )
    await new_invite.insert()

    base_url = "https://family-wallet.com"

    # 3. Віддаємо новий лінк фронтенду
    return {
        "invite_link": f"{base_url}/join/{new_invite.token}",
        "token": new_invite.token,
        "expires_at": new_invite.expires_at
    }


@router.post("/join", status_code=status.HTTP_200_OK)
async def join_group(request: JoinGroupRequest, current_user: User = Depends(get_current_user)):
    """Приєднання до групи за invite_link (для ролі MEMBER)"""
    # 0. Витягуємо токен з посилання
    token = _extract_token_from_link(request.invite_link)

    # 1. Шукаємо токен в базі
    invite = await InviteToken.find_one(InviteToken.token == token)

    if not invite:
        raise HTTPException(status_code=400, detail="Invalid or forged invite token")

    # 2. Перевіряємо, чи не прострочений лінк (Negative AC -> 410 Gone)
    if invite.expires_at < datetime.utcnow():
        raise HTTPException(status_code=410, detail="Invite link has expired")

    # 3. Перевіряємо, чи користувач вже не в цій сім'ї
    existing_member = await GroupMembership.find_one(
        GroupMembership.user_id == current_user.id, GroupMembership.group_id == invite.group_id
    )
    if existing_member:
        raise HTTPException(status_code=400, detail="You are already a member of this group")

    # 4. Створюємо членство з роллю MEMBER
    new_membership = GroupMembership(
        user_id=current_user.id, group_id=invite.group_id, role="MEMBER"
    )
    await new_membership.insert()

    # 5. Фіксуємо час використання (для аналітики Conversion Rate з ТЗ)
    invite.used_at = datetime.utcnow()
    await invite.save()

    return {"message": "You have successfully joined the family!"}
