import unittest
import asyncio
from transia.standalone_utils import async_request
from unittest.mock import patch, MagicMock

class TestAsyncRequest(unittest.IsolatedAsyncioTestCase):
    async def test_async_request_get(self):
        with patch('httpx.AsyncClient.request') as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = "async response"
            mock_request.return_value = mock_response
            
            res = await async_request("http://test.com")
            self.assertEqual(res, "async response")
            mock_request.assert_called_once()

    async def test_async_request_post(self):
        with patch('httpx.AsyncClient.request') as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = "post response"
            mock_request.return_value = mock_response
            
            res = await async_request("http://test.com", method="POST", data={"key": "value"})
            self.assertEqual(res, "post response")
            # Check if it was called with data
            args, kwargs = mock_request.call_args
            self.assertEqual(kwargs['data'], {"key": "value"})

if __name__ == "__main__":
    unittest.main()
