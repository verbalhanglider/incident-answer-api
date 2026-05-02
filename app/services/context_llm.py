from copy import copy
import logging
from typing import Any
from pydantic import TypeAdapter

from ..models.requests import ContextAnswerRequest
from ..models.responses import ContextAnswerResponse
from ..models.internals import LLMRequestSpec
from .response_adapters import CONTEXT_ANSWER_RESPONSE_ADAPTER
from .llm_client import call_llm_with_retry
from .prompts import PROMPT_WITH_CONTEXT, EXTRACTOR_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

def build_context_answer_spec(payload: ContextAnswerRequest):
    return LLMRequestSpec(
        provider="ollama",
        url="http://localhost:11434/api/chat",
        model_name="gemma3",
        system_prompt=EXTRACTOR_SYSTEM_PROMPT,
        prompt=copy(PROMPT_WITH_CONTEXT).replace("FILL_IN_QUESTION", payload.text),
        output_schema=CONTEXT_ANSWER_RESPONSE_ADAPTER.json_schema(),
        stream=False
    )

def llm_answer_from_context(payload: ContextAnswerRequest) -> dict[str, Any]:
    logger.info("request received for answer with context")
    spec = build_context_answer_spec(payload)
    response = call_llm_with_retry(spec)
    if "error" in response:
        response["kind"] = "error"
    else:
        response["kind"] = "context"
    logger.info(response)
    return response