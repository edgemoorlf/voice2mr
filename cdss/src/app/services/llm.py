from openai import OpenAI
from typing import Dict, List, Optional
from app.core.config import (
    LLM_API_URL, LLM_API_KEY, LLM_MODEL_NAME,
    FALLBACK_LLM_API_URL, FALLBACK_LLM_API_KEY, FALLBACK_MODEL_NAME
)
from app.core.exceptions import LLMServiceError
from app.core.i18n import get_language_prompt

class LLMService:
    def __init__(self):
        self.primary_client = OpenAI(base_url=LLM_API_URL, api_key=LLM_API_KEY)
        self.fallback_client = OpenAI(base_url=FALLBACK_LLM_API_URL, api_key=FALLBACK_LLM_API_KEY)

    def _add_json_instruction(self, messages: List[Dict]) -> List[Dict]:
        """Add JSON instruction to system message"""
        messages = messages.copy()
        if messages and messages[0]["role"] == "system":
            messages[0]["content"] = messages[0]["content"] + " Please respond in JSON format."
        else:
            messages.insert(0, {"role": "system", "content": "Please respond in JSON format."})
        return messages

    def _create_chat_completion(self, client: OpenAI, model: str, messages: List[Dict], response_format: Optional[Dict] = None):
        """Create a chat completion that works with OpenAI, DeepSeek and Ollama APIs"""
        try:
            base_url_str = str(client.base_url)
            
            # Check for DeepSeek API
            if "deepseek" in base_url_str.lower():
                # DeepSeek format
                kwargs = {
                    'model': model,
                    'messages': messages,
                }
                if response_format and response_format.get("type") == "json_object":
                    kwargs['messages'] = self._add_json_instruction(messages)
                return client.chat.completions.create(**kwargs)
            
            # Check for Ollama (local URL)
            elif "localhost" in base_url_str or "127.0.0.1" in base_url_str:
                # Ollama format
                if response_format and response_format.get("type") == "json_object":
                    messages = self._add_json_instruction(messages)
                return client.chat.completions.create(
                    model=model,
                    messages=messages,
                    stream=False
                )
            else:
                # OpenAI format
                kwargs = {
                    'model': model,
                    'messages': messages,
                }
                if response_format:
                    kwargs['messages'] = self._add_json_instruction(messages)
                    kwargs['response_format'] = response_format
                return client.chat.completions.create(**kwargs)
        except Exception as e:
            raise LLMServiceError(client.base_url, str(e))

    async def generate_completion(
        self,
        messages: List[Dict],
        is_json: bool = False,
        system_context: Optional[str] = None
    ) -> Dict:
        """
        Generate a completion using the LLM service.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            is_json: Whether to request JSON formatted response
            system_context: Optional system context to prepend to messages
            
        Returns:
            Dict containing 'content' and 'usage' information
        """
        try:
            formatted_messages = []
            if system_context:
                formatted_messages.append({"role": "system", "content": system_context})
            formatted_messages.extend(messages)

            kwargs = {
                'model': LLM_MODEL_NAME,
                'messages': formatted_messages
            }
            
            if is_json:
                kwargs['response_format'] = {"type": "json_object"}

            response = self._create_chat_completion(
                client=self.primary_client,
                **kwargs
            )
            
            return {
                'content': response.choices[0].message.content,
                'usage': response.usage
            }
            
        except Exception as primary_error:
            try:
                # Try fallback service
                kwargs['model'] = FALLBACK_MODEL_NAME
                fallback_response = self._create_chat_completion(
                    client=self.fallback_client,
                    **kwargs
                )
                
                return {
                    'content': fallback_response.choices[0].message.content,
                    'usage': fallback_response.usage
                }
                
            except Exception as fallback_error:
                raise LLMServiceError(
                    "All Services",
                    f"Primary: {str(primary_error)}. Fallback: {str(fallback_error)}"
                )

# Create a singleton instance
llm_service = LLMService()
