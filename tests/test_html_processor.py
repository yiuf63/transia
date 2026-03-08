import unittest
import asyncio
from transia.html_processor import HtmlProcessor
from transia.standalone_engines import StandaloneBaseEngine
from lxml import etree

class BatchMockEngine(StandaloneBaseEngine):
    async def async_translate(self, text):
        # 模拟 BatchProcessor 的分隔符逻辑
        separator = "\n---\n"
        if separator in text:
            parts = text.split(separator)
            return separator.join([f"译: {p.strip()}" for p in parts])
        return f"译: {text}"

class TestHtmlProcessor(unittest.IsolatedAsyncioTestCase):
    async def test_process_html(self):
        html_content = """
        <html>
            <body>
                <h1>Title</h1>
                <p>Hello world.</p>
            </body>
        </html>
        """
        engine = BatchMockEngine(target_lang="zh")
        processor = HtmlProcessor(engine)
        processor.use_cache = False
    
        tree = etree.fromstring(html_content)
        await processor.process_tree(tree)
    
        # 验证结果
        h1 = tree.xpath("//h1")[0]
        p = tree.xpath("//p")[0]
    
        self.assertEqual(h1.xpath("span[@class='translated']")[0].text, "译: Title")
        self.assertEqual(p.xpath("span[@class='translated']")[0].text, "译: Hello world.")

if __name__ == "__main__":
    unittest.main()
