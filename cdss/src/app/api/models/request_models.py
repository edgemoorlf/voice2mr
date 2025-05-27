from fastapi import UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional, List

class CDSSRequestModel(BaseModel):
    prompt: str
    role: str
    session_id: Optional[str] = None
    medical_records: Optional[str] = None
    history: Optional[List[str]] = None
    language: str = "zh"  # Default to Chinese for backward compatibility

class VoiceFileRequest(BaseModel):
    voice_file: UploadFile = None
    is_json: bool = False
    prompt: str = ""

class MRRequestModel(BaseModel):
    transcript: str
    medical_records: Optional[str] = None
    is_json: bool = True
    language: str = "zh"  # Default to Chinese for backward compatibility
