from app.models.group import Group
from app.models.group_membership import GroupMembership
from bson import ObjectId

class GroupRepository:
    @staticmethod
    async def create_group(group: Group) -> Group:
        return await group.insert()

    @staticmethod
    async def add_member(membership: GroupMembership) -> GroupMembership:
        return await membership.insert()

    @staticmethod
    async def get_membership(user_id: ObjectId, group_id: ObjectId) -> GroupMembership | None:
        return await GroupMembership.find_one(
            GroupMembership.user_id == user_id,
            GroupMembership.group_id == group_id
        )
