import unittest
import asyncio
import json
from transia.standalone_engines import OpenAICompatibleEngine
from unittest.mock import patch

class TestLLMEngine(unittest.IsolatedAsyncioTestCase):
    async def test_llm_request_construction(self):
        config = {
            "api_key": "test-key",
            "model": "gpt-4",
            "prompt": "Translate: <text>"
        }
        engine = OpenAICompatibleEngine(target_lang="zh", config=config)
        engine.endpoint = "https://api.openai.com/v1/chat/completions"
        
        with patch('transia.standalone_engines.async_request') as mock_async_request:
            mock_response = json.dumps({
                "choices": [{"message": {"content": "你好"}}]
            })
            mock_async_request.return_value = mock_response
            
            res = await engine.async_translate("hello")
            self.assertEqual(res, "你好")
            
            # 验证请求体
            args, kwargs = mock_async_request.call_args
            body = json.loads(kwargs['data'])
            self.assertEqual(body['model'], "gpt-4")
            self.assertIn("Translate to zh", body['messages'][1]['content'])
            self.assertIn("hello", body['messages'][1]['content'])
            self.assertEqual(kwargs['headers']['Authorization'], "Bearer test-key")

if __name__ == "__main__":
    unittest.main()
