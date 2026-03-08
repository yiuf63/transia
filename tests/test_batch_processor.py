import unittest
from transia.batch_processor import BatchProcessor

class TestBatchProcessor(unittest.TestCase):
    def setUp(self):
        # 将阈值设得非常小，以确保触发分割
        self.processor = BatchProcessor(max_batch_chars=10, separator="\n---\n")

    def test_create_batches(self):
        items = ["Longer line 1", "Longer line 2"]
        batches = self.processor.create_batches(items)
        self.assertGreater(len(batches), 1)

    def test_split_translation(self):
        translated_batch = "翻译 1\n---\n翻译 2"
        results, success = self.processor.split_batch(translated_batch, expected_count=2)
        self.assertTrue(success)
        self.assertEqual(len(results), 2)

    def test_split_mismatch(self):
        translated_batch = "翻译 1\n---\n翻译 2\n---\n翻译 3"
        results, success = self.processor.split_batch(translated_batch, expected_count=2)
        self.assertFalse(success)
        self.assertEqual(len(results), 3)
