"""Dependencies for dependency injection"""
from fastapi import Depends
from openai import OpenAI
from funasr import AutoModel
from paddleocr import PaddleOCR

from app.core.config import settings

# Global session storage
sessions = {}


def get_sessions():
    """Returns the session storage dictionary"""
    return sessions


def get_ocr_model():
    """Returns the OCR model instance"""
    ocr = PaddleOCR(
        use_angle_cls=settings.OCR_USE_ANGLE_CLS, 
        lang=settings.OCR_LANG
    )
    return ocr


def get_asr_model():
    """Returns the ASR model instance"""
    asr_model = AutoModel(
        model=settings.ASR_MODEL,
        vad_model=settings.ASR_VAD_MODEL,
        vad_kwargs={
            "max_single_segment_time": settings.ASR_VAD_MAX_SINGLE_SEGMENT_TIME,
            "max_end_silence_time": settings.ASR_VAD_MAX_END_SILENCE_TIME,
            "sil_to_speech_time_thres": settings.ASR_VAD_SIL_TO_SPEECH_TIME_THRES,
            "speech_to_sil_time_thres": settings.ASR_VAD_SPEECH_TO_SIL_TIME_THRES,
            "speech_2_noise_ratio": settings.ASR_VAD_SPEECH_2_NOISE_RATIO,
        },
        punc_model=settings.ASR_PUNC_MODEL,
        log_level=settings.ASR_LOG_LEVEL,
        hub=settings.ASR_HUB,
        device=settings.ASR_DEVICE,
    )
    return asr_model


def get_llm_client():
    """Returns the OpenAI client for LLM interaction"""
    client = OpenAI(base_url=settings.LLM_API_URL, api_key="not used")
    return client 