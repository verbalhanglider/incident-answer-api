from copy import copy
import logging
from pydantic import BaseModel
from typing import Any

from .llm_client import call_llm_with_retry
from .llm_spec_factory import build_llm_request_spec
from ..models.requests import ClassificationRequest
from .providers.base import LLMRequestSpec
from ..models.responses import ClassificationResponse
from .response_adapters import CLASSIFICATION_RESPONSE_ADAPTER


logger = logging.getLogger(__name__)

class CLASSIFICATION_PROMPT_INPUT(BaseModel):
    text: str

def build_system_prompt(_: CLASSIFICATION_PROMPT_INPUT) -> str:
    return \
    """
    You are a support intent classifier.

    Rules:
    - return only valid json
    - choose exactly one intent from the allowed set
    - do not include explanation or extra text
    - do not invent new categories
    """

def build_content_prompt(payload: CLASSIFICATION_PROMPT_INPUT):
    prompt_template = \
    """
    Classify the following message into one of these intents:

    - billing: charges, refunds, invoices, payments
    - shipping: delivery, tracking, delays, missing packages
    - general: anything not primarily about billing/payment or shipping classify as this
    - if payment, refund, invoice or charges are mentioned classify as billing even if shipping is also mentioned
    - if the request is too vague to classify as billing or shipping classify as general
    - include a confidence score following schema
    - add note explaining reason for confidence score
    - always return text received in raw_text field

    Return JSON that conforms to the provided schema

    Text:
    FILL_IN_QUESTION 
    """
    prompt = prompt_template.replace("FILL_IN_QUESTION", payload.text)
    return prompt

def build_classification_spec(payload: ClassificationRequest) -> LLMRequestSpec:
    prompt_input = CLASSIFICATION_PROMPT_INPUT(text=payload.text)
    return build_llm_request_spec(prompt_input, CLASSIFICATION_RESPONSE_ADAPTER, build_system_prompt, build_content_prompt)

def llm_classify_request(payload: ClassificationRequest) -> ClassificationResponse:
    spec = build_classification_spec(payload)
    raw_response = call_llm_with_retry(spec)
    response = CLASSIFICATION_RESPONSE_ADAPTER.validate_python(raw_response)
    return response
