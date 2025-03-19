"""Pydantic models for request and response validation"""
from pydantic import BaseModel
from typing import Optional, List
from fastapi import UploadFile, File


class CDSSRequestModel(BaseModel):
    """Model for CDSS request"""
    prompt: str
    role: str
    session_id: Optional[str] = None
    medical_records: Optional[str] = None
    history: Optional[List[str]] = None


class CDSSResponseModel(BaseModel):
    """Model for CDSS response"""
    session_id: str
    content: str
    timestamp: int
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class MRRequestModel(BaseModel):
    """Model for Medical Record request"""
    transcript: str
    medical_records: Optional[str] = None
    is_json: bool = True


class MRResponseModel(BaseModel):
    """Model for Medical Record response"""
    content: str
    timestamp: int
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ScaleResponseModel(BaseModel):
    """Model for Scale response"""
    answers: List[str]
    key_values: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int 