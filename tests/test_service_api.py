import unittest
from unittest.mock import MagicMock, AsyncMock, patch
from transia.translation_service import TranslationService, TransiaEvent

class TestServiceAPI(unittest.IsolatedAsyncioTestCase):
    async def test_translate_flow(self):
        # 使用 context manager 确保 patch 100% 生效
        # 必须同时 Mock get_file_hash 以防止 FileNotFoundError
        with patch("transia.translation_service.EpubHandler") as mock_handler, \
             patch("transia.translation_service.HtmlProcessor") as mock_processor, \
             patch("transia.translation_service.get_file_hash") as mock_hash:
            
            mock_hash.return_value = "fake_hash"
            
            profile = {"engine": "google"}
            service = TranslationService(profile)
            
            mock_handler_inst = mock_handler.return_value
            mock_handler_inst.get_html_files.return_value = ["chap1.html"]
            mock_handler_inst.temp_dir = "/tmp"
            
            mock_proc_inst = mock_processor.return_value
            mock_proc_inst.process_file = AsyncMock(return_value=True)
            
            success = await service.translate("dummy.epub", "out.epub", {"bilingual": True})
            self.assertTrue(success)
            mock_handler_inst.extract.assert_called_once()
            mock_handler_inst.save.assert_called_once()
