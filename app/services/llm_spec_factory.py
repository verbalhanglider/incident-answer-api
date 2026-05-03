from typing import Protocol, Callable
from pydantic import TypeAdapter, BaseModel
from typing import Any, TypeVar

from .response_adapters import build_response_adapter
from .providers.base import LLMRequestSpec, LLMProvider

P = TypeVar("P", bound=BaseModel)

DEFAULT_MODEL_URL = "http://localhost:11434/api/chat"
DEFAULT_MODEL_NAME = "gemma3"
DEFAULT_MODEL_PROVIDER = LLMProvider.OLLAMA

def build_llm_request_spec(
        payload: P,
        type_adapter: TypeAdapter,
        build_system_prompt: Callable[[P], str],
        build_content_prompt: Callable[[P], str],
        model_url: str = DEFAULT_MODEL_URL,
        model_name: str = DEFAULT_MODEL_NAME,
        model_provider: LLMProvider = DEFAULT_MODEL_PROVIDER
) -> LLMRequestSpec:
    return LLMRequestSpec(
        provider= model_provider,
        url=model_url,
        model_name=model_name,
        system_prompt=build_system_prompt(payload),
        prompt=build_content_prompt(payload),
        output_schema=type_adapter.json_schema(),
        stream=False
    )