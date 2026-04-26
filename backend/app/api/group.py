from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId
from datetime import datetime
from urllib.parse import urlparse
from pydantic import BaseModel

# Імпортуємо моделі
from app.models.group_membership import GroupMembership
from app.models.invite import InviteToken
# Імпортуємо залежність для перевірки авторизації (заміни на свій імпорт, якщо він інакший)
from app.core.dependencies import get_current_user
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
async def create_group(
    request: GroupCreateRequest,
    current_user: User = Depends(get_current_user)
):
    """Створення нової сім'ї/групи. Користувач автоматично стає ADMIN."""
    from app.models.group import Group

    # 1. Створюємо саму групу
    new_group = Group(name=request.name, created_by=current_user.id)
    await new_group.insert()

    # 2. Створюємо запис про членство з роллю ADMIN
    membership = GroupMembership(
        user_id=current_user.id,
        group_id=new_group.id,
        role="ADMIN"
    )
    await membership.insert()

    return {
        "message": "Group created successfully",
        "group_id": str(new_group.id),
        "name": new_group.name
    }

@router.get("/{group_id}/invite", status_code=status.HTTP_200_OK)
async def generate_invite_link(
    group_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Генерація унікального посилання для запрошення в групу.
    Доступно ТІЛЬКИ для користувачів з роллю ADMIN у цій групі.
    """
    try:
        group_obj_id = ObjectId(group_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid group ID format")

    # КРОК 2: Перевірка прав доступу (Чи є юзер в цій групі і чи він АДМІН)
    membership = await GroupMembership.find_one(
        GroupMembership.user_id == current_user.id,
        GroupMembership.group_id == group_obj_id
    )

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this group"
        )

    if membership.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only an administrator can generate invite links"
        )

    # КРОК 3: Генерація та збереження токена
    new_invite = InviteToken(
        group_id=group_obj_id,
        created_by=current_user.id
    )
    await new_invite.insert()

    # КРОК 4: Формування відповіді
    # Для MVP можна захардкодити домен фронтенду в .env, наприклад FRONTEND_URL=http://localhost:3000
    base_url = "https://family-wallet.com"  # або os.getenv("FRONTEND_URL")
    invite_link = f"{base_url}/join/{new_invite.token}"

    return {
        "invite_link": invite_link,
        "token": new_invite.token,
        "expires_at": new_invite.expires_at
    }


@router.post("/join", status_code=status.HTTP_200_OK)
async def join_group(
    request: JoinGroupRequest,
    current_user: User = Depends(get_current_user)
):
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
        GroupMembership.user_id == current_user.id,
        GroupMembership.group_id == invite.group_id
    )
    if existing_member:
        raise HTTPException(status_code=400, detail="You are already a member of this group")

    # 4. Створюємо членство з роллю MEMBER
    new_membership = GroupMembership(
        user_id=current_user.id,
        group_id=invite.group_id,
        role="MEMBER"
    )
    await new_membership.insert()

    # 5. Фіксуємо час використання (для аналітики Conversion Rate з ТЗ)
    invite.used_at = datetime.utcnow()
    await invite.save()

    return {"message": "You have successfully joined the family!"}
