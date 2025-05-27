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
