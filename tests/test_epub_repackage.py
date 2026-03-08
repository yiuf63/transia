import unittest
import os
import shutil
import zipfile
from transia.epub_handler import EpubHandler

class TestEpubRepackage(unittest.TestCase):
    def setUp(self):
        self.epub_path = "tests/alice.epub"
        self.output_path = "tests/alice_repacked.epub"
        self.handler = EpubHandler(self.epub_path)

    def tearDown(self):
        self.handler.cleanup()
        if os.path.exists(self.output_path):
            os.remove(self.output_path)

    def test_repackage(self):
        self.handler.extract()
        html_files = self.handler.get_html_files()
        target_file = html_files[0]
        
        # 1. Modify a file
        with open(target_file, "a") as f:
            f.write("<!-- MODIFIED -->")
            
        # 2. Save
        self.handler.save(self.output_path)
        self.assertTrue(os.path.exists(self.output_path))
        
        # 3. Verify mimetype is first and uncompressed
        with zipfile.ZipFile(self.output_path, 'r') as z:
            info = z.getinfo('mimetype')
            self.assertEqual(info.compress_type, zipfile.ZIP_STORED)
            self.assertEqual(z.namelist()[0], 'mimetype')
            
            # 4. Check modification
            rel_path = os.path.relpath(target_file, self.handler.temp_dir)
            content = z.read(rel_path).decode('utf-8')
            self.assertIn("<!-- MODIFIED -->", content)

if __name__ == "__main__":
    unittest.main()
