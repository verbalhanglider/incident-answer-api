from pydantic import BaseModel
from typing import Any, Dict

class BuildLLMPromptAndSchema(BaseModel):
    llm_system_prompt: str
    llm_output_schema: 'Dict[str, Any]'
    llm_prompt: str