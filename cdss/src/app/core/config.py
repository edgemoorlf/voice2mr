import os
from dotenv import load_dotenv

# Load environment variables from app/.env
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env')) 

# LLM Configuration
LLM_API_URL = os.environ.get("LLM_API_URL", "http://localhost:11434/v1")
LLM_API_KEY = os.environ.get("LLM_API_KEY", "not used")
LLM_MODEL_NAME = os.environ.get("LLM_MODEL_NAME", "gemma3:1b")
FALLBACK_LLM_API_URL = os.environ.get("FALLBACK_LLM_API_URL", "http://localhost:11434/v1")
FALLBACK_LLM_API_KEY = os.environ.get("FALLBACK_LLM_API_KEY", "not used")
FALLBACK_MODEL_NAME = os.environ.get("FALLBACK_MODEL_NAME", "qwen2.5:0.5b")
LIGHT_MODE = os.environ.get("LIGHT_MODE", "True")
HAS_ASR = os.environ.get("asr", "False")
HAS_OCR = os.environ.get("ocr", "False")
APP_VERSION = "1.0.0"

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
    },
    "deepseek": {
        "api_key": os.environ.get("DEEPSEEK_API_KEY"),
        "base_url": "https://api.deepseek.com"
    }
}

# Light mode detection
try:
    import app.services.asr
    import app.services.ocr
    HAS_ASR = True
    HAS_OCR = True
except ImportError:
    HAS_ASR = False
    HAS_OCR = False

LIGHT_MODE = not (HAS_ASR and HAS_OCR)
