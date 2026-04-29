from fastapi import APIRouter
import logging
from app.models.requests import LLMRequest, ExtractionRequest, ClassificationRequest
from app.models.responses import ExtractResponse, HealthResponse, ExtractErrorResponse
from app.services.extract_llm import llm_extract_request
from app.services.classify_llm import llm_classify_request

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/llm_request", response_model=ExtractResponse)
def llm_request(payload: LLMRequest):
    logger.info(f"request received for task {payload.task}")
    response = llm_extract_request(payload.text, payload.task)
    return response

@router.post("/classify", response_model="ClassificationResponse")
def classify_llm_request(payload: ClassificationRequest):
    logger.info("request received for classification")
    response = llm_classify_request(payload.text)
    if "error" in response:
        return ExtractErrorResponse(error=response["error"], raw=response.get("raw"))
    return response

@router.get("/health", response_model=HealthResponse)
def health():
    logger.info('health request received')
    return HealthResponse(message="I am alive")