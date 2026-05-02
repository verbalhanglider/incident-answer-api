from typing import Annotated, Literal, Optional
from pydantic import BaseModel, Field

class ClassificationExtractResponse(BaseModel):
    kind: Literal["classification"] = "classification"
    intent: str
    confidence_notes: str
    confidence: float
    raw_text: str

class ExtractionResponseFromContext(BaseModel):
    kind: Literal["context"] = "context"
    answer: str

class ExtractErrorResponse(BaseModel):
    kind: Literal["error"] = "error"
    error: str
    status_code: int
    raw: str | None = None

class ExtractValidResponse(BaseModel):
    kind: Literal["extract"] = "extract"
    customer: str
    issue_type: str
    amount: int
    issue: str
    summary: str

ExtractResponse = Annotated[
    ExtractErrorResponse | ExtractValidResponse, 
    Field(discriminator='kind')
]

ClasssificationResponse = Annotated[ 
    ClassificationExtractResponse | ExtractErrorResponse,
    Field(discriminator='kind')
]

class ContextResponse(BaseModel):
    kind: Literal["context"] = "context"
    answer: str

ContextAnswerResponse = Annotated[
    ContextResponse | ExtractErrorResponse,
    Field(discriminator='kind')
    ]

class HealthResponse(BaseModel):
    message: str