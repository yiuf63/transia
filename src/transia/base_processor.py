"""Shared translation processing logic used by format-specific handlers."""

import asyncio
from typing import List, Optional, Callable
from .batch_processor import BatchProcessor
from .cache import TranslationCache
from .standalone_utils import logger

class BaseProcessor:
    """Enhanced base class with dependency injection and progress reporting."""
    
    def __init__(self, engine, cache: TranslationCache, batch_processor: BatchProcessor, bilingual=True, concurrency_limit=5):
        self.engine = engine
        self.cache = cache
        self.batch_processor = batch_processor
        self.bilingual = bilingual
        self.on_progress: Optional[Callable] = None
        self._semaphore = asyncio.Semaphore(concurrency_limit)
        self.has_errors = False

    def _report_progress(self, current: int, total: int, message: str):
        if self.on_progress:
            self.on_progress(current, total, message)

    async def translate_item(self, text: str) -> Optional[str]:
        engine_name = self.engine.__class__.__name__
        target_lang = self.engine.target_lang
        
        # 为了测试回调，某些场景可能需要绕过缓存，这里保持逻辑一致
        if getattr(self, 'use_cache', True):
            cached = self.cache.get(text, engine_name, target_lang)
            if cached: return cached
        
        async with self._semaphore:
            try:
                result = await self.engine.async_translate(text)
                if result:
                    self.cache.set(text, result, engine_name, target_lang)
                return result
            except Exception as e:
                logger.error(f"Translation request failed: {e}")
                return None

    async def smart_translate_batch(self, items: List[str]) -> List[Optional[str]]:
        """Translates a list of items, reporting progress if possible."""
        if not items: return []
        
        batch_text = self.batch_processor.separator.join(items)
        
        # 触发进度回调 (这里由于是单文件内的批次，我们简单上报)
        self._report_progress(1, 1, "Translating batches...")
        
        translated_text = await self.translate_item(batch_text)
        
        if translated_text is None:
            if len(items) == 1:
                self.has_errors = True
                return [None]
            return await self._split_and_retry(items)

        results, success = self.batch_processor.split_batch(translated_text, len(items))
        if success:
            safe_results: List[Optional[str]] = [item for item in results]
            return safe_results
        
        if len(items) == 1:
            self.has_errors = True
            return [None]
            
        return await self._split_and_retry(items)

    async def _split_and_retry(self, items: List[str]) -> List[Optional[str]]:
        mid = len(items) // 2
        left = await self.smart_translate_batch(items[:mid])
        right = await self.smart_translate_batch(items[mid:])
        return left + right
