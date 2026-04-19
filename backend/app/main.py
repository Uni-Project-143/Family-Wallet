from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

# Імпортуємо наші модулі з папок (Кроки 1-4)
from app.middleware.logging import log_requests_middleware
from app.exceptions import global_exception_handler, http_exception_handler
from app.api import health, wallets, gifts

app = FastAPI(
    title="Family Wallet API",
    version="1.0.0"
)

# Залишаємо налаштування CORS (це потрібно для фронтенду)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. Підключаємо наше системне логування подій
app.add_middleware(BaseHTTPMiddleware, dispatch=log_requests_middleware)

# 2. Підключаємо централізовані обробники помилок
app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)

# 3. Підключаємо наші контролери (Роутери)
app.include_router(health.router)
app.include_router(wallets.router, prefix="/api/v1/wallets")
app.include_router(gifts.router, prefix="/api/v1/gifts")
