from copy import copy
import logging
from typing import Any
from pydantic import BaseModel

from app.services.providers.base import LLMRequestSpec

from .llm_client import call_llm_with_retry
from .llm_spec_factory import build_llm_request_spec
from .providers.base import LLMRequestSpec
from ..models.requests import ContextAnswerRequest
from ..models.responses import ContextAnswerResponse 
from .response_adapters import CONTEXT_ANSWER_RESPONSE_ADAPTER

logger = logging.getLogger(__name__)

class CONTEXT_ANSWER_PROMPT_INPUT(BaseModel):
    text: str
    context: list[str]

def build_system_prompt(_: CONTEXT_ANSWER_PROMPT_INPUT) -> str:
    return \
    """
   You are a helpful assistant that only returns a valid JSON object. 

    Rules: 
    - Do not include any commentary or extra text outside the JSON. 
    - The JSON must conform to the provided schema." 
    """

def build_content_prompt(payload: CONTEXT_ANSWER_PROMPT_INPUT) -> str:
    prompt_template = \
        """
    Answer the user's question using ONLY the provided context.

    If the answer is not in the context, always say you don't know based on provided context.

    Context:
    FILL_IN_CONTEXT 

    Question:
    FILL_IN_QUESTION 
    """
    prompt_template.replace("FILL_IN_CONTEXT", "\n- ".join(payload.context))
    prompt = prompt_template.replace("FILL_IN_QUESTION", payload.text)
    return prompt

def build_context_answer_spec(payload: ContextAnswerRequest) -> LLMRequestSpec:
    context = []
    prompt_input = CONTEXT_ANSWER_PROMPT_INPUT(text=payload.text, context=context)
    return build_llm_request_spec(prompt_input, CONTEXT_ANSWER_RESPONSE_ADAPTER, build_system_prompt, build_content_prompt)

def llm_answer_from_context(payload: ContextAnswerRequest) -> ContextAnswerResponse:
    spec = build_context_answer_spec(payload)
    raw_response = call_llm_with_retry(spec)
    response = CONTEXT_ANSWER_RESPONSE_ADAPTER.validate_python(raw_response)
    return response