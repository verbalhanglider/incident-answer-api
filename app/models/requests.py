from pydantic import BaseModel


class ClassificationRequest(BaseModel):
    text: str


class ExtractionRequest(BaseModel):
    text: str