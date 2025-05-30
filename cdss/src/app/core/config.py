import os
from dotenv import load_dotenv

# Load environment variables from app/.env
load_dotenv('app/.env')

# LLM Configuration
LLM_API_URL = os.environ.get("LLM_API_URL", "http://localhost:11434/v1")
MODEL_NAME = os.environ.get("MODEL_NAME", "gemma3:1b")
FALLBACK_LLM_API_URL = os.environ.get("FALLBACK_LLM_API_URL", "http://localhost:11434/v1")
FALLBACK_MODEL_NAME = os.environ.get("FALLBACK_MODEL_NAME", "qwen2.5:0.5b")

# Constants
KV_LIMIT = 256

# Supported Media Types
SUPPORTED_AUDIO_TYPES = [
    "audio/mpeg", 
    "audio/wav", 
    "audio/mp3", 
    "audio/m4a", 
    "video/quicktime", 
    "video/mp4"
]

# ASR Configuration
ASR_CONFIG = {
    "vad_kwargs": {
        "max_single_segment_time": 90000,
        "max_end_silence_time": 1200,
        "sil_to_speech_time_thres": 200,
        "speech_to_sil_time_thres": 200,
        "speech_2_noise_ratio": 1.2,
    }
}

# Multi-language ASR/OCR Configuration
LANGUAGE_MODEL_CONFIG = {
    "asr": {
        "zh": {
            "type": "funasr",
            "model": "paraformer-zh",
            "enabled": True
        },
        "en": {
            "type": "whisper",
            "model": "base",
            "enabled": False
        },
        "es": {
            "type": "whisper", 
            "model": "base",
            "enabled": False
        },
        "fr": {
            "type": "whisper",
            "model": "base", 
            "enabled": False
        },
        "th": {
            "type": "external",  # Route to external API
            "provider": "openai",
            "enabled": False
        }
    },
    "ocr": {
        "zh": {"type": "paddleocr", "lang": "ch", "enabled": True},
        "en": {"type": "paddleocr", "lang": "en", "enabled": False},
        "es": {"type": "paddleocr", "lang": "es", "enabled": False},
        "fr": {"type": "paddleocr", "lang": "french", "enabled": False},
        "th": {"type": "paddleocr", "lang": "th", "enabled": False}
    }
}

# External service configuration
EXTERNAL_SERVICES = {
    "openai": {
        "api_key": os.environ.get("OPENAI_API_KEY"),
        "base_url": "https://api.openai.com/v1"
    },
    "azure": {
        "api_key": os.environ.get("AZURE_VISION_KEY"),
        "endpoint": os.environ.get("AZURE_VISION_ENDPOINT")
    }
}
