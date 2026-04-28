from pydantic import BaseModel, Field
from typing import Annotated, Literal


class ClassifyRequest(BaseModel):
    task: Literal["classify"] = "classify"
    text: str


class ExtractionRequest(BaseModel):
    task: Literal["extract"] = "extract"
    text: str

class ContextAnswerRequest(BaseModel):
    task: Literal["answer_with_context"] = "answer_with_context"
    text: str

LLMRequest = Annotated[
    ClassifyRequest | ExtractionRequest | ContextAnswerRequest,
    Field(discriminator="task")
]