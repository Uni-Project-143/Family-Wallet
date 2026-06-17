import logging
from datetime import datetime
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

logger = logging.getLogger("FamilyWallet")

class DomainException(HTTPException):
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)

class UserAlreadyExistsError(DomainException):
    def __init__(self):
        super().__init__(status_code=409, detail="Email is already registered")

class InvalidCredentialsError(DomainException):
    def __init__(self):
        super().__init__(status_code=401, detail="Invalid email or password")

class ForbiddenAccessError(DomainException):
    def __init__(self, detail: str = "Access denied"):
        super().__init__(status_code=403, detail=detail)

class ResourceNotFoundError(DomainException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=404, detail=detail)

class InviteExpiredError(DomainException):
    def __init__(self):
        super().__init__(status_code=410, detail="Invite link has expired")

class InvalidInviteError(DomainException):
    def __init__(self, detail: str = "Invalid or forged invite token"):
        super().__init__(status_code=400, detail=detail)

async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"INTERNAL ERROR: {repr(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "errorCode": "INTERNAL_ERROR",
            "message": "Сталася непередбачувана помилка на сервері"
        }
    )

async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "errorCode": f"HTTP_{exc.status_code}",
            "message": exc.detail
        }
    )
