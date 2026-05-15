from datetime import datetime
from bson import ObjectId
from urllib.parse import urlparse

from app.models.group import Group
from app.models.group_membership import GroupMembership
from app.models.invite import InviteToken
from app.repositories.group_repository import GroupRepository
from app.repositories.invite_repository import InviteRepository
from app.exceptions import ForbiddenAccessError, InvalidInviteError, InviteExpiredError
from app.schemas.group import GroupResponse

from app.config.database import db_client

class GroupService:
    BASE_URL = "https://family-wallet.com"

    @staticmethod
    def _extract_token(invite_link: str) -> str:
        """Витягує токен з лінки."""
        try:
            parsed = urlparse(invite_link.strip())
            parts = [p for p in parsed.path.split("/") if p]
            if len(parts) < 2 or parts[-2] != "join" or not parts[-1]:
                raise InvalidInviteError("Invalid invite link structure")
            return parts[-1]
        except Exception:
            raise InvalidInviteError("Invalid invite link structure")

    @staticmethod
    async def _check_admin_access(group_id: ObjectId, user_id: ObjectId):
        """Перевіряє, чи є користувач адміном групи."""
        membership = await GroupRepository.get_membership(user_id, group_id)
        if not membership:
            raise ForbiddenAccessError("You are not a member of this group")
        if membership.role != "ADMIN":
            raise ForbiddenAccessError("Only an administrator can perform this action")

    @classmethod
    async def create_group(cls, name: str, user_id: ObjectId) -> dict:
        # 2. ДОДАНО: Транзакція БД для атомарного створення групи та адміна
        async with await db_client.start_session() as session:
            async with session.start_transaction():
                new_group = Group(name=name, created_by=user_id)
                await GroupRepository.create_group(new_group, session=session)

                membership = GroupMembership(user_id=user_id, group_id=new_group.id, role="ADMIN")
                await GroupRepository.add_member(membership, session=session)

                return {
                    "message": "Group created successfully",
                    "group_id": str(new_group.id),
                    "name": new_group.name,
                }

    @classmethod
    async def get_invite_link(cls, group_id_str: str, user_id: ObjectId) -> dict:
        try:
            group_id = ObjectId(group_id_str)
        except Exception:
            raise InvalidInviteError("Invalid group ID format")

        await cls._check_admin_access(group_id, user_id)
        now = datetime.utcnow()
        active_invite = await InviteRepository.get_active_invite(group_id, now)

        if active_invite:
            return {
                "invite_link": f"{cls.BASE_URL}/join/{active_invite.token}",
                "token": active_invite.token,
                "expires_at": active_invite.expires_at
            }

        new_invite = InviteToken(group_id=group_id, created_by=user_id)
        await InviteRepository.create(new_invite)

        return {
            "invite_link": f"{cls.BASE_URL}/join/{new_invite.token}",
            "token": new_invite.token,
            "expires_at": new_invite.expires_at
        }

    @classmethod
    async def regenerate_invite_link(cls, group_id_str: str, user_id: ObjectId) -> dict:
        try:
            group_id = ObjectId(group_id_str)
        except Exception:
            raise InvalidInviteError("Invalid group ID format")

        await cls._check_admin_access(group_id, user_id)
        now = datetime.utcnow()

        # Інвалідуємо старі токени
        await InviteRepository.invalidate_all_for_group(group_id, now)

        # Створюємо новий
        new_invite = InviteToken(group_id=group_id, created_by=user_id)
        await InviteRepository.create(new_invite)

        return {
            "invite_link": f"{cls.BASE_URL}/join/{new_invite.token}",
            "token": new_invite.token,
            "expires_at": new_invite.expires_at
        }

    @classmethod
    async def join_group(cls, invite_link: str, user_id: ObjectId) -> dict:
        token = cls._extract_token(invite_link)
        invite = await InviteRepository.get_by_token(token)

        if not invite:
            raise InvalidInviteError("Invalid or forged invite token")

        if invite.expires_at < datetime.utcnow():
            raise InviteExpiredError()

        existing_member = await GroupRepository.get_membership(user_id, invite.group_id)
        if existing_member:
            raise InvalidInviteError("You are already a member of this group")

        # 3. ДОДАНО: Транзакція БД для атомарного приєднання та оновлення інвайту
        async with await db_client.start_session() as session:
            async with session.start_transaction():
                new_membership = GroupMembership(user_id=user_id, group_id=invite.group_id, role="MEMBER")
                await GroupRepository.add_member(new_membership, session=session)

                invite.used_at = datetime.utcnow()
                await InviteRepository.save(invite, session=session)

        return {"message": "You have successfully joined the family!"}

    @staticmethod
    async def get_user_groups(user_id: ObjectId) -> list[GroupResponse]:
        # 1. Знаходимо всі "зв'язки" юзера з групами
        memberships = await GroupRepository.get_user_memberships(user_id)

        if not memberships:
            return []  # Якщо груп немає — повертаємо пустий список (Фронт покаже Empty State)

        # 2. Збираємо всі ID груп і робимо словник (мапу) ролей,
        group_ids = [m.group_id for m in memberships]
        role_map = {str(m.group_id): m.role for m in memberships}

        # 3. Дістаємо самі групи з бази (за один запит!)
        groups = await GroupRepository.get_groups_by_ids(group_ids)

        # 4. Формуємо красиву відповідь для фронтенда
        result = []
        for group in groups:
            result.append(
                GroupResponse(
                    id=str(group.id),
                    name=group.name,
                    role=role_map.get(str(group.id), "MEMBER")
                )
            )
        return result
