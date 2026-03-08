import unittest
import os
from unittest.mock import MagicMock, AsyncMock
from transia.html_processor import HtmlProcessor
from transia.standalone_engines import GoogleFreeEngine
from transia.cache import TranslationCache
from transia.batch_processor import BatchProcessor

class TestProgressCallback(unittest.IsolatedAsyncioTestCase):
    async def test_callback_trigger(self):
        engine = GoogleFreeEngine()
        engine.async_translate = AsyncMock(return_value="翻译结果文字")
        
        db_path = "test_progress.db"
        if os.path.exists(db_path): os.remove(db_path)
        cache = TranslationCache(db_path=db_path)
        batch_proc = BatchProcessor(max_batch_chars=100)
        
        processor = HtmlProcessor(engine, cache, batch_proc)
        # 关键：禁用缓存确保进入翻译流水线
        processor.use_cache = False
        
        callback = MagicMock()
        processor.on_progress = callback
        
        from lxml import etree
        # 增加文字长度确保不被过滤
        tree = etree.fromstring("<html><body><p>This is a long sentence to trigger progress.</p></body></html>")
        await processor.process_tree(tree)
        
        # 验证进度回调是否被调用
        self.assertGreaterEqual(callback.call_count, 1)
        if os.path.exists(db_path): os.remove(db_path)
