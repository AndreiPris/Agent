#!/usr/bin/env python3
"""
Test script to verify conversational and empathetic tone of the bot
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from intelligence.action_handler import ActionHandler

def test_conversational_tone():
    """Test the conversational and empathetic tone of the bot"""
    
    print("=== Testing Conversational Tone of XOFlowers Bot ===\n")
    
    # Initialize the action handler
    handler = ActionHandler()
    
    # Test cases with different contexts
    test_cases = [
        {
            "message": "flori pentru ziua de naștere a unei directoare",
            "context": "Director Birthday",
            "expected_tone": "professional, elegant, high-profile appropriate"
        },
        {
            "message": "caut un buchet romantic pentru iubita mea",
            "context": "Romantic",
            "expected_tone": "warm, romantic, emotionally supportive"
        },
        {
            "message": "am nevoie de flori pentru mama",
            "context": "Mother's Day",
            "expected_tone": "caring, understanding, family-oriented"
        },
        {
            "message": "vreau trandafiri roșii pentru nuntă",
            "context": "Wedding",
            "expected_tone": "celebratory, emotional, special occasion"
        },
        {
            "message": "aranjamente pentru înmormântare",
            "context": "Funeral",
            "expected_tone": "respectful, dignified, comforting"
        },
        {
            "message": "bujori pentru aniversare",
            "context": "Anniversary",
            "expected_tone": "celebratory, personal, meaningful"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"--- Test {i}: {test_case['context']} ---")
        print(f"Message: {test_case['message']}")
        print(f"Expected tone: {test_case['expected_tone']}")
        print()
        
        # Get response
        response, intent, confidence = handler.handle_message(test_case['message'], f"test_user_{i}")
        
        print(f"Intent: {intent} (confidence: {confidence:.2f})")
        print(f"Response:\n{response}")
        print()
        
        # Check for conversational elements
        conversational_elements = [
            "înțeleg", "perfect", "desigur", "absolut", "ce frumos", "îmi pare",
            "să găsim", "să alegem", "recomand", "sugerez", "sfatul meu"
        ]
        
        empathetic_elements = [
            "💕", "🌸", "✨", "💫", "🌺", "🌹", "💖", "🤍", "❤️"
        ]
        
        found_conversational = [elem for elem in conversational_elements if elem in response.lower()]
        found_empathetic = [elem for elem in empathetic_elements if elem in response]
        
        print(f"Conversational elements found: {found_conversational}")
        print(f"Empathetic elements found: {found_empathetic}")
        print("=" * 80)
        print()

if __name__ == "__main__":
    test_conversational_tone()
