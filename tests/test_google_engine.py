import unittest
import asyncio
from transia.standalone_engines import GoogleFreeEngine
from unittest.mock import patch

class TestGoogleFreeEngine(unittest.IsolatedAsyncioTestCase):
        async def test_google_translate_async(self):
            engine = GoogleFreeEngine(source_lang="en", target_lang="zh")
            mock_response = '[[["你好","hello",null,null,1]],null,"en"]'
            
            with patch('transia.standalone_engines.async_request') as mock_async_request:
                mock_async_request.return_value = mock_response
                res = await engine.async_translate("hello")
                self.assertEqual(res, "你好")
                # 验证请求参数
            args, kwargs = mock_async_request.call_args
            params = kwargs['data']
            self.assertEqual(params['tl'], "zh")
            self.assertEqual(params['q'], "hello")

if __name__ == "__main__":
    unittest.main()
