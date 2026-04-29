from pydantic import BaseModel, Field
from typing import Annotated, Literal

class ExtractionRequest(BaseModel):
    task: Literal["extract"] = "extract"
    text: str

class ContextAnswerRequest(BaseModel):
    task: Literal["answer_with_context"] = "answer_with_context"
    text: str

LLMRequest = Annotated[
    ExtractionRequest | ContextAnswerRequest,
    Field(discriminator="task")
]

class ClassificationRequest(BaseModel):
    text: str