import unittest
from unittest.mock import AsyncMock, patch
from transia.standalone_engines import OpenAICompatibleEngine

@patch("transia.standalone_engines.OpenAICompatibleEngine.async_translate")
class TestAutoGlossary(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.engine = OpenAICompatibleEngine(config={"api_key": "test"})

    async def test_term_extraction(self, mock_translate):
        mock_translate.return_value = '{"Meursault": "默尔索"}'
        terms = await self.engine.extract_terms("Original", "Translation")
        self.assertEqual(terms["Meursault"], "默尔索")
