import unittest
import os
import json
from transia.standalone_utils import ConfigurationManager

class TestConfigurationManager(unittest.TestCase):
    def setUp(self):
        self.config_file = "test_config.json"
        if os.path.exists(self.config_file):
            os.remove(self.config_file)

    def tearDown(self):
        if os.path.exists(self.config_file):
            os.remove(self.config_file)

    def test_load_empty(self):
        config = ConfigurationManager(self.config_file)
        self.assertEqual(config.config, {})

    def test_load_from_file(self):
        with open(self.config_file, "w") as f:
            json.dump({"profiles": {"test": {"engine": "google"}}}, f)
        
        config = ConfigurationManager(self.config_file)
        self.assertEqual(config.get_profile("test")["engine"], "google")

    def test_set_and_save(self):
        config = ConfigurationManager(self.config_file)
        config.set("app_name", "transia")
        
        # 验证是否保存到文件
        with open(self.config_file, 'r') as f:
            data = json.load(f)
            self.assertEqual(data["app_name"], "transia")
