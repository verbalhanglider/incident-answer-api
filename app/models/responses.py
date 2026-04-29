from typing import Annotated, Literal, Optional
from pydantic import BaseModel, Field

class ClassificationExtractResponse(BaseModel):
    kind: Literal["classification"] = "classification"
    intent: str
    confidence_notes: str
    confidence: float
    raw_text: str

class BillingExtractResponse(BaseModel):
    kind: Literal["billing"] = "billing" 
    customer: str
    amount: float
    issue_type: str
    summary: str

class ExtractionResponseFromContext(BaseModel):
    kind: Literal["context"] = "context"
    answer: str

class ExtractErrorResponse(BaseModel):
    kind: Literal["error"] = "error"
    error: str
    raw: str | None = None

ExtractResponse = Annotated[
    BillingExtractResponse | ExtractionResponseFromContext | ExtractErrorResponse,
    Field(discriminator='kind')
]

classsificationResponse = Annotated[ 
    ClassificationExtractResponse | ExtractErrorResponse,
    Field(discriminator='kind')
]

class HealthResponse(BaseModel):
    message: str