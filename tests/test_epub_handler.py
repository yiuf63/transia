import unittest
import os
import shutil
from transia.epub_handler import EpubHandler

class TestEpubHandler(unittest.TestCase):
    def setUp(self):
        self.epub_path = "tests/alice.epub"
        self.output_path = "tests/alice_out.epub"
        self.handler = EpubHandler(self.epub_path)

    def tearDown(self):
        if hasattr(self.handler, 'temp_dir') and os.path.exists(self.handler.temp_dir):
            shutil.rmtree(self.handler.temp_dir)
        if os.path.exists(self.output_path):
            os.remove(self.output_path)

    def test_parse_structure(self):
        # 1. 解压并解析
        self.handler.extract()
        opf_path = self.handler.get_opf_path()
        self.assertTrue(os.path.exists(opf_path))
        
        # 2. 获取 HTML 文件列表
        html_files = self.handler.get_html_files()
        self.assertGreater(len(html_files), 0)
        self.assertTrue(any(f.endswith('.xhtml') or f.endswith('.html') for f in html_files))
        
        print(f"Found OPF: {opf_path}")
        print(f"Found {len(html_files)} HTML files.")

if __name__ == "__main__":
    unittest.main()
