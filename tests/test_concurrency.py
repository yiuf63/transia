import unittest
from lxml import etree
from transia.html_processor import HtmlProcessor
from transia.standalone_engines import GoogleFreeEngine
from transia.cache import TranslationCache
from transia.batch_processor import BatchProcessor

class SlowMockEngine(GoogleFreeEngine):
    async def async_translate(self, text):
        return f"translated {text}"

class TestConcurrencyControl(unittest.IsolatedAsyncioTestCase):
    async def test_semaphore_limit(self):
        # 显式构造依赖，确保不被单例污染
        db_path = "test_concurrency.db"
        cache = TranslationCache(db_path=db_path)
        engine = SlowMockEngine()
        batch_proc = BatchProcessor(max_batch_chars=1) # 强制最小批次
        
        processor = HtmlProcessor(engine, cache, batch_proc)
        processor.use_cache = False
        
        # 构造足够长且包含字母的文本，绕过所有过滤器
        html = "<div><p>Sample long sentence alpha</p><p>Sample long sentence beta</p></div>"
        tree = etree.fromstring(html)
        
        await processor.process_tree(tree)
        
        found = tree.xpath(".//*[contains(@class, 'translated')]")
        self.assertEqual(len(found), 2)
        
        import os
        if os.path.exists(db_path): os.remove(db_path)
