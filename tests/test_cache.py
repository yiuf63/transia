import unittest
import asyncio
import time
import os
from transia.html_processor import HtmlProcessor
from transia.standalone_engines import StandaloneBaseEngine
from lxml import etree

class MockEngine(StandaloneBaseEngine):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.call_count = 0

    async def async_translate(self, text):
        self.call_count += 1
        await asyncio.sleep(0.1)
        return f"Translated: {text}"

class TestCache(unittest.IsolatedAsyncioTestCase):
    async def test_translation_caching(self):
        db_path = "test_translations.db"
        if os.path.exists(db_path):
            os.remove(db_path)
            
        engine = MockEngine(target_lang="zh")
        processor = HtmlProcessor(engine)
        processor.cache.db_path = db_path
        processor.cache._init_db()
        
        html = "<html><body><p>Sentence 1</p><p>Sentence 2</p></body></html>"
        tree = etree.fromstring(html)
        
        # 1. 第一次翻译 (应该调用引擎)
        start_time = time.time()
        await processor.process_tree(tree)
        first_duration = time.time() - start_time
        self.assertEqual(engine.call_count, 1) # 由于批处理，2个段落合成1个 batch
        
        # 2. 第二次翻译 (应该命中缓存)
        engine.call_count = 0
        tree2 = etree.fromstring(html)
        start_time = time.time()
        await processor.process_tree(tree2)
        second_duration = time.time() - start_time
        
        self.assertEqual(engine.call_count, 0)
        self.assertLess(second_duration, first_duration)
        print(f"First duration: {first_duration:.4f}s, Second duration: {second_duration:.4f}s")
        
        if os.path.exists(db_path):
            os.remove(db_path)

if __name__ == "__main__":
    unittest.main()
