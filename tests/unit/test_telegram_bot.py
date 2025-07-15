#!/usr/bin/env python3
"""
Test script to verify the Telegram bot can be initialized without actually starting
"""
import os
import sys
sys.path.insert(0, '.')

from dotenv import load_dotenv
load_dotenv()

# Set a dummy token for testing
os.environ['TELEGRAM_BOT_TOKEN'] = 'dummy_token_for_testing'

try:
    from src.api.telegram_app import XOFlowersTelegramBot
    
    print("🧪 Testing Telegram Bot Initialization...")
    
    # Test that we can create the bot object
    try:
        bot = XOFlowersTelegramBot(debug=True)
        print("✅ Bot object created successfully")
        print(f"✅ Bot token configured: {bot.token[:20]}...")
        print(f"✅ Debug mode: {bot.debug}")
        print(f"✅ Application configured: {bot.application is not None}")
        
        # Test that AI components are initialized
        assert hasattr(bot, 'intent_classifier'), "Intent classifier should be initialized"
        assert hasattr(bot, 'action_handler'), "Action handler should be initialized"
        assert hasattr(bot, 'context_manager'), "Context manager should be initialized"
        assert hasattr(bot, 'security_filter'), "Security filter should be initialized"
        print("✅ All AI components initialized")
        
        # Test that handlers are set up
        assert len(bot.application.handlers) > 0, "Handlers should be configured"
        print(f"✅ Handlers configured: {len(bot.application.handlers)} handler groups")
        
        print("\n🎉 Telegram Bot Structure Test PASSED!")
        print("📝 The bot is ready to run with a real Telegram token.")
        
    except Exception as e:
        print(f"❌ Bot initialization failed: {e}")
        
except Exception as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()
