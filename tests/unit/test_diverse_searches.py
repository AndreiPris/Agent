#!/usr/bin/env python3
"""
Test the bot with specific flower searches
"""

import sys
import os
sys.path.insert(0, 'src')

from dotenv import load_dotenv
load_dotenv()

from api.telegram_app import XOFlowersTelegramBot

def test_diverse_searches():
    print("🌸 Testing XOFlowers Bot with Diverse Searches")
    print("=" * 60)
    
    # Initialize bot
    bot = XOFlowersTelegramBot(debug=True)
    
    # Test various searches
    test_cases = [
        "Vreau trandafiri roșii",
        "Căut niște bujori",
        "Vreau lăcrimioare",
        "Am nevoie de flori pentru nuntă",
        "Vreau ceva elegant pentru mama",
        "Căut flori pentru aniversare",
        "Vreau un buchet de primăvară",
        "Am nevoie de ceva luxury",
        "Vreau flori pentru director",
        "Căut un cadou special"
    ]
    
    for i, query in enumerate(test_cases, 1):
        print(f"\\n{i}. Testing: '{query}'")
        print("-" * 40)
        
        try:
            response, intent, confidence = bot.action_handler.handle_message(query, f"test_user_{i}")
            print(f"Intent: {intent} (confidence: {confidence:.2f})")
            print(f"Response preview: {response[:200]}...")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_diverse_searches()
