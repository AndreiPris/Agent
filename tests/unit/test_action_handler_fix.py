#!/usr/bin/env python3
"""
Test script to verify the action handler works correctly with the fixed product search.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from intelligence.action_handler import ActionHandler

def test_action_handler():
    """Test the action handler with the fixed product search."""
    print("🤖 Testing Action Handler with Fixed Product Search")
    print("=" * 60)
    
    # Initialize the action handler
    action_handler = ActionHandler()
    
    # Test 1: Anniversary flowers for mom
    print("\n1. Testing 'anniversary flowers for mom' query:")
    print("-" * 50)
    
    response = action_handler.handle_message("anniversary flowers for mom", "test_user")
    print(f"Response: {response}")
    
    # Test 2: Budget recommendations
    print("\n2. Testing budget recommendations:")
    print("-" * 50)
    
    response = action_handler.handle_message("I have a budget of 1000 MDL for anniversary flowers", "test_user")
    print(f"Response: {response}")
    
    # Test 3: Popular products
    print("\n3. Testing popular products:")
    print("-" * 50)
    
    response = action_handler.handle_message("show me popular products", "test_user")
    print(f"Response: {response}")
    
    # Test 4: Search for potentially problematic terms
    print("\n4. Testing search for 'roses' (should work):")
    print("-" * 50)
    
    response = action_handler.handle_message("I want roses", "test_user")
    print(f"Response: {response}")
    
    # Test 5: Search for 'fertilizer' (should return no results)
    print("\n5. Testing search for 'fertilizer' (should return no results):")
    print("-" * 50)
    
    response = action_handler.handle_message("I want fertilizer", "test_user")
    print(f"Response: {response}")
    
    print("\n" + "=" * 60)
    print("🎯 Action Handler Test Complete")

if __name__ == "__main__":
    test_action_handler()
