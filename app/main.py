
from asyncio.log import logger
from urllib import request

from fastapi import FastAPI
from app.logging_config import setup_logging
from app.api.routes import router

setup_logging()
app = FastAPI()

@app.middleware("http")
async def log_requests(request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response


app.include_router(router)