from app.models.invite import InviteToken
from datetime import datetime
from bson import ObjectId

class InviteRepository:
    @staticmethod
    async def get_active_invite(group_id: ObjectId, current_time: datetime, session=None) -> InviteToken | None:
        return await InviteToken.find_one(
            InviteToken.group_id == group_id,
            InviteToken.expires_at > current_time,
            session=session
        )

    @staticmethod
    async def get_by_token(token: str, session=None) -> InviteToken | None:
        return await InviteToken.find_one(
            InviteToken.token == token,
            session=session
        )

    @staticmethod
    async def create(invite: InviteToken, session=None) -> InviteToken:
        return await invite.insert(session=session)

    @staticmethod
    async def save(invite: InviteToken, session=None) -> InviteToken:
        return await invite.save(session=session)

    @staticmethod
    async def invalidate_all_for_group(group_id: ObjectId, current_time: datetime, session=None):
        # Передаємо session у find(), щоб update відпрацював у межах транзакції
        await InviteToken.find(
            InviteToken.group_id == group_id,
            InviteToken.expires_at > current_time,
            session=session
        ).update({"$set": {"expires_at": current_time}})
