from fastapi import APIRouter
import logging
from pydantic import TypeAdapter

from app.models.requests import ExtractionRequest, ClassificationRequest, ContextAnswerRequest
from app.models.responses import ExtractResponse, HealthResponse, ClasssificationResponse, ContextAnswerResponse
from app.services.extract_llm import llm_extract_request
from app.services.classify_llm import llm_classify_request
from app.services.context_llm import llm_answer_from_context
from app.services.response_adapters import CLASSIFICATION_RESPONSE_ADAPTER, CONTEXT_ANSWER_RESPONSE_ADAPTER, EXTRACT_RESPONSE_ADAPTER

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/extract", response_model=ExtractResponse)
def llm_request(payload: ExtractionRequest) -> ExtractResponse:
    logger.info(f"request received for extraction")
    response = llm_extract_request(payload)
    return EXTRACT_RESPONSE_ADAPTER.validate_python(response)

@router.post("/classify", response_model=ClasssificationResponse)
def classify_llm_request(payload: ClassificationRequest) -> ClasssificationResponse:
    logger.info("request received for classification")
    response = llm_classify_request(payload)
    print(response)
    return CLASSIFICATION_RESPONSE_ADAPTER.validate_python(response)

@router.post('/answer/context', response_model=ContextAnswerResponse)
def answer_with_context(payload: ContextAnswerRequest) -> ContextAnswerResponse:
    logger.info("request received for answer with context")
    response = llm_answer_from_context(payload)
    return CONTEXT_ANSWER_RESPONSE_ADAPTER.validate_python(response)

@router.get("/health", response_model=HealthResponse)
def health():
    logger.info('health request received')
    return HealthResponse(message="I am alive")