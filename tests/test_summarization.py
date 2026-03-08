import unittest
from unittest.mock import AsyncMock, patch
from transia.html_processor import HtmlProcessor
from transia.standalone_engines import OpenAICompatibleEngine
from transia.cache import TranslationCache
from transia.batch_processor import BatchProcessor

class TestSummarization(unittest.IsolatedAsyncioTestCase):
    async def test_chapter_summary_flow(self):
        engine = OpenAICompatibleEngine(config={"api_key": "test"})
        engine.generate_summary = AsyncMock(return_value="Summary of chapter")
        engine.async_translate = AsyncMock(return_value="translated text")
        
        # 确保缓存表存在
        cache = TranslationCache(db_path="test_sum.db")
        batch_proc = BatchProcessor()
        
        processor = HtmlProcessor(engine, cache, batch_proc)
        processor.summarize_enabled = True
        
        from lxml import etree
        tree = etree.fromstring("<html><body><p>Text to trigger summary</p></body></html>")
        
        # 核心：必须模拟 process_tree 结束后的总结调用
        # 在目前的 HtmlProcessor 中，总结是在 process_tree 内部执行的
        await processor.process_tree(tree)
        
        # 验证总结是否被存入背景
        bg = getattr(engine, "background", "")
        self.assertIn("Previous: Summary of chapter", bg)
        
        import os
        if os.path.exists("test_sum.db"): os.remove("test_sum.db")
