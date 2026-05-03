
from enum import StrEnum
from pydantic import BaseModel, ConfigDict
from typing import Any

class LLMProvider(StrEnum):
    OLLAMA = "ollama"

class LLMRequestSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")
    provider: LLMProvider
    url: str
    model_name: str
    system_prompt: str
    prompt: str
    output_schema: dict[str, Any]
    stream: bool = False