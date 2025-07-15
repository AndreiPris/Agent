#!/usr/bin/env python3
"""
Test script to verify budget functionality in action handler
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from intelligence.action_handler import ActionHandler

def test_action_handler_budget():
    """Test budget functionality through action handler"""
    
    print("=== Testing Action Handler Budget Functionality ===\n")
    
    # Initialize the action handler
    handler = ActionHandler()
    
    # Test cases for budget queries
    test_cases = [
        "vreau buchete pentru aniversare până la 800 lei",
        "caut flori pentru aniversare cu buget 800 MDL",
        "trandafiri până la 1000 lei",
        "bujori cu buget până la 1500 lei",
        "flori pentru nuntă până la 2000 lei",
        "ceva ieftin până la 500 lei",
    ]
    
    for i, message in enumerate(test_cases, 1):
        print(f"--- Test {i} ---")
        print(f"Message: '{message}'")
        print()
        
        # Get response from action handler
        response, intent, confidence = handler.handle_message(message, f"test_user_{i}")
        
        print(f"Intent: {intent}")
        print(f"Confidence: {confidence:.2f}")
        print(f"Response:\n{response}")
        print()
        print("=" * 80)
        print()

if __name__ == "__main__":
    test_action_handler_budget()
