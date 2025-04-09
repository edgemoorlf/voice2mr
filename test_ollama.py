import unittest
from openai import OpenAI

class TestOllamaService(unittest.TestCase):
    def setUp(self):
        self.client = OpenAI(base_url="http://localhost:11434/v1", api_key="not used")
        
    def test_chat_completion(self):
        """Test basic chat completion functionality"""
        response = self.client.chat.completions.create(
            model="gemma3:27b",  # Using same model as in jcdss.py
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello!"}
            ],
            max_tokens=50
        )
        
        # Verify response structure
        self.assertTrue(hasattr(response, 'choices'))
        self.assertTrue(len(response.choices) > 0)
        self.assertTrue(hasattr(response.choices[0], 'message'))
        self.assertTrue(hasattr(response.choices[0].message, 'content'))
        
        # Verify usage stats
        self.assertTrue(hasattr(response, 'usage'))
        self.assertTrue(hasattr(response.usage, 'prompt_tokens'))
        self.assertTrue(hasattr(response.usage, 'completion_tokens'))

    def test_error_handling(self):
        """Test invalid model handling"""
        with self.assertRaises(Exception):
            self.client.chat.completions.create(
                model="invalid-model",
                messages=[{"role": "user", "content": "Hello"}]
            )

if __name__ == '__main__':
    unittest.main()
