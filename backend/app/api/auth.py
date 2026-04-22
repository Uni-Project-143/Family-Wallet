from fastapi import APIRouter, HTTPException, status
from app.schemas.auth import UserRegisterRequest, UserLoginRequest, TokenResponse
from app.models.user import User
from app.core.security import get_password_hash, verify_password, create_access_token

router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=TokenResponse)
async def register(request: UserRegisterRequest):
    # 1. Перевірка дублікату
    existing_user = await User.find_one(User.email == request.email)
    if existing_user:
        raise HTTPException(status_code=409, detail="Email вже зареєстрований")

    # 2. Хешування та створення
    hashed_pwd = get_password_hash(request.password)
    new_user = User(
        full_name=request.fullName,
        email=request.email,
        hashed_password=hashed_pwd
        # role="ADMIN" - ВИДАЛЕНО!
    )
    await new_user.insert()

    # 3. Генерація токена ТІЛЬКИ з user_id
    token = create_access_token(user_id=str(new_user.id))

    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
async def login(request: UserLoginRequest):
    user = await User.find_one(User.email == request.email)

    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невірний email або пароль"
        )

    # Генерація токена ТІЛЬКИ з user_id
    token = create_access_token(user_id=str(user.id))

    return TokenResponse(access_token=token)
