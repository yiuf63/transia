"""SQLite-backed translation cache and processed-file tracking."""

import sqlite3
import hashlib
import os
from .standalone_utils import logger

class TranslationCache:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(TranslationCache, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, db_path="translations.db"):
        # 允许通过初始化改变 db_path (仅用于测试)
        if hasattr(self, '_initialized') and self._initialized and self.db_path == db_path:
            return
            
        self.db_path = db_path
        self._init_db()
        self._initialized = True

    def _init_db(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS cache (
                        key TEXT PRIMARY KEY,
                        original_text TEXT,
                        translated_text TEXT,
                        engine TEXT,
                        target_lang TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS file_status (
                        file_path TEXT PRIMARY KEY,
                        file_hash TEXT,
                        target_lang TEXT,
                        status TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_lang_engine ON cache(target_lang, engine)')
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")

    def _get_key(self, text, engine, target_lang, glossary_hash=""):
        content = f"{text}|{engine}|{target_lang}|{glossary_hash}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()

    def get(self, text, engine, target_lang, glossary_hash=""):
        key = self._get_key(text, engine, target_lang, glossary_hash)
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT translated_text FROM cache WHERE key = ?", (key,))
                row = cursor.fetchone()
                return row[0] if row else None
        except Exception:
            return None

    def set(self, text, translated_text, engine, target_lang, glossary_hash=""):
        if not translated_text: return
        key = self._get_key(text, engine, target_lang, glossary_hash)
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO cache (key, original_text, translated_text, engine, target_lang) VALUES (?, ?, ?, ?, ?)",
                    (key, text, translated_text, engine, target_lang)
                )
        except Exception as e:
            logger.warning(f"Cache write error: {e}")

    def is_file_processed(self, file_name, file_hash, target_lang):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT status FROM file_status WHERE file_path = ? AND file_hash = ? AND target_lang = ?",
                    (file_name, file_hash, target_lang)
                )
                row = cursor.fetchone()
                return row and row[0] == "completed"
        except Exception:
            return False

    def mark_file_processed(self, file_name, file_hash, target_lang):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO file_status (file_path, file_hash, target_lang, status) VALUES (?, ?, ?, ?)",
                    (file_name, file_hash, target_lang, "completed")
                )
        except Exception as e:
            logger.warning(f"Failed to update file status: {e}")

    def update_file_status(self, file_name, file_hash, target_lang):
        return self.mark_file_processed(file_name, file_hash, target_lang)
