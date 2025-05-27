import pytest
import os
from pathlib import Path

@pytest.fixture
def test_data_dir():
    """Return the path to the test data directory"""
    return Path(__file__).parent / "data"

@pytest.fixture
def sample_audio_file():
    """Return sample audio file content"""
    return b"test audio data"

@pytest.fixture
def sample_image_file():
    """Return sample image file content"""
    return b"test image data"

@pytest.fixture
def sample_medical_record():
    """Return a sample medical record"""
    return """
##患者信息：##
性别： 女
年龄： 34岁
就诊时间： 2024年1月15日 15:30
科别： 皮肤科门诊

##主诉：##
双侧面颊皮疹1年余，加重20余天。
"""

@pytest.fixture(autouse=True)
def setup_test_env(monkeypatch):
    """Setup test environment variables"""
    env_vars = {
        "LLM_API_URL": "http://localhost:11434/v1",
        "MODEL_NAME": "test-model",
        "FALLBACK_LLM_API_URL": "http://localhost:11435/v1",
        "FALLBACK_MODEL_NAME": "fallback-model"
    }
    for key, value in env_vars.items():
        monkeypatch.setenv(key, value) 