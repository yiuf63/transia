import unittest
import asyncio
from transia.standalone_engines import StandaloneBaseEngine
from unittest.mock import patch, MagicMock

class MockEngine(StandaloneBaseEngine):
    def get_endpoint(self):
        return "http://test.com"
    def get_headers(self):
        return {"User-Agent": "test"}
    def get_body(self, text):
        return {"q": text}
    def get_result(self, response):
        return response

class TestBaseEngine(unittest.IsolatedAsyncioTestCase):
    async def test_async_translate(self):
        engine = MockEngine(source_lang="en", target_lang="zh")
        with patch('transia.standalone_engines.async_request') as mock_async_request:
            mock_async_request.return_value = "translated"
            res = await engine.async_translate("hello")
            self.assertEqual(res, "translated")
            mock_async_request.assert_called_once()

if __name__ == "__main__":
    unittest.main()