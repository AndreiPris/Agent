#!/usr/bin/env python3
"""
Simple test script to check if the conversational agent components work
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'config'))

from dotenv import load_dotenv
load_dotenv()

# Test imports
try:
    from intelligence.intent_classifier import IntentClassifier
    from intelligence.action_handler import ActionHandler
    from src.security.filters import SecurityFilter
    print("✅ All imports successful")
except Exception as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

# Test basic functionality
try:
    # Initialize components
    intent_classifier = IntentClassifier()
    action_handler = ActionHandler()
    security_filter = SecurityFilter()
    
    # Test messages
    test_messages = [
        "Bună ziua! Vreau flori pentru soția mea",
        "Ce program aveți?",
        "Vreau să mă abonez la newsletter",
        "Cum pot să plătesc?"
    ]
    
    print("\n🧪 Testing conversational agent components:")
    print("=" * 50)
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n{i}. Message: '{message}'")
        
        # Security check
        is_safe = security_filter.is_message_safe(message)
        print(f"   Security: {'✅ Safe' if is_safe else '❌ Blocked'}")
        
        if is_safe:
            # Intent classification
            intent, confidence = intent_classifier.classify_intent(message)
            print(f"   Intent: {intent}")
            
            # Action handling
            response, returned_intent, returned_confidence = action_handler.handle_message(message, "test_user")
            print(f"   Response: {response[:100]}...")
        
        print("-" * 40)
    
    print("\n🎉 All components working correctly!")
    
except Exception as e:
    print(f"❌ Error during testing: {e}")
    import traceback
    traceback.print_exc()
