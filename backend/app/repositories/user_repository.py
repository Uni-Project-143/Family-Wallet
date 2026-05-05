from app.models.user import User
from bson import ObjectId

class UserRepository:
    @staticmethod
    async def get_by_email(email: str) -> User | None:
        return await User.find_one(User.email == email)

    @staticmethod
    async def get_by_id(user_id: ObjectId | str) -> User | None:
        return await User.get(user_id)

    @staticmethod
    async def create(user: User) -> User:
        return await user.insert()
