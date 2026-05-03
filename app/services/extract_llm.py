import logging
from typing_extensions import Any
from pydantic import BaseModel

from .llm_client import call_llm_with_retry
from .llm_spec_factory import build_llm_request_spec
from .providers.base import LLMRequestSpec
from ..models.requests import ExtractionRequest
from ..models.responses import ExtractResponse
from .response_adapters import EXTRACT_RESPONSE_ADAPTER

logger = logging.getLogger(__name__)

class EXTRACTION_PROMPT_INPUT(BaseModel):
    text: str

def build_system_prompt(_: EXTRACTION_PROMPT_INPUT) -> str:
    return \
    """
   You are a helpful assistant that only returns a valid JSON object. 

    Rules: 
    - Do not include any commentary or extra text outside the JSON. 
    - The JSON must conform to the provided schema." 
    """

def build_content_prompt(payload: EXTRACTION_PROMPT_INPUT):
    return payload.text 

def build_extraction_request_spec(payload: ExtractionRequest) -> LLMRequestSpec:
    prompt_input = EXTRACTION_PROMPT_INPUT(text=payload.text)
    return build_llm_request_spec(prompt_input, EXTRACT_RESPONSE_ADAPTER, build_system_prompt, build_content_prompt)

def llm_extract_request(payload: ExtractionRequest) -> ExtractResponse:
    spec = build_extraction_request_spec(payload)
    raw_response = call_llm_with_retry(spec)
    response = EXTRACT_RESPONSE_ADAPTER.validate_python(raw_response)
    return response
