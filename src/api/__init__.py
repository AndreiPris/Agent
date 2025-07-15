"""
XOFlowers API Module
Contains API interfaces for Telegram and Instagram platforms
"""

from .telegram_app import XOFlowersTelegramBot as TelegramApp
from .instagram_app import XOFlowersInstagramBot as InstagramApp

__all__ = ['TelegramApp', 'InstagramApp']
