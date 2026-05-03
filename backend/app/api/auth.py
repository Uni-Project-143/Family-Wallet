from fastapi import APIRouter, status
from app.schemas.auth import UserRegisterRequest, UserLoginRequest, TokenResponse
from app.services.auth_service import AuthService

router = APIRouter()

@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=TokenResponse)
async def register(request: UserRegisterRequest):
    """Реєстрація нового користувача."""
    return await AuthService.register(request)

@router.post("/login", response_model=TokenResponse)
async def login(request: UserLoginRequest):
    """Авторизація користувача та отримання JWT токена."""
    return await AuthService.login(request)
