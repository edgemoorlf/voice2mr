"""Application configuration settings"""
import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Voice2MR API"
    
    # Environment
    DEBUG: bool = os.environ.get("DEBUG", "False").lower() == "true"
    LOG_LEVEL: str = os.environ.get("LOG_LEVEL", "INFO")
    
    # LLM Settings
    LLM_API_URL: str = os.environ.get("LLM_API_URL", "http://localhost:11434/v1")
    MODEL_NAME: str = os.environ.get("MODEL_NAME", "qwen2.5:latest")
    
    # Application Settings
    DOMAIN: str = os.environ.get("DOMAIN", "oncology")
    COLLECTION: str = os.environ.get("COLLECTION", "")
    KV_LIMIT: int = int(os.environ.get("KV_LIMIT", "256"))
    
    # OCR and ASR Models
    OCR_USE_ANGLE_CLS: bool = True
    OCR_LANG: str = "ch"
    
    ASR_MODEL: str = "paraformer-zh"
    ASR_VAD_MODEL: str = "fsmn-vad"
    ASR_PUNC_MODEL: str = "ct-punc"
    ASR_HUB: str = "ms"
    ASR_DEVICE: str = "cpu"
    ASR_LOG_LEVEL: str = "info"
    
    # ASR VAD Settings
    ASR_VAD_MAX_SINGLE_SEGMENT_TIME: int = 90000
    ASR_VAD_MAX_END_SILENCE_TIME: int = 1200
    ASR_VAD_SIL_TO_SPEECH_TIME_THRES: int = 200
    ASR_VAD_SPEECH_TO_SIL_TIME_THRES: int = 200
    ASR_VAD_SPEECH_2_NOISE_RATIO: float = 1.2
    
    # Files
    HOTWORDS_FILE: str = "./hotwords.txt"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings() 