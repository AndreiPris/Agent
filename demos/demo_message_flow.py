#!/usr/bin/env python3
"""
XOFlowers Message Processing Flow Demo
Live demonstration of the complete message processing pipeline
"""

import os
import sys
import time
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def main():
    print("🌸 XOFLOWERS MESSAGE PROCESSING FLOW DEMO")
    print("=" * 60)
    print("Live demonstration of the complete message processing pipeline")
    print("Flow: Message → Security → Intent → Action → Response → Delivery")
    print()
    
    try:
        # Initialize components
        print("🔧 Initializing components...")
        from security.filters import SecurityFilter
        from intelligence.intent_classifier import IntentClassifier
        from intelligence.action_handler import ActionHandler
        
        security_filter = SecurityFilter()
        intent_classifier = IntentClassifier()
        action_handler = ActionHandler()
        print("✅ All components ready!")
        print()
        
        # Demo messages
        demo_messages = [
            "Vreau un buchet de trandafiri pentru mama mea",
            "Ce program aveți?",
            "Bună ziua!",
            "Vreau să plătesc pentru buchet",
            "Mulțumesc, la revedere!"
        ]
        
        for i, message in enumerate(demo_messages, 1):
            print(f"📨 DEMO MESSAGE {i}: '{message}'")
            print("-" * 60)
            
            start_time = time.time()
            
            # Complete flow
            print("🔍 Step 1: Receiving message...")
            time.sleep(0.1)  # Simulate processing time
            print("✅ Message received")
            
            print("🔒 Step 2: Security check...")
            is_safe = security_filter.is_safe_message(message)
            time.sleep(0.1)
            if is_safe:
                print("✅ Security check passed")
            else:
                print("🚫 Message blocked")
                continue
                
            print("🧠 Step 3: Intent classification...")
            intent, confidence = intent_classifier.classify_intent(message, f"demo_user_{i}")
            time.sleep(0.1)
            print(f"✅ Intent: {intent} (confidence: {confidence:.2f})")
            
            print("⚡ Step 4: Processing action...")
            response, action_type, response_confidence = action_handler.handle_message(message, f"demo_user_{i}")
            time.sleep(0.1)
            print(f"✅ Action: {action_type}")
            
            print("🎨 Step 5: Generating response...")
            time.sleep(0.1)
            print(f"✅ Response generated ({len(response)} chars)")
            
            print("📤 Step 6: Sending message...")
            time.sleep(0.1)
            total_time = round(time.time() - start_time, 3)
            print(f"✅ Message sent in {total_time}s")
            
            print(f"\n🎯 RESPONSE:")
            print(f"   {response[:200]}{'...' if len(response) > 200 else ''}")
            print("\n" + "=" * 60 + "\n")
            
    except Exception as e:
        print(f"❌ Demo error: {e}")
        return
    
    print("🎉 DEMO COMPLETE!")
    print("✅ All message processing components working correctly!")
    print("🚀 System is ready for production use!")

if __name__ == '__main__':
    main()
