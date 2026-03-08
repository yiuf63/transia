"""Translation engine implementations for multiple LLM and MT providers."""

import os
import json
import re
import asyncio
import urllib.parse
from .standalone_utils import logger, request, async_request

class StandaloneBaseEngine:
    def __init__(self, source_lang='auto', target_lang='zh', config=None):
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.config = config if config else {}
        self.api_key = self.config.get('api_key')
        self.glossary = {}
        self.method = 'GET'
        self.background = ""

    def set_glossary(self, glossary): self.glossary = glossary
    def set_background(self, background): self.background = background

    def get_endpoint(self): return ""
    def get_body(self, text): return {}
    def get_headers(self): return {}
    def get_result(self, response): return response

    async def async_translate(self, text):
        try:
            url = self.get_endpoint()
            body = self.get_body(text)
            headers = self.get_headers()
            if self.method == 'GET' and isinstance(body, dict):
                response = await async_request(url, data=body, headers=headers, method=self.method)
            else:
                if isinstance(body, (dict, list)): body = json.dumps(body)
                response = await async_request(url, data=body, headers=headers, method=self.method)
            return self.get_result(response)
        except Exception as e:
            logger.error(f"Async translation error: {e}")
            return text

    async def generate_summary(self, text): return text[:200] + "..." if len(text) > 200 else text
    async def extract_terms(self, original_text, translated_text): return {}
    async def generate_translator_notes(self, original_text, translated_text): return ""

class GoogleFreeEngine(StandaloneBaseEngine):
    def get_endpoint(self): return "https://translate.googleapis.com/translate_a/single"
    def get_body(self, text): return {"client": "gtx", "sl": self.source_lang, "tl": self.target_lang, "dt": "t", "q": text}
    def get_result(self, response):
        try:
            data = json.loads(response)
            return "".join([part[0] for part in data[0] if part[0]])
        except Exception: return ""

class OpenAICompatibleEngine(StandaloneBaseEngine):
    def __init__(self, source_lang='auto', target_lang='zh', config=None):
        super().__init__(source_lang, target_lang, config)
        self.method = 'POST'
        if not self.api_key: self.api_key = os.environ.get('OPENAI_API_KEY')
        self.model = self.config.get('model', 'gpt-3.5-turbo')
        self.endpoint = self.config.get('endpoint', 'https://api.openai.com/v1/chat/completions')
        self.system_prompt = self.config.get('system_prompt', 
            "You are an expert literary translator. Your translation should be fluent, natural, and idiomatic, as if it were originally written in the target language."
        )

    def get_endpoint(self): return self.endpoint
    def get_headers(self): return {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

    def _create_body(self, messages, temperature=0.3):
        return {"model": self.model, "messages": messages, "temperature": temperature}

    def get_body(self, text):
        glossary_str = "\n".join([f"{k}: {v}" for k, v in self.glossary.items()])
        full_system = f"{self.system_prompt}"
        if self.background: full_system += f"\n\nContext:\n{self.background}"
        if glossary_str: full_system += f"\n\nGlossary:\n{glossary_str}"
        return self._create_body([
            {"role": "system", "content": full_system},
            {"role": "user", "content": f"Translate to {self.target_lang}, output translation only:\n\n{text}"}
        ])

    def get_result(self, response):
        try:
            data = json.loads(response)
            return data['choices'][0]['message']['content'].strip()
        except Exception: return ""

    async def generate_summary(self, text):
        prompt = f"Summarize the following chapter content: {text[:2000]}"
        body = self.get_body(prompt)
        try: return await self.async_translate(prompt)
        except Exception: return ""

    async def extract_terms(self, original_text, translated_text):
        prompt = (f"Extract key proper nouns from this text and translation as a JSON object {{original: translation}}."
                  f"\n\nOriginal: {original_text[:2000]}\n\nTranslation: {translated_text[:2000]}")
        body = self.get_body(prompt)
        try:
            response = await self.async_translate(prompt)
            match = re.search(r'\{.*\}', response, re.DOTALL)
            if match: return json.loads(match.group())
            return json.loads(response)
        except Exception: return {}

    async def generate_translator_notes(self, original_text, translated_text):
        prompt = (
            "You are a cultural commentator. Compare the original text with its translation. "
            "Identify idioms, cultural references, or historical contexts that the target audience might miss. "
            "For each, provide a brief translator's note. Format as Markdown. If no notes needed, output 'None'."
            f"\n\nOriginal:\n'''{original_text}'''\n\nTranslation:\n'''{translated_text}'''"
        )
        body = self.get_body(prompt)
        try:
            notes = await self.async_translate(prompt)
            return notes if "none" not in notes.lower() else ""
        except Exception: return ""

class DeepSeekEngine(OpenAICompatibleEngine): # ... (rest of the code)
    pass
class AnthropicCompatibleEngine(StandaloneBaseEngine): # ... (rest of the code)
    pass
