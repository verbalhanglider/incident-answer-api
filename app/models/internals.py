from pydantic import BaseModel, ConfigDict
from typing import Any, Dict

class OllamaMessage(BaseModel):
    role: str
    content: str

class OllamaChatPayload(BaseModel):
    model: str
    messages: list[OllamaMessage]
    format: dict[str, Any]
    stream: bool = False

class LLMRequestSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")
    provider: str
    url: str
    model_name: str
    system_prompt: str
    prompt: str
    output_schema: dict[str, Any]
    stream: bool = False

def build_ollama_provider_payload(spec: LLMRequestSpec) -> OllamaChatPayload:
    return OllamaChatPayload(
        model=spec.model_name,
        messages=[
            OllamaMessage(role="system", content=spec.system_prompt),
            OllamaMessage(role="user", content=spec.prompt)
        ],
        format=spec.output_schema,
        stream=spec.stream
    )