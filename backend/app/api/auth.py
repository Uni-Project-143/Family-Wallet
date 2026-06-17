import os
from datetime import datetime, timezone
from fastapi import APIRouter, status, Request, Response, Depends, HTTPException, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr

from app.schemas.auth import UserRegisterRequest, UserLoginRequest, TokenResponse
from app.services.auth_service import AuthService
from app.core.limiter import limiter
from app.models.user import User
from app.models.password_reset import PasswordResetToken
from app.services.notification_service import NotificationService
from app.core.dependencies import get_current_user
from app.repositories.token_repository import TokenRepository
from app.core.security import get_password_hash

router = APIRouter()
security = HTTPBearer()

@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=TokenResponse)
async def register(request_data: UserRegisterRequest):
    """Реєстрація нового користувача."""
    return await AuthService.register(request_data)

@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/15minutes")
async def login(request: Request, response: Response, login_data: UserLoginRequest):
    """Авторизація користувача та отримання JWT токена."""
    # `response: Response` обов'язковий: slowapi (headers_enabled=True) вписує в нього
    # заголовки X-RateLimit-*; без нього кидає 500 на кожен запит логіну.
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
    token = credentials.credentials
    await TokenRepository.add_to_blacklist(token)
    return {"message": "Successfully logged out"}

class FcmTokenRequest(BaseModel):
    fcm_token: str

@router.put("/me/fcm-token", status_code=status.HTTP_200_OK)
async def update_fcm_token(
    request: FcmTokenRequest,
    current_user: User = Depends(get_current_user)
):
    """Ендпоінт для фронтенда, щоб зберігати токен пристрою для Push-сповіщень"""
    current_user.fcm_token = request.fcm_token
    await current_user.save()
    return {"success": True, "message": "FCM token updated"}

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

@router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(request: ForgotPasswordRequest, background_tasks: BackgroundTasks):
    user = await User.find_one({"email": request.email})

    if not user:
        return {"message": "Якщо цей email зареєстрований, лист для відновлення пароля надіслано."}

    await PasswordResetToken.find({"email": request.email}).delete()

    reset_record = PasswordResetToken(email=request.email)
    await reset_record.insert()

    frontend_base = os.getenv("FRONTEND_URL", "http://localhost:5173")
    reset_link = f"{frontend_base}/reset-password?token={reset_record.token}"

    html_content = f"""
        <h3>Відновлення пароля</h3>
        <p>Хтось запросив скидання пароля для вашого акаунту.</p>
        <p>Натисніть на посилання нижче, щоб встановити новий пароль:</p>
        <a href="{reset_link}">{reset_link}</a>
        <p>Якщо це були не ви, просто проігноруйте цей лист.</p>
        """

    background_tasks.add_task(
        NotificationService._send_email_sendgrid,
        to_email=request.email,
        subject="Відновлення пароля у Family Wallet",
        html_content=html_content
    )

    return {"message": "Лист для відновлення пароля успішно надіслано."}

@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(request: ResetPasswordRequest):
    now_naive = datetime.now(timezone.utc).replace(tzinfo=None)
    reset_record = await PasswordResetToken.find_one({
        "token": request.token,
        "expires_at": {"$gt": now_naive}
    })

    if not reset_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Токен невалідний або його термін дії минув."
        )

    user = await User.find_one({"email": reset_record.email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Користувача не знайдено."
        )

    user.hashed_password = get_password_hash(request.new_password)
    await user.save()

    await reset_record.delete()

    return {"message": "Пароль успішно змінено. Тепер ви можете увійти."}
