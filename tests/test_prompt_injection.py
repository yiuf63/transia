import unittest
import json
from transia.standalone_engines import OpenAICompatibleEngine
from unittest.mock import patch

class TestPromptInjection(unittest.TestCase):
    def test_background_injection(self):
        config = {
            "api_key": "test",
            "model": "gpt-3.5",
            "endpoint": "http://test.com"
        }
        engine = OpenAICompatibleEngine(target_lang="zh", config=config)
        
        # 注入背景信息
        background = "This book is about a girl named Alice in a magical land."
        engine.set_background(background)
        
        body = engine.get_body("Down the rabbit hole.")
        
        # 验证 System Prompt 中包含背景信息
        system_msg = body["messages"][0]["content"]
        self.assertIn("Context:", system_msg)
        self.assertIn(background, system_msg)
        self.assertIn(background, system_msg)
        
        print(f"Constructed System Prompt: {system_msg}")

if __name__ == "__main__":
    unittest.main()
