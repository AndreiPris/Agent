#!/usr/bin/env python3
"""
Simple Interactive Test for XOFlowers AI Agent
Tests the action handler directly without needing platform-specific credentials
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from intelligence.action_handler import ActionHandler
from intelligence.intent_classifier import IntentClassifier
from intelligence.product_search import ProductSearchEngine

def main():
    print("🌸 XOFlowers AI Agent - Interactive Test")
    print("=" * 50)
    
    # Initialize components
    try:
        print("📋 Initializing components...")
        handler = ActionHandler()
        print("✅ ActionHandler initialized")
        
        print("🌺 Ready to test! Type 'quit' to exit.")
        print("💬 Try messages like:")
        print("  - 'vreau trandafiri roșii'")
        print("  - 'flori pentru mama'")
        print("  - 'caut ceva romantic'")
        print("  - 'ce program aveți?'")
        print("  - 'bună ziua'")
        print("-" * 50)
        
        user_id = "test_user_123"
        
        while True:
            try:
                message = input("\n🗣️ You: ").strip()
                
                if message.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 La revedere!")
                    break
                    
                if not message:
                    continue
                
                print("🤖 Bot is thinking...")
                response, intent, confidence = handler.handle_message(message, user_id)
                
                print(f"\n📊 Intent: {intent} (confidence: {confidence:.2f})")
                print(f"🌸 Bot: {response}")
                
            except KeyboardInterrupt:
                print("\n\n👋 La revedere!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
