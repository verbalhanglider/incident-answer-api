
from asyncio.log import logger
from urllib import request
from fastapi.exceptions import RequestValidationError
from fastapi import FastAPI
from app.logging_config import logger
from app.api.routes import router
from app.middleware.logging_middleware import LoggingMiddleware
from .exception_handlers import (
    app_exception_handler,
    http_exception_handler,
    request_validation_handler,
    unhandled_exception_handler,
)
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.models.errors import AppException

app = FastAPI()
app.add_middleware(LoggingMiddleware)
app.add_exception_handler(AppException, app_exception_handler) # type: ignore
app.add_exception_handler(StarletteHTTPException, http_exception_handler) # type: ignore
app.add_exception_handler(RequestValidationError, request_validation_handler) # type: ignore
app.add_exception_handler(Exception, unhandled_exception_handler)

app.include_router(router)