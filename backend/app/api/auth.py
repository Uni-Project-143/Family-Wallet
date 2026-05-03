from fastapi import APIRouter, status, Request
from app.schemas.auth import UserRegisterRequest, UserLoginRequest, TokenResponse
from app.services.auth_service import AuthService
from app.core.limiter import limiter

router = APIRouter()

@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=TokenResponse)
async def register(request_data: UserRegisterRequest):
    """Реєстрація нового користувача."""
    return await AuthService.register(request_data)

@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/15minutes")
async def login(request: Request, login_data: UserLoginRequest):
    """Авторизація користувача та отримання JWT токена."""
    return await AuthService.login(login_data)
