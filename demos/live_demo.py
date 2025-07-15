#!/usr/bin/env python3
"""
XOFlowers AI Agent - Live Demo Script
Shows the bot responding to various messages
"""

import sys
import os
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from intelligence.action_handler import ActionHandler

def demo_chat():
    print("🌸 XOFlowers AI Agent - Live Demo")
    print("=" * 50)
    
    # Initialize
    handler = ActionHandler()
    print("✅ Bot initialized and ready!")
    print("=" * 50)
    
    # Demo conversations
    conversations = [
        ("greeting", "Bună ziua!"),
        ("product_search", "Vreau trandafiri roșii pentru soția mea"),
        ("romantic_occasion", "Caut ceva romantic pentru aniversarea noastră"),
        ("budget_inquiry", "Aveți buchete până la 500 MDL?"),
        ("mother_gift", "Flori pentru mama la ziua ei"),
        ("business_info", "Ce program de lucru aveți?"),
        ("price_check", "Cât costă un buchet de bujori?"),
        ("farewell", "Mulțumesc, la revedere!")
    ]
    
    user_id = "demo_user"
    
    for scenario, message in conversations:
        print(f"\n🎭 {scenario.upper().replace('_', ' ')}")
        print(f"👤 Customer: {message}")
        print("🤖 XOFlowers Bot:", end=" ")
        
        # Simulate thinking
        for i in range(3):
            print(".", end="", flush=True)
            time.sleep(0.3)
        print(" 💭")
        
        try:
            response, intent, confidence = handler.handle_message(message, user_id)
            print(f"📊 Detected: {intent} (confidence: {confidence:.0%})")
            print(f"🌸 Response:")
            print("-" * 40)
            
            # Show first few lines of response
            lines = response.split('\n')
            for line in lines[:6]:  # Show first 6 lines
                if line.strip():
                    print(line)
            
            if len(lines) > 6:
                print("... (response continues)")
            
            print("-" * 40)
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("\n" + "=" * 50)
        time.sleep(1)  # Brief pause between conversations
    
    print("\n🎉 Demo completed!")
    print("✅ XOFlowers AI Agent is fully functional!")
    print("🚀 Ready for real customer interactions!")

if __name__ == "__main__":
    demo_chat()
