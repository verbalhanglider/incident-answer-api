from copy import copy
import logging
from typing import Any

from .llm_client import call_llm_with_retry
from ..models.requests import ClassificationRequest
from ..models.responses import ClasssificationResponse
from ..models.internals import LLMRequestSpec
from .prompts import INTENT_CLASSIFIER_PROMPT, INTENT_CLASSIER_SYSTEM_PROMPT
from .response_adapters import build_response_adapter
from .schemas import CLASSIFIER_SCHEMA


logger = logging.getLogger(__name__)

def build_classification_spec(payload: ClassificationRequest) -> LLMRequestSpec:
    response_adapter = build_response_adapter(ClasssificationResponse)
    return LLMRequestSpec(
        provider="ollama",
        url="http://localhost:11434/api/chat",
        model_name="gemma3",
        system_prompt=INTENT_CLASSIER_SYSTEM_PROMPT,
        prompt=copy(INTENT_CLASSIFIER_PROMPT).replace("FILL_IN_QUESTION", payload.text),
        output_schema=response_adapter.json_schema(),
        stream=False
    )

def llm_classify_request(payload: ClassificationRequest) -> dict[str, Any]:
    spec = build_classification_spec(payload)
    logger.info(spec.output_schema)
    response = call_llm_with_retry(spec)
    if "error" in response:
        response["kind"] = "error"
    else:
        response["kind"] = "classification"
    return response
