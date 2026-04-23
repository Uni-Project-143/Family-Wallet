import logging
from datetime import datetime
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

logger = logging.getLogger("FamilyWallet")


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
