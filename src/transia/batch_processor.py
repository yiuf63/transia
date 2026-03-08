"""Batch creation and split utilities for robust multi-paragraph translation."""

import re
from typing import List, Tuple

class BatchProcessor:
    def __init__(self, max_batch_chars: int = 1500, separator: str = "\n---\n"):
        self.max_batch_chars = max_batch_chars
        self.separator = separator

    def create_batches(self, items: List[str]) -> List[str]:
        batches: List[str] = []
        current_batch: List[str] = []
        current_len = 0
        
        for item in items:
            item_len = len(item)
            if current_batch and (current_len + item_len + len(self.separator)) > self.max_batch_chars:
                batches.append(self.separator.join(current_batch))
                current_batch = []
                current_len = 0
            current_batch.append(item)
            current_len += item_len + len(self.separator)
            
        if current_batch:
            batches.append(self.separator.join(current_batch))
        return batches

    def split_batch(self, translated_text: str, expected_count: int) -> Tuple[List[str], bool]:
        """Splits batch with robust regex to handle inconsistent LLM spacing."""
        if not translated_text:
            return [], False
            
        # 兼容多种可能的换行符和空格组合
        pattern = re.escape(self.separator.strip())
        parts = re.split(fr'\n*\s*{pattern}\s*\n*', translated_text.strip())
        
        # 过滤掉由于末尾分隔符可能产生的空项
        parts = [p.strip() for p in parts if p.strip()]
        
        if len(parts) == expected_count:
            return parts, True
        
        return parts, False
