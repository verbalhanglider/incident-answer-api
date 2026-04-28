from fastapi import APIRouter
import logging
from typing import Union
from app.models.requests import LLMRequest, ExtractionRequest
from app.models.responses import ExtractResponse
from app.services.llm_service import make_llm_request

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/llm_request", response_model=ExtractResponse)
def llm_request(payload: LLMRequest):
    logger.info("request received for task {payload.task}")
    response = make_llm_request(payload.text, payload.task)
    return ExtractResponse(**response)

@router.post("/classify", response_model=ClassificationResponse)
def run_classification(payload: ClassificationRequest) -> ClassificationResponse:
    logger.info('classification request with payload', extra={'json_fields': payload.model_dump_json()})
    response = ClassificationResponse(**make_llm_request(payload.text,"classify"))
    return response

@router.post("/extract", response_model=ExtractResponse)
def extract_data(payload: ExtractionRequest) -> ExtractResponse:
    logger.info('extraction request with payload', extra={'json_fields': payload.model_dump_json()})
    request_classification = make_llm_request(payload.text, "classify")
    intent = request_classification.get("intent", "")
    llm_response = {}
    if intent == "":
        llm_response = ExtractErrorResponse(kind="error", **{"error": "missing_intent", "raw": payload.text})
    if intent == "billing":
        logger.info(f'llm classified request as billing with text: {payload.text}')
        llm_response = BillingExtractResponse(kind="billing", **make_llm_request(payload.text, "extract"))
    elif intent == "shipping":
        return ExtractErrorResponse(kind="error", **{"error": "not implemented"})
    elif intent == "general":
        llm_response = ExtractionResponseFromContext(kind="context", **make_llm_request(payload.text, "answer_with_context"))
    else:
        llm_response = ExtractErrorResponse(kind="error", error='empty_intent', raw=payload.text)
    return llm_response


@router.get("/health", response_model=HealthResponse)
def health():
    logger.info('health request received')
    return HealthResponse(message="I am alive")