from app.models.invite import InviteToken
from datetime import datetime
from bson import ObjectId

class InviteRepository:
    @staticmethod
    async def get_active_invite(group_id: ObjectId, current_time: datetime) -> InviteToken | None:
        return await InviteToken.find_one(
            InviteToken.group_id == group_id,
            InviteToken.expires_at > current_time
        )

    @staticmethod
    async def get_by_token(token: str) -> InviteToken | None:
        return await InviteToken.find_one(InviteToken.token == token)

    @staticmethod
    async def create(invite: InviteToken) -> InviteToken:
        return await invite.insert()

    @staticmethod
    async def save(invite: InviteToken) -> InviteToken:
        return await invite.save()

    @staticmethod
    async def invalidate_all_for_group(group_id: ObjectId, current_time: datetime):
        await InviteToken.find(
            InviteToken.group_id == group_id,
            InviteToken.expires_at > current_time
        ).update({"$set": {"expires_at": current_time}})
