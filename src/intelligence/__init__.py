"""
XOFlowers Intelligence Module
Contains the core AI logic, intent classification, and product search
"""

from .intent_classifier import IntentClassifier
from .product_search import ProductSearchEngine
from .action_handler import ActionHandler

__all__ = ['IntentClassifier', 'ProductSearchEngine', 'ActionHandler']
