from pydantic import BaseModel
from typing import List, Optional, Dict

class CDSSResponseModel(BaseModel):
    session_id: Optional[str] = None
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

class ServerInfoModel(BaseModel):
    light_mode: bool
    features: Dict[str, bool]
    version: str
