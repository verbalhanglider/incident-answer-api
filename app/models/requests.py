from pydantic import BaseModel, Field
from typing import Union
from typing_extensions import Annotated, Literal


class ClassifyRequest(BaseModel):
    task: Literal["classify"] = "classify"
    text: str


class ExtractionRequest(BaseModel):
    task: Literal["extract"] = "extract"
    text: str

class ContextAnswerRequest(BaseModel):
    task: Literal["classify"] = "classify"
    text: str

LLMRequest = Annotated[
    Union[ClassifyRequest, ExtractionRequest, ContextAnswerRequest],
    Field(discriminator="task")
]