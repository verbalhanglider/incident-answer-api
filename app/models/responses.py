from typing import Annotated, Literal, Optional
from pydantic import BaseModel, Field

class ClassificationResponse(BaseModel):
    intent: str
    confidence_notes: str
    confidence: float
    raw_text: str

class ExtractResponse(BaseModel):
    customer: str
    issue_type: str
    amount: int
    issue: str
    summary: str

class ContextAnswerResponse(BaseModel):
    answer: str

class HealthResponse(BaseModel):
    message: str