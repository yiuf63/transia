import unittest
import asyncio
from transia.srt_handler import SrtHandler
from transia.standalone_engines import StandaloneBaseEngine

class MockEngine(StandaloneBaseEngine):
    async def async_translate(self, text):
        return f"译: {text}"

class TestSrtHandler(unittest.IsolatedAsyncioTestCase):
    async def test_srt_translation(self):
        srt_content = """1
00:00:01,000 --> 00:00:04,000
Hello, world!

2
00:00:05,000 --> 00:00:08,000
This is a test.
"""
        input_path = "tests/test.srt"
        output_path = "tests/test_out.srt"
        
        with open(input_path, "w") as f:
            f.write(srt_content)
            
        engine = MockEngine()
        handler = SrtHandler(engine)
        await handler.process_file(input_path, output_path)
        
        with open(output_path, "r") as f:
            result = f.read()
            self.assertIn("Hello, world!", result)
            self.assertIn("译: Hello, world!", result)
            self.assertIn("00:00:05,000 --> 00:00:08,000", result)

if __name__ == "__main__":
    unittest.main()
