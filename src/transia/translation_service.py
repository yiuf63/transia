"""Top-level translation orchestration service and event dispatch."""

import os
import asyncio
from enum import Enum
from typing import Optional, Callable, Dict, Any, Union
from .epub_handler import EpubHandler
from .html_processor import HtmlProcessor
from .srt_handler import SrtHandler
from .batch_processor import BatchProcessor
from .standalone_engines import GoogleFreeEngine, DeepSeekEngine, OpenAICompatibleEngine, AnthropicCompatibleEngine
from .standalone_utils import get_file_hash, logger
from .cache import TranslationCache

class TransiaEvent(Enum):
    PROGRESS = "on_progress"
    LOG = "on_log"
    TERM_LEARNED = "on_term_learned"

class TranslationService:
    def __init__(self, profile_data: dict, target_lang: str = "zh"):
        self.target_lang = target_lang
        self.profile = profile_data
        self.engine = self._init_engine()
        self.cache = TranslationCache()
        self.batch_processor = BatchProcessor(max_batch_chars=1500)
        self.callbacks: Dict[TransiaEvent, Optional[Callable]] = {e: None for e in TransiaEvent}

    def _init_engine(self) -> Union[GoogleFreeEngine, DeepSeekEngine, OpenAICompatibleEngine, AnthropicCompatibleEngine]:
        engine_name = self.profile.get("engine", "google").lower()
        if engine_name == "deepseek": return DeepSeekEngine(target_lang=self.target_lang, config=self.profile)
        if engine_name == "openai": return OpenAICompatibleEngine(target_lang=self.target_lang, config=self.profile)
        if engine_name == "anthropic": return AnthropicCompatibleEngine(target_lang=self.target_lang, config=self.profile)
        return GoogleFreeEngine(target_lang=self.target_lang, config=self.profile)

    def subscribe(self, event: TransiaEvent, callback: Callable) -> None: self.callbacks[event] = callback
    def _emit(self, event: TransiaEvent, *args, **kwargs) -> None:
        if cb := self.callbacks.get(event):
            if asyncio.iscoroutinefunction(cb): asyncio.create_task(cb(*args, **kwargs))
            else: cb(*args, **kwargs)

    async def translate(self, input_path: str, output_path: str, options: Dict[str, Any]) -> bool:
        ext = os.path.splitext(input_path)[1].lower()
        concurrency = options.get("concurrency", 5)
        
        notes_path = options.get("notes_path")
        if notes_path and os.path.exists(notes_path):
            os.remove(notes_path) # 清空旧注释
        
        def progress_bridge(curr, total, msg): self._emit(TransiaEvent.PROGRESS, curr, total, msg)

        if ext == ".epub":
            epub_handler = EpubHandler(input_path)
            epub_handler.extract()
            processor = HtmlProcessor(self.engine, self.cache, self.batch_processor, bilingual=options.get("bilingual", True), concurrency_limit=concurrency)
            processor.summarize_enabled = options.get("summarize", False)
            processor.notes_enabled = bool(notes_path)
            processor.notes_file = notes_path
            processor.on_progress = progress_bridge
            
            all_success = True
            for i, f in enumerate(epub_handler.get_html_files()):
                rel_path = os.path.relpath(f, epub_handler.temp_dir)
                file_hash = get_file_hash(f)
                if self.cache.is_file_processed(rel_path, file_hash, self.target_lang):
                    self._emit(TransiaEvent.LOG, f"Skipping: {rel_path}")
                    continue
                if not await processor.process_file(f): all_success = False
                else: self.cache.mark_file_processed(rel_path, file_hash, self.target_lang)
                self._emit(TransiaEvent.TERM_LEARNED, self.engine.glossary)
            
            epub_handler.save(output_path)
            epub_handler.cleanup()
            return all_success
            
        elif ext == ".srt":
            srt_handler = SrtHandler(self.engine, self.cache, self.batch_processor, bilingual=options.get("bilingual", True), concurrency_limit=concurrency)
            srt_handler.on_progress = progress_bridge
            return await srt_handler.process_file(input_path, output_path)
        return False
