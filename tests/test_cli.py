import unittest
from typer.testing import CliRunner
from transia.main import app

runner = CliRunner()

class TestCLI(unittest.TestCase):
    def test_cli_help(self):
        result = runner.invoke(app, ["--help"])
        self.assertEqual(result.exit_code, 0)
        # 验证子命令描述
        self.assertIn("Translate an ebook", result.stdout)

    def test_cli_invalid_file(self):
        result = runner.invoke(app, ["nonexistent.epub", "out.epub"])
        self.assertNotEqual(result.exit_code, 0)
        # Note: Typer might print errors to stderr depending on configuration
        # CliRunner captures stdout by default. 
        # Using a more direct check or allowing mix_stderr
        result = runner.invoke(app, ["nonexistent.epub", "out.epub"])
        self.assertNotEqual(result.exit_code, 0)

if __name__ == "__main__":
    unittest.main()
