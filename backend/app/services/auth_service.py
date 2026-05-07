from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.core.security import get_password_hash, verify_password, create_access_token
from app.exceptions import UserAlreadyExistsError, InvalidCredentialsError
from app.schemas.auth import UserRegisterRequest, UserLoginRequest


class AuthService:

    @staticmethod
    async def register(request: UserRegisterRequest) -> dict:
        # 1. Перевірка дублікату
        existing_user = await UserRepository.get_by_email(request.email)
        if existing_user:
            raise UserAlreadyExistsError()

        # 2. Хешування та створення
        hashed_pwd = get_password_hash(request.password)
        new_user = User(
            full_name=request.fullName,
            email=request.email,
            hashed_password=hashed_pwd
        )
        await UserRepository.create(new_user)

        # 3. Генерація токена
        token = create_access_token(user_id=str(new_user.id))

        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                        "id": str(new_user.id),
                        "email": new_user.email,
                        "fullName": new_user.full_name
                    }
        }
    @staticmethod
    async def login(request: UserLoginRequest) -> dict:
        # 1. Шукаємо юзера
        user = await UserRepository.get_by_email(request.email)

        # 2. Перевіряємо пароль
        if not user or not verify_password(request.password, user.hashed_password):
            raise InvalidCredentialsError()

        # 3. Генерація токена
        token = create_access_token(user_id=str(user.id))

        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": str(user.id),
                "email": user.email,
                "fullName": user.full_name
            }
        }
