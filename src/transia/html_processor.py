"""HTML/NCX content translation processor with glossary and context hooks."""

import os
import asyncio
import json
from lxml import etree
from .base_processor import BaseProcessor
from .standalone_utils import logger, trim
from .cache import TranslationCache
from .batch_processor import BatchProcessor

class HtmlProcessor(BaseProcessor):
    HEADING_TAGS = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'title']
    TRANSLATABLE_TAGS = [
        'p', 'li', 'td', 'th', 'caption', 'span', 'blockquote', 'cite', 
        'dd', 'dt', 'section', 'article', 'div', 'text'
    ] + HEADING_TAGS

    def __init__(self, engine, cache=None, batch_processor=None, bilingual=True, concurrency_limit=5):
        cache = cache if cache is not None else TranslationCache()
        batch_processor = batch_processor if batch_processor is not None else BatchProcessor()
        super().__init__(engine, cache, batch_processor, bilingual, concurrency_limit)
        self.summarize_enabled = False
        self.notes_enabled = False
        self.notes_file = None
        self.use_cache = True
        self._chapter_texts = []

    async def process_tree(self, tree, is_xml=False) -> bool:
        self._chapter_texts = []
        xpath_query = " | ".join([f"//*[local-name()='{tag}']" for tag in self.TRANSLATABLE_TAGS])
        elements = tree.xpath(xpath_query)
        
        items_to_translate = []
        el_map = []
        
        for el in elements:
            if el.get("class") == "translated" or el.xpath(".//span[@class='translated']"): continue
            children = el.getchildren()
            if any(child.tag.split('}')[-1] in self.TRANSLATABLE_TAGS and len(trim("".join(child.itertext()))) > 5 for child in children): continue
            texts = [t for t in el.xpath(".//text()[not(parent::span[@class='translated'])]")]
            original_text = trim("".join(texts))
            if len(original_text) > 1 and any(c.isalnum() for c in original_text):
                items_to_translate.append(original_text)
                el_map.append(el)
                self._chapter_texts.append(original_text)

        if not items_to_translate: return True

        all_translations = await self.smart_translate_batch(items_to_translate)
        
        for i, el in enumerate(el_map):
            if i >= len(all_translations): break
            trans = all_translations[i]
            if trans is None: continue
            
            tag_name = el.tag.split('}')[-1]
            if self.bilingual:
                if is_xml or tag_name in ['title', 'text']:
                    original = (el.text or "").strip()
                    el.text = f"{original}  /  {trans}" if original else trans
                else:
                    span = etree.Element("span")
                    span.set("class", "translated")
                    indent = "2em" if tag_name not in self.HEADING_TAGS else "0"
                    span.set("style", f"display: block; text-indent: {indent}; color: #555; font-size: 0.9em; margin-top: 0.5em; border-left: 2px solid #eee; padding-left: 0.5em;")
                    span.text = trans
                    el.append(span)
            else:
                el.clear()
                el.text = trans
        
        if self._chapter_texts:
            full_text = "\n".join(self._chapter_texts)
            valid_trans = "\n".join([t for t in all_translations if t])
            if self.summarize_enabled:
                summary = await self.engine.generate_summary(full_text)
                self.engine.background = f"{getattr(self.engine, 'background', '')}\n\nPrevious: {summary}".strip()
            
            if self.notes_enabled and self.notes_file:
                notes = await self.engine.generate_translator_notes(full_text, valid_trans)
                if notes:
                    with open(self.notes_file, "a", encoding="utf-8") as f:
                        f.write(f"\n\n---\n\n### Chapter Notes\n\n{notes}")

        return not self.has_errors

    async def process_file(self, file_path) -> bool:
        self.has_errors = False
        is_ncx = file_path.lower().endswith('.ncx')
        parser = etree.XMLParser(recover=True, remove_blank_text=False) if is_ncx else etree.HTMLParser(encoding='utf-8')
        try:
            tree = etree.parse(file_path, parser)
            success = await self.process_tree(tree, is_xml=is_ncx)
            with open(file_path, "wb") as f:
                f.write(etree.tostring(tree, encoding='utf-8', method="xml", xml_declaration=is_ncx))
            return success
        except Exception as e:
            logger.error(f"Failed to process {file_path}: {e}")
            return False
