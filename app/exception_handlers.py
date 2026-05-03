from datetime import datetime, UTC
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from .models.errors import AppException
from .logging_config import logger

def error_body(request: Request, *, type_: str, code: str, message: str, details=None):
    return {
        "error": {
            "type": type_,
            "code": code,
            "message": message,
            "details": details,
            "path": request.url.path,
            "request_id": getattr(request.state, "request_id", None),
            "timestamp": datetime.now(UTC).isoformat(),
        }
    }

async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content=error_body(
            request,
            type_=exc.error_type,
            code=exc.error_code,
            message=exc.message,
            details=exc.details,
        ),
    )

async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    message = exc.detail if isinstance(exc.detail, str) else "HTTP error"
    logger.warning("http exception", extra={
        "type": "http_error",
        "code": "HTTP_{exc.status_code}",
        "error_message": message,
        "details": None if isinstance(exc.detail, str) else exc.detail 
    })
    return JSONResponse(
        status_code=exc.status_code,
        content=error_body(
            request,
            type_="http_error",
            code=f"HTTP_{exc.status_code}",
            message=message,
            details=None if isinstance(exc.detail, str) else exc.detail,
        ),
        headers=getattr(exc, "headers", None),
    )

async def request_validation_handler(request: Request, exc: RequestValidationError):

    details = [
        {
            "loc": list(err["loc"]),
            "error_message": err["msg"],
            "type": err["type"],
        }
        for err in exc.errors()
    ]
    logger.warning("request validation failed", extra=details[0])
    return JSONResponse(
        status_code=422,
        content=error_body(
            request,
            type_="request_validation",
            code="REQUEST_INVALID",
            message="Request validation failed",
            details=details,
        ),
    )

async def unhandled_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content=error_body(
            request,
            type_="internal_error",
            code="INTERNAL_SERVER_ERROR",
            message="An unexpected error occurred",
        ),
    )