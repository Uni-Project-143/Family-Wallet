import logging
from datetime import datetime
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

logger = logging.getLogger("FamilyWallet")

async def global_exception_handler(request: Request, exc: Exception):
    """Перехоплює будь-який краш і віддає стандартний JSON."""
    logger.error(f"CRITICAL ERROR: {repr(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "errorCode": "INTERNAL_ERROR",
            "message:": "Сталася непередбачувана помилка на сервері"
        }
    )

async def http_exception_handler(request: Request, exc: HTTPException):
    """Обробляє стандартні помилки HTTP."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "errorCode": f"HTTP_{exc.status_code}",
            "message": exc.detail
        }
    )
