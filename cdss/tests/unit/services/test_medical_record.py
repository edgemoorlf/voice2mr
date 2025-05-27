import pytest
from unittest.mock import Mock, patch, MagicMock
from app.core.exceptions import LLMServiceError

# Mock i18n functions
mock_doctor_context = "您是一位中国医院的智能医疗助手。您使用中文交流，是肿瘤学专家。"
mock_mr_format = "请将以下内容转换为正式的病历记录："
mock_mr_format_detail = """请包含以下项目：
主诉,现病史,既往史,过敏史,家族史,体格检查,辅助检查,诊断,处置意见,注意事项,中医辩证,中药处方。
如果某项无信息，请填写"无"。
请不要遗漏任何检查数据。
请不要提及任何个人身份信息。"""

def mock_get_language_prompt(language: str, prompt_key: str) -> str:
    prompts = {
        'doctor_context': mock_doctor_context,
        'mr_format': mock_mr_format,
        'mr_format_detail': mock_mr_format_detail
    }
    return prompts[prompt_key]

# Mock response
mock_response = Mock()
mock_response.choices = [Mock(message=Mock(content="""
{
    "主诉": "头痛3天",
    "现病史": "患者3天前无明显诱因出现头痛",
    "既往史": "无",
    "过敏史": "无",
    "家族史": "无",
    "体格检查": "生命体征平稳",
    "辅助检查": "无",
    "诊断": "头痛待查",
    "处置意见": "建议进一步检查",
    "注意事项": "如症状加重及时就医",
    "中医辩证": "肝阳上亢",
    "中药处方": "天麻钩藤饮"
}
"""))]
mock_response.usage = Mock(prompt_tokens=10, completion_tokens=20, total_tokens=30)

# Mock the OpenAI clients
mock_primary_client = Mock()
mock_primary_client.base_url = "http://45.78.200.182:3010/v1/"
mock_primary_client.chat.completions.create.return_value = mock_response

mock_fallback_client = Mock()
mock_fallback_client.base_url = "http://localhost:11434/v1"
mock_fallback_client.chat.completions.create.return_value = mock_response

# Create a mock LLM service
mock_llm_service = Mock()
mock_llm_service.primary_client = mock_primary_client
mock_llm_service.fallback_client = mock_fallback_client

async def mock_generate_completion(*args, **kwargs):
    # Use the mock primary client to get the response
    response = mock_primary_client.chat.completions.create(
        model="test-model",
        messages=kwargs.get('messages', []),
        response_format={"type": "json_object"} if kwargs.get('is_json') else None
    )
    return {
        'content': response.choices[0].message.content,
        'usage': response.usage
    }

mock_llm_service.generate_completion.side_effect = mock_generate_completion

# Apply patches
patches = [
    patch('app.services.medical_record.llm_service', mock_llm_service),
    patch('app.core.i18n.get_language_prompt', side_effect=mock_get_language_prompt)
]

for p in patches:
    p.start()

# Now import MedicalRecordService after patches are applied
from app.services.medical_record import MedicalRecordService

@pytest.fixture
def medical_record_service():
    return MedicalRecordService()

async def test_generate_record_from_text(medical_record_service):
    """Test medical record generation from text"""
    text = "患者男性，45岁，头痛3天。"
    result = await medical_record_service.generate_medical_record(text)
    
    assert isinstance(result, dict)
    assert "content" in result
    assert "主诉" in result["content"]
    assert "头痛3天" in result["content"]
    assert "timestamp" in result
    mock_primary_client.chat.completions.create.assert_called_once()

# Stop all patches after tests
def teardown_module(module):
    for p in patches:
        p.stop() 