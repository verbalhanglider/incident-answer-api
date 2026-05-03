from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request

from ..logging_config import logger

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Log request details
        method = request.method
        url = request.url.path

        logger.info(f"Request: {method} {url}")
        
        # Process the request
        response = await call_next(request)
        
        # Log response details
        status_code = response.status_code
        logger.info(f"Response: {method} {url} returned {status_code}")
        
        return response
