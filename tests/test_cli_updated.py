import unittest
import re
from unittest.mock import AsyncMock, patch

from typer.testing import CliRunner

from transia.main import app

runner = CliRunner()
ANSI_ESCAPE_RE = re.compile(r"\x1b\[[0-9;]*m")


def strip_ansi(text: str) -> str:
    return ANSI_ESCAPE_RE.sub("", text)


class TestCLIUpdated(unittest.TestCase):
    def test_cli_new_params(self):
        result = runner.invoke(app, ["translate", "--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("--search", strip_ansi(result.stdout))

    def test_cli_parameter_logic(self):
        # 验证命令是否能识别新参数并启动（即使最后因为文件不存在退出）
        result = runner.invoke(app, [
            "translate",
            "non_existent.epub",
            "out.epub",
            "--search"
        ])
        # 如果子命令存在且参数正确，但文件不存在，Typer 会抛出 Argument Error
        self.assertNotEqual(result.exit_code, 0)

    def test_cli_output_extension_mismatch(self):
        with runner.isolated_filesystem():
            with open("book.srt", "w", encoding="utf-8") as file:
                file.write("1\n00:00:00,000 --> 00:00:01,000\nhello")
            result = runner.invoke(app, ["translate", "book.srt", "out.epub"])
            self.assertEqual(result.exit_code, 1)
            self.assertIn("Output extension mismatch", result.stdout + result.stderr)

    def test_cli_no_success_message_when_service_fails(self):
        with runner.isolated_filesystem():
            with open("book.srt", "w", encoding="utf-8") as file:
                file.write("1\n00:00:00,000 --> 00:00:01,000\nhello")
            with patch(
                "transia.main.TranslationService.translate",
                new=AsyncMock(return_value=False)
            ):
                result = runner.invoke(app, ["translate", "book.srt", "out.srt"])
            self.assertEqual(result.exit_code, 1)
            output = result.stdout + result.stderr
            self.assertIn("Translation failed", output)
            self.assertNotIn("Success! Saved", output)
