#!/usr/bin/env python3
"""
Test various conversational scenarios to ensure the bot sounds like a real florist
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from intelligence.action_handler import ActionHandler

def test_various_scenarios():
    """Test various conversational scenarios"""
    
    print("=== Testing Various Conversational Scenarios ===\n")
    
    # Initialize the action handler
    handler = ActionHandler()
    
    # Test cases
    test_cases = [
        {
            "message": "vreau ceva romantic pentru soția mea",
            "context": "Romantic for wife",
            "expected": "Should be warm, romantic, marriage-appropriate"
        },
        {
            "message": "flori pentru înmormântare",
            "context": "Funeral",
            "expected": "Should be respectful, dignified, comforting"
        },
        {
            "message": "bujori pentru aniversare 25 de ani",
            "context": "Anniversary",
            "expected": "Should be celebratory, milestone-appropriate"
        },
        {
            "message": "un cadou floral pentru mama la ziua ei",
            "context": "Mother's birthday",
            "expected": "Should be caring, family-oriented, special"
        },
        {
            "message": "aranjament pentru birou să pun pe masă",
            "context": "Office arrangement",
            "expected": "Should be professional, practical, elegant"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"--- Test {i}: {test_case['context']} ---")
        print(f"Message: '{test_case['message']}'")
        print(f"Expected: {test_case['expected']}")
        print()
        
        # Get response
        response, intent, confidence = handler.handle_message(test_case['message'], f"test_user_{i}")
        
        print(f"Intent: {intent} (confidence: {confidence:.2f})")
        print(f"\nResponse:\n{response}")
        
        # Check for key conversational elements
        empathetic_words = ['înțeleg', 'perfect', 'frumos', 'special', 'împreună', 'din inimă']
        found_empathy = [word for word in empathetic_words if word in response.lower()]
        
        advice_words = ['recomand', 'sugerez', 'sfatul', 'experiență', 'am văzut']
        found_advice = [word for word in advice_words if word in response.lower()]
        
        print(f"\n✅ Empathetic elements: {found_empathy}")
        print(f"✅ Advisory elements: {found_advice}")
        
        print("=" * 80)
        print()

if __name__ == "__main__":
    test_various_scenarios()
