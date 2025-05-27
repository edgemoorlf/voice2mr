import pytest
from unittest.mock import Mock, patch, MagicMock
from app.services.llm import LLMService, llm_service
from app.core.exceptions import LLMServiceError

@pytest.fixture
def mock_openai():
    with patch('app.services.llm.OpenAI') as mock:
        yield mock

@pytest.fixture
def mock_response():
    response = Mock()
    response.choices = [Mock(message=Mock(content="Test response"))]
    response.usage = Mock(
        prompt_tokens=10,
        completion_tokens=20,
        total_tokens=30
    )
    return response

@pytest.fixture
def llm_service_instance(mock_openai):
    return LLMService()

async def test_generate_completion_success(llm_service_instance, mock_response, mock_openai):
    """Test successful completion generation"""
    # Setup mock
    mock_openai.return_value.chat.completions.create.return_value = mock_response
    
    # Test data
    messages = [{"role": "user", "content": "test message"}]
    system_context = "test context"
    
    # Call the service
    result = await llm_service_instance.generate_completion(
        messages=messages,
        system_context=system_context
    )
    
    # Assertions
    assert result["content"] == "Test response"
    assert result["usage"].prompt_tokens == 10
    assert result["usage"].completion_tokens == 20
    assert result["usage"].total_tokens == 30
    
    # Verify the call
    mock_openai.return_value.chat.completions.create.assert_called_once()

async def test_generate_completion_json(llm_service_instance, mock_response, mock_openai):
    """Test completion with JSON response format"""
    mock_openai.return_value.chat.completions.create.return_value = mock_response
    
    result = await llm_service_instance.generate_completion(
        messages=[{"role": "user", "content": "test"}],
        is_json=True
    )
    
    # Verify JSON format was requested
    call_kwargs = mock_openai.return_value.chat.completions.create.call_args.kwargs
    assert call_kwargs.get("response_format") == {"type": "json_object"}

async def test_primary_service_failure_fallback_success(llm_service_instance, mock_response, mock_openai):
    """Test fallback to secondary service when primary fails"""
    # Make primary service fail
    mock_openai.return_value.chat.completions.create.side_effect = [
        Exception("Primary service error"),
        mock_response  # Fallback service succeeds
    ]
    
    result = await llm_service_instance.generate_completion(
        messages=[{"role": "user", "content": "test"}]
    )
    
    # Verify fallback worked
    assert result["content"] == "Test response"
    assert mock_openai.return_value.chat.completions.create.call_count == 2

async def test_both_services_failure(llm_service_instance, mock_openai):
    """Test error when both primary and fallback services fail"""
    # Make both services fail
    mock_openai.return_value.chat.completions.create.side_effect = [
        Exception("Primary service error"),
        Exception("Fallback service error")
    ]
    
    with pytest.raises(LLMServiceError) as exc_info:
        await llm_service_instance.generate_completion(
            messages=[{"role": "user", "content": "test"}]
        )
    
    assert "Primary" in str(exc_info.value)
    assert "Fallback" in str(exc_info.value)

def test_singleton_instance():
    """Test that llm_service is a singleton"""
    assert isinstance(llm_service, LLMService)
    
    # Create a new instance and verify it's different
    new_instance = LLMService()
    assert new_instance is not llm_service

@pytest.mark.parametrize("base_url,expected_format", [
    ("http://localhost:11434/v1", "stream=False"),  # Ollama format
    ("https://api.openai.com/v1", "response_format"),  # OpenAI format
])
async def test_api_format_selection(llm_service_instance, mock_openai, base_url, expected_format):
    """Test correct API format selection based on URL"""
    # Set the base URL
    mock_openai.return_value.base_url = base_url
    mock_openai.return_value.chat.completions.create.return_value = Mock(
        choices=[Mock(message=Mock(content="test"))],
        usage=Mock(prompt_tokens=1, completion_tokens=1, total_tokens=2)
    )
    
    await llm_service_instance.generate_completion(
        messages=[{"role": "user", "content": "test"}],
        is_json=True
    )
    
    # Verify the correct format was used
    call_kwargs = mock_openai.return_value.chat.completions.create.call_args.kwargs
    if "localhost" in base_url:
        assert call_kwargs.get("stream") is False
    else:
        assert "response_format" in call_kwargs 