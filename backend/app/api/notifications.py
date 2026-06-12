from fastapi import APIRouter, Depends
from typing import List
from app.api.auth import get_current_user
from app.models.user import User
from app.models.notification import NotificationLog

router = APIRouter(prefix="/api/v1/notifications", tags=["Notifications"])

@router.get("/", status_code=200)
async def get_my_notifications(current_user: User = Depends(get_current_user)):
    """
    Повертає історію сповіщень поточного користувача,
    відсортовану від найновіших до найстаріших.
    """
    notifications = await NotificationLog.find(
        NotificationLog.user_id == str(current_user.id)
    ).sort("-created_at").to_list()

    return notifications

@router.patch("/mark-read", status_code=200)
async def mark_all_as_read(current_user: User = Depends(get_current_user)):
    """
    Позначає всі непрочитані сповіщення користувача як прочитані.
    """
    update_result = await NotificationLog.find(
        {"user_id": str(current_user.id), "is_read": False}
    ).update(
        {"$set": {"is_read": True}}
    )

    return {
        "status": "success",
        "message": "All notifications marked as read",
        "modified_count": update_result.modified_count if update_result else 0
    }
