from app.core.config import (
    LLM_API_URL, MODEL_NAME,
    FALLBACK_LLM_API_URL, FALLBACK_MODEL_NAME,
    SUPPORTED_AUDIO_TYPES
)

def test_llm_config_values():
    """Test LLM configuration values are properly set"""
    assert isinstance(LLM_API_URL, str), "LLM_API_URL should be a string"
    assert isinstance(MODEL_NAME, str), "MODEL_NAME should be a string"
    assert isinstance(FALLBACK_LLM_API_URL, str), "FALLBACK_LLM_API_URL should be a string"
    assert isinstance(FALLBACK_MODEL_NAME, str), "FALLBACK_MODEL_NAME should be a string"
    
    # Test URL format
    assert LLM_API_URL.startswith(('http://', 'https://')), "LLM_API_URL should be a valid URL"
    assert FALLBACK_LLM_API_URL.startswith(('http://', 'https://')), "FALLBACK_LLM_API_URL should be a valid URL"

def test_supported_audio_types():
    """Test supported audio types configuration"""
    assert isinstance(SUPPORTED_AUDIO_TYPES, (list, tuple, set)), "SUPPORTED_AUDIO_TYPES should be a sequence"
    assert len(SUPPORTED_AUDIO_TYPES) > 0, "SUPPORTED_AUDIO_TYPES should not be empty"
    
    expected_types = {
        "audio/mpeg", "audio/wav", "audio/mp3", 
        "audio/m4a", "video/quicktime", "video/mp4"
    }
    assert all(audio_type in expected_types for audio_type in SUPPORTED_AUDIO_TYPES), \
        "All audio types should be valid MIME types"
