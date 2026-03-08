"""Public package exports for the Transia standalone project."""

from .translation_service import TranslationService
from .standalone_engines import DeepSeekEngine, OpenAICompatibleEngine, GoogleFreeEngine, AnthropicCompatibleEngine
from .standalone_utils import ConfigurationManager

__version__ = "2.1.0"
__all__ = ["TranslationService", "DeepSeekEngine", "OpenAICompatibleEngine", "GoogleFreeEngine", "AnthropicCompatibleEngine", "ConfigurationManager"]
