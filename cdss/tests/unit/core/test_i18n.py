import pytest
from app.core.i18n import (
    get_language_prompt,
    get_error_message,
    get_medical_record_template,
    format_doctor_query_context,
    format_patient_query_context,
    SUPPORTED_LANGUAGES,
    DEFAULT_LANGUAGE
)

@pytest.mark.parametrize("language", SUPPORTED_LANGUAGES)
def test_language_prompt_basic(language):
    """Test basic prompt retrieval for all supported languages"""
    # Test basic prompts that should exist in all languages
    prompts = ['doctor_context', 'patient_context', 'mr_format']
    for prompt_key in prompts:
        prompt = get_language_prompt(language, prompt_key)
        assert isinstance(prompt, str), f"Prompt for {language}/{prompt_key} should be a string"
        assert len(prompt) > 0, f"Prompt for {language}/{prompt_key} should not be empty"

def test_language_prompt_fallback():
    """Test fallback to default language for unsupported language"""
    prompt = get_language_prompt("unsupported_lang", "doctor_context")
    default_prompt = get_language_prompt(DEFAULT_LANGUAGE, "doctor_context")
    assert prompt == default_prompt, "Should fallback to default language prompt"

def test_error_message():
    """Test error message formatting"""
    error_key = "test_error"
    message = get_error_message(DEFAULT_LANGUAGE, error_key)
    assert isinstance(message, str), "Error message should be a string"
    assert error_key in message, "Error message should contain the error key"

def test_medical_record_template():
    """Test medical record template retrieval"""
    # Test for default language
    template = get_medical_record_template(DEFAULT_LANGUAGE)
    assert isinstance(template, str), "Template should be a string"
    assert len(template) > 0, "Template should not be empty"
    assert "##" in template, "Template should contain markdown headers"
    
    # Test fallback for unsupported language
    fallback_template = get_medical_record_template("unsupported_lang")
    assert fallback_template == template, "Should fallback to default language template"

@pytest.mark.parametrize("language", SUPPORTED_LANGUAGES)
def test_query_context_formatting(language):
    """Test query context formatting for all supported languages"""
    medical_records = "Test medical records"
    retrieved_info = "Test retrieved info"
    
    # Test doctor query context
    doctor_context = format_doctor_query_context(language, medical_records, retrieved_info)
    assert isinstance(doctor_context, str), "Doctor context should be a string"
    assert medical_records in doctor_context, "Medical records should be in doctor context"
    assert retrieved_info in doctor_context, "Retrieved info should be in doctor context"
    
    # Test patient query context
    patient_context = format_patient_query_context(language, medical_records)
    assert isinstance(patient_context, str), "Patient context should be a string"
    assert medical_records in patient_context, "Medical records should be in patient context"

def test_prompt_consistency():
    """Test that all languages have consistent prompt keys"""
    base_language = DEFAULT_LANGUAGE
    base_prompts = set()
    
    # Get all prompt keys from default language
    for prompt_key in ['doctor_context', 'patient_context', 'mr_format', 
                      'mr_format_detail', 'doctor_query_context', 'patient_query_context']:
        try:
            get_language_prompt(base_language, prompt_key)
            base_prompts.add(prompt_key)
        except:
            continue
    
    # Check all languages have the same prompt keys
    for language in SUPPORTED_LANGUAGES:
        for prompt_key in base_prompts:
            prompt = get_language_prompt(language, prompt_key)
            assert isinstance(prompt, str), f"Missing or invalid prompt {prompt_key} for language {language}"
            assert len(prompt) > 0, f"Empty prompt {prompt_key} for language {language}" 