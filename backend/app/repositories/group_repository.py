from app.models.group import Group
from app.models.group_membership import GroupMembership
from bson import ObjectId

class GroupRepository:
    @staticmethod
    async def create_group(group: Group, session=None):
        await group.insert(session=session)

    @staticmethod
    async def add_member(membership: GroupMembership, session=None):
        await membership.insert(session=session)

    @staticmethod
    async def get_membership(user_id: ObjectId, group_id: ObjectId, session=None) -> GroupMembership | None:
        return await GroupMembership.find_one(
            GroupMembership.user_id == user_id,
            GroupMembership.group_id == group_id,
            session=session
        )

    @staticmethod
    async def get_user_memberships(user_id: ObjectId, session=None):
        """Знаходить всі записи про участь юзера в групах"""
        return await GroupMembership.find(GroupMembership.user_id == user_id, session=session).to_list()

    @staticmethod
    async def get_groups_by_ids(group_ids: list[ObjectId], session=None):
        """Шукає самі групи за списком їх ID"""
        return await Group.find({"_id": {"$in": group_ids}}, session=session).to_list()
