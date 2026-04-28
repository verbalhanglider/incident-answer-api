from fastapi import APIRouter
import logging
from app.models.requests import LLMRequest, ExtractionRequest
from app.models.responses import ExtractResponse, HealthResponse, ExtractErrorResponse
from app.services.llm_service import make_llm_request

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/llm_request", response_model=ExtractResponse)
def llm_request(payload: LLMRequest):
    logger.info("request received for task {payload.task}")
    response = make_llm_request(payload.text, payload.task)
    return ExtractResponse(**response)

@router.get("/health", response_model=HealthResponse)
def health():
    logger.info('health request received')
    return HealthResponse(message="I am alive")