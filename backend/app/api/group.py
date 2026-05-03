from fastapi import APIRouter, Depends, status
from pydantic import BaseModel

# Твій імпорт для авторизації (переконайся, що він правильний)
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.group_service import GroupService

router = APIRouter()

class GroupCreateRequest(BaseModel):
    name: str

class JoinGroupRequest(BaseModel):
    invite_link: str

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_group(request: GroupCreateRequest, current_user: User = Depends(get_current_user)):
    """Створення нової сім'ї/групи. Користувач автоматично стає ADMIN."""
    return await GroupService.create_group(request.name, current_user.id)

@router.get("/{group_id}/invite", status_code=status.HTTP_200_OK)
async def get_invite_link(group_id: str, current_user: User = Depends(get_current_user)):
    """Get an active invite link for the group."""
    return await GroupService.get_invite_link(group_id, current_user.id)

@router.post("/{group_id}/invite/regenerate", status_code=status.HTTP_200_OK)
async def regenerate_invite_link(group_id: str, current_user: User = Depends(get_current_user)):
    """Invalidate all existing invite links for the group and generate a new one."""
    return await GroupService.regenerate_invite_link(group_id, current_user.id)

@router.post("/join", status_code=status.HTTP_200_OK)
async def join_group(request: JoinGroupRequest, current_user: User = Depends(get_current_user)):
    """Приєднання до групи за invite_link (для ролі MEMBER)."""
    return await GroupService.join_group(request.invite_link, current_user.id)
