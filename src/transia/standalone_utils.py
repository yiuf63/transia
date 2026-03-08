"""Shared utility helpers: config, logging, hashing, and HTTP requests."""

import os
import json
import logging
import hashlib
import httpx
import urllib.parse
from mechanize import Browser
import ssl

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger("Translator")

class ConfigurationManager:
    def __init__(self, config_path="config.json"):
        self.config_path = config_path
        self.config = self.load()

    def load(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def save(self):
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=4)

    def get(self, key, default=None):
        return self.config.get(key, default)

    def set(self, key, value):
        self.config[key] = value
        self.save()

    def get_profile(self, profile_name):
        """Returns engine configuration for a given profile."""
        profiles = self.get("profiles", {})
        return profiles.get(profile_name)

def uid(*args):
    md5 = hashlib.md5()
    for arg in args:
        md5.update(arg if isinstance(arg, bytes) else arg.encode('utf-8'))
    return md5.hexdigest()

def get_file_hash(file_path):
    """Calculates MD5 hash of a file."""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def trim(text):
    if not text: return ""
    # 移除 BOM (\ufeff) 和其他不可见字符
    text = text.replace('\ufeff', '').replace('\u00a0', ' ')
    return " ".join(text.split())

def request(url, data=None, headers={}, method='GET', timeout=30):
    br = Browser()
    br.set_handle_robots(False)
    # 增加鲁棒性：忽略 SSL 证书错误
    try:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        br.set_ca_data(context=ssl_context)
    except Exception:
        pass

    for k, v in headers.items():
        br.addheaders = [(k, v)]
    
    try:
        if method.upper() == 'GET' and data:
            url = f"{url}?{urllib.parse.urlencode(data)}"
            response = br.open(url, timeout=timeout)
        elif method.upper() == 'POST':
            response = br.open(url, data=data, timeout=timeout)
        else:
            response = br.open(url, timeout=timeout)
        return response.read().decode('utf-8')
    except Exception as e:
        logger.error(f"Sync request failed: {e}")
        return ""

def load_glossary(file_path):
    glossary = {}
    if not file_path or not os.path.exists(file_path):
        return glossary
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or ":" not in line:
                    continue
                parts = line.split(":", 1)
                orig = parts[0].strip()
                trans = parts[1].strip()
                if orig and trans:
                    glossary[orig] = trans
        logger.info(f"Loaded {len(glossary)} glossary terms from {file_path}")
    except Exception as e:
        logger.error(f"Failed to load glossary: {e}")
    return glossary

async def async_request(url, data=None, headers={}, method='GET', timeout=30, proxy_uri=None):
    async with httpx.AsyncClient(timeout=timeout, proxy=proxy_uri) as client:
        try:
            if method.upper() == 'GET' and data:
                response = await client.request(method, url, params=data, headers=headers)
            else:
                response = await client.request(method, url, data=data, headers=headers)
            response.raise_for_status()
            return response.text.strip()
        except Exception as e:
            logger.error(f"Async request failed: {e}")
            return ""
