import unittest
from transia.standalone_engines import OpenAICompatibleEngine

class TestGlossaryInjection(unittest.TestCase):
    def test_glossary_prompt_injection(self):
        engine = OpenAICompatibleEngine(target_lang="zh", config={"api_key": "test", "endpoint": "test"})
        
        glossary = {
            "Alice": "爱丽丝 (Wonderland Explorer)",
            "Rabbit": "大兔子"
        }
        if hasattr(engine, 'set_glossary'):
            engine.set_glossary(glossary)
        
            # 获取 Body
            body = engine.get_body("Alice followed the Rabbit.")
            system_content = body["messages"][0]["content"]
            
            # 验证术语是否在 Prompt 中
            self.assertIn("Glossary", system_content)
            self.assertIn("Alice", system_content)
            self.assertIn("爱丽丝", system_content)
            self.assertIn("大兔子", system_content)
            print(f"Injected System Prompt:\n{system_content}")
        else:
            self.fail("Engine does not have set_glossary method")

if __name__ == "__main__":
    unittest.main()