from fastapi import APIRouter
import logging

from ..models.requests import ExtractionRequest, ClassificationRequest, ContextAnswerRequest
from ..services.classify_llm import llm_classify_request
from ..services.context_llm import llm_answer_from_context
from ..services.extract_llm import llm_extract_request
from ..models.responses import ExtractResponse, HealthResponse, ClassificationResponse, ContextAnswerResponse


logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/extract", response_model=ExtractResponse)
def llm_request(payload: ExtractionRequest) -> ExtractResponse:
    response = llm_extract_request(payload)
    return response

@router.post("/classify", response_model=ClassificationResponse)
def classify_llm_request(payload: ClassificationRequest) -> ClassificationResponse:
    response = llm_classify_request(payload)
    return response

@router.post('/answer/context', response_model=ContextAnswerResponse)
def answer_with_context(payload: ContextAnswerRequest) -> ContextAnswerResponse:
    response = llm_answer_from_context(payload)
    return response

@router.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(message="I am alive")