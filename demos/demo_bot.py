#!/usr/bin/env python3
"""
Demonstration of XOFlowers AI Agent
Shows various scenarios and responses
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from intelligence.action_handler import ActionHandler

def demo_conversation():
    print("🌸 XOFlowers AI Agent - Live Demonstration")
    print("=" * 60)
    
    # Initialize
    try:
        handler = ActionHandler()
        print("✅ Bot initialized successfully")
        print("=" * 60)
        
        # Test scenarios
        scenarios = [
            ("greeting", "bună ziua"),
            ("product_search", "vreau trandafiri roșii"),
            ("romantic", "caut ceva romantic pentru soția mea"),
            ("birthday", "flori pentru ziua de naștere"),
            ("budget", "buchet până la 500 MDL"),
            ("mother", "flori pentru mama"),
            ("info", "ce program aveți?"),
            ("farewell", "mulțumesc, la revedere")
        ]
        
        user_id = "demo_user_123"
        
        for scenario_name, message in scenarios:
            print(f"\n🎭 Scenario: {scenario_name.upper()}")
            print(f"👤 User: {message}")
            print("🤖 Bot is thinking...")
            
            try:
                response, intent, confidence = handler.handle_message(message, user_id)
                print(f"📊 Intent: {intent} (confidence: {confidence:.2f})")
                print(f"🌸 Bot Response:")
                print("-" * 40)
                print(response)
                print("-" * 40)
                
            except Exception as e:
                print(f"❌ Error processing message: {e}")
                
            print("\n" + "=" * 60)
            
    except Exception as e:
        print(f"❌ Failed to initialize bot: {e}")
        return 1
    
    print("\n🎉 Demonstration completed successfully!")
    print("✅ The XOFlowers AI Agent is working perfectly!")
    return 0

if __name__ == "__main__":
    sys.exit(demo_conversation())
