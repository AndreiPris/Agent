"""
XOFlowers AI Agent - Main Source Package
Instagram AI Agent for XOFlowers built with ChromaDB + LLMs
"""

from .api import TelegramApp, InstagramApp
from .intelligence import IntentClassifier, ActionHandler, ProductSearchEngine
from .pipeline import XOFlowersScraper, ChromaDBPopulator
from .security import SecurityFilter

__version__ = "2.0.0"
__all__ = ['TelegramApp', 'InstagramApp', 'IntentClassifier', 'ActionHandler', 'ProductSearchEngine', 'XOFlowersScraper', 'ChromaDBPopulator', 'SecurityFilter']
