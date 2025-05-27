from pydantic import BaseModel
from typing import List

class CDSSResponseModel(BaseModel):
    session_id: str
    content: str
    timestamp: int
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

class MRResponseModel(BaseModel):
    content: str
    timestamp: int
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

class ScaleResponseModel(BaseModel):
    answers: List[str]
    key_values: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
