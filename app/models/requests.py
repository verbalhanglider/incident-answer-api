from pydantic import BaseModel, Field, ConfigDict
from typing import Annotated, Literal

class ExtractionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    text: str

class ClassificationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    text: str

class ContextAnswerRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    text: str
    context: str | None = None