from copy import deepcopy
import logging
from typing_extensions import Any
from pydantic import TypeAdapter

from .prompts import EXTRACTOR_SYSTEM_PROMPT
from .response_adapters import build_response_adapter
from .schemas import EXTRACTION_SCHEMA
from app.models.internals import LLMRequestSpec
from app.models.requests import ExtractionRequest
from app.models.responses import ExtractResponse
from app.services.llm_client import call_llm_with_retry
from app.services.response_adapters import EXTRACT_RESPONSE_ADAPTER

logger = logging.getLogger(__name__)

def build_extraction_request_spec(payload: ExtractionRequest) -> LLMRequestSpec:
    return LLMRequestSpec(
        provider="ollama",
        url="http://localhost:11434/api/chat",
        model_name="gemma3",
        system_prompt=EXTRACTOR_SYSTEM_PROMPT,
        prompt=payload.text,
        output_schema=EXTRACT_RESPONSE_ADAPTER.json_schema(),
        stream=False
    )

def llm_extract_request(payload: ExtractionRequest) -> dict[str, Any]:
    logger.info(f'making request for user question {payload.text}')
    spec = build_extraction_request_spec(payload)
    response = call_llm_with_retry(spec)
    if "error" in response:
        response["kind"] = "error"
    else:
        response["kind"] = "extract"
    return response
