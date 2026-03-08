"""SRT subtitle translation handler built on top of shared base processing."""

import os
import re
from typing import List, Optional
from .base_processor import BaseProcessor
from .batch_processor import BatchProcessor
from .cache import TranslationCache
from .standalone_utils import logger


class SrtHandler(BaseProcessor):
    """Handles SRT subtitle files by inheriting robust translation logic."""

    def __init__(
        self,
        engine,
        cache=None,
        batch_processor=None,
        bilingual=True,
        concurrency_limit=5,
    ):
        cache = cache if cache is not None else TranslationCache()
        batch_processor = (
            batch_processor if batch_processor is not None else BatchProcessor()
        )
        super().__init__(engine, cache, batch_processor, bilingual, concurrency_limit)

    def parse_srt(self, content: str):
        """Parses SRT content into list of blocks."""
        # 分割字幕块：通常是双换行符
        blocks = re.split(r"\n\s*\n", content.strip())
        return blocks

    async def process_file(self, input_path: str, output_path: str) -> bool:
        logger.info(f"Processing SRT: {input_path}")
        try:
            with open(input_path, "r", encoding="utf-8") as f:
                content = f.read()

            blocks = self.parse_srt(content)
            items_to_translate = []
            block_meta = []  # 记录索引和时间戳

            for block in blocks:
                lines = block.split("\n")
                if len(lines) >= 3:
                    index = lines[0]
                    timestamp = lines[1]
                    text = " ".join(lines[2:])
                    items_to_translate.append(text)
                    block_meta.append((index, timestamp))

            if not items_to_translate:
                return True

            # 调用基类分治翻译
            translations = await self.smart_translate_batch(items_to_translate)

            result_blocks = []
            for i, trans in enumerate(translations):
                idx, ts = block_meta[i]
                original = items_to_translate[i]

                # 即使翻译失败，基类也会返回 None，我们在这里安全处理
                final_text = trans if trans else original

                if self.bilingual:
                    block_content = f"{idx}\n{ts}\n{original}\n{final_text}"
                else:
                    block_content = f"{idx}\n{ts}\n{final_text}"
                result_blocks.append(block_content)

            with open(output_path, "w", encoding="utf-8") as f:
                f.write("\n\n".join(result_blocks))

            return not self.has_errors
        except Exception as e:
            logger.error(f"SRT processing failed: {e}")
            return False
