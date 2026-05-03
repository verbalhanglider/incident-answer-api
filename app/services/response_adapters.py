
from pydantic import TypeAdapter
from typing import Any

from ..models.responses import ExtractResponse, ContextAnswerResponse, ClassificationResponse

def build_response_adapter(response_type: Any) -> TypeAdapter:
    return TypeAdapter(response_type)

CLASSIFICATION_RESPONSE_ADAPTER = build_response_adapter(ClassificationResponse)
CONTEXT_ANSWER_RESPONSE_ADAPTER = build_response_adapter(ContextAnswerResponse)
EXTRACT_RESPONSE_ADAPTER = build_response_adapter(ExtractResponse)