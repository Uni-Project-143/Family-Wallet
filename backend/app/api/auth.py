from fastapi import APIRouter, status, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.schemas.auth import UserRegisterRequest, UserLoginRequest, TokenResponse
from app.services.auth_service import AuthService
from app.core.limiter import limiter

# Нові імпорти для логауту
from app.core.dependencies import get_current_user
from app.repositories.token_repository import TokenRepository

router = APIRouter()
security = HTTPBearer()


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=TokenResponse)
async def register(request_data: UserRegisterRequest):
    """Реєстрація нового користувача."""
    return await AuthService.register(request_data)


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/15minutes")
async def login(request: Request, login_data: UserLoginRequest):
    """Авторизація користувача та отримання JWT токена."""
    return await AuthService.login(login_data)


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    current_user=Depends(get_current_user)
):
    """
    Вихід користувача з системи.
    Додає поточний JWT токен у чорний список.
    """
    # Дістаємо сам рядок токена
    token = credentials.credentials

    # Записуємо його в базу (чорний список)
    await TokenRepository.add_to_blacklist(token)

    return {"message": "Successfully logged out"}
