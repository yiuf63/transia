import unittest
from unittest.mock import patch, MagicMock
from transia.search_service import SearchService

class TestSearchService(unittest.TestCase):
    @patch('transia.search_service.DDGS')
    def test_search_book_background(self, mock_ddgs):
        # 模拟搜索结果
        mock_instance = mock_ddgs.return_value.__enter__.return_value
        mock_instance.text.return_value = [
            {"body": "Alice in Wonderland is a novel by Lewis Carroll."},
            {"body": "It features a girl named Alice who falls into a rabbit hole."}
        ]
        
        service = SearchService()
        result = service.search_book("Alice's Adventures in Wonderland", "Lewis Carroll")
        
        self.assertIn("Alice", result)
        self.assertIn("Lewis Carroll", result)
        self.assertTrue(mock_instance.text.called)

if __name__ == "__main__":
    unittest.main()
