from pydantic import BaseModel
from typing import Any
import json

from .base import LLMRequestSpec

class OllamaMessage(BaseModel):
    role: str
    content: str

class OllamaChatPayload(BaseModel):
    model: str
    messages: list[OllamaMessage]
    format: dict[str, Any]
    stream: bool = False

class OllamaAdapter:
    @staticmethod
    def build_payload(spec: LLMRequestSpec) -> dict[str, Any]:
        return OllamaChatPayload(
            model=spec.model_name,
            messages=[
                OllamaMessage(role="system", content=spec.system_prompt),
                OllamaMessage(role="user", content=spec.prompt)
            ],
            format=spec.output_schema,
            stream=spec.stream
        ).model_dump()

    @staticmethod
    def extract_response(raw_response: dict) -> Any:
        return json.loads(raw_response['message']['content'])