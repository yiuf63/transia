import unittest
import asyncio
from transia.standalone_engines import OpenAICompatibleEngine
from unittest.mock import patch, MagicMock

class TestEngineInjection(unittest.IsolatedAsyncioTestCase):
    async def test_api_key_injection(self):
        # 验证可以通过 config 动态注入 API Key
        dynamic_config = {
            "api_key": "dynamic-secret-key",
            "model": "gpt-3.5-turbo",
            "endpoint": "https://api.openai.com/v1/chat/completions"
        }
        engine = OpenAICompatibleEngine(target_lang="zh", config=dynamic_config)
        
        self.assertEqual(engine.api_key, "dynamic-secret-key")
        
        with patch('transia.standalone_engines.async_request') as mock_request:
            mock_request.return_value = '{"choices": [{"message": {"content": "你好"}}]}'
            await engine.async_translate("hello")
            
            # 检查请求头中是否使用了注入的 key
            args, kwargs = mock_request.call_args
            self.assertEqual(kwargs['headers']['Authorization'], "Bearer dynamic-secret-key")

    async def test_runtime_injection(self):
        # 验证实例化后仍能修改 key (模拟 Web 请求级别注入)
        engine = OpenAICompatibleEngine(target_lang="zh", config={"endpoint": "http://test.com"})
        engine.api_key = "runtime-key"
        
        with patch('transia.standalone_engines.async_request') as mock_request:
            mock_request.return_value = '{"choices": [{"message": {"content": "你好"}}]}'
            await engine.async_translate("hello")
            
            args, kwargs = mock_request.call_args
            self.assertEqual(kwargs['headers']['Authorization'], "Bearer runtime-key")

    async def test_deepseek_injection(self):
        from transia.standalone_engines import DeepSeekEngine
        config = {"api_key": "ds-key"}
        engine = DeepSeekEngine(target_lang="zh", config=config)
        self.assertEqual(engine.api_key, "ds-key")

    async def test_anthropic_injection(self):
        from transia.standalone_engines import AnthropicCompatibleEngine
        config = {"api_key": "ant-key"}
        engine = AnthropicCompatibleEngine(target_lang="zh", config=config)
        self.assertEqual(engine.api_key, "ant-key")

if __name__ == "__main__":
    unittest.main()
