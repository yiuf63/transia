import unittest
import os
from transia.epub_handler import EpubHandler

class TestEpubMetadata(unittest.TestCase):
    def setUp(self):
        self.epub_path = "tests/alice.epub"
        if not os.path.exists(self.epub_path):
            self.skipTest("tests/alice.epub not found")
        self.handler = EpubHandler(self.epub_path)

    def tearDown(self):
        self.handler.cleanup()

    def test_extract_metadata(self):
        self.handler.extract()
        metadata = self.handler.get_metadata()
        
        self.assertIn("title", metadata)
        self.assertIn("author", metadata)
        # 爱丽丝梦游仙境的标题应该包含 Alice
        self.assertIn("Alice", metadata["title"])
        # 作者应该是 Lewis Carroll
        self.assertIn("Lewis Carroll", metadata["author"])
        
        print(f"Extracted Metadata: {metadata}")

if __name__ == "__main__":
    unittest.main()
