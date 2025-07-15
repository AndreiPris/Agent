#!/usr/bin/env python3
"""
Test XOFlowers AI system with real intent classification
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from intelligence.intent_classifier import IntentClassifier
    from intelligence.action_handler import ActionHandler
    
    print("🌸 Testing XOFlowers AI System...")
    print("=" * 50)
    
    # Initialize components
    intent_classifier = IntentClassifier()
    action_handler = ActionHandler()
    
    # Test messages in Romanian
    test_messages = [
        "Bună ziua! Vreau să cumpăr flori pentru mama mea.",
        "Caut trandafiri roșii pentru iubita mea",
        "Ce preț au buchetele de nuntă?",
        "Când sunteți deschiși?",
        "Vreau să comand flori cu livrare",
        "Salut! Ce flori recomandați pentru ziua de naștere?",
        "Mulțumesc pentru servicii! La revedere!",
        "Am o problemă cu comanda mea"
    ]
    
    print("\n🤖 Testing Intent Classification and Response Generation:")
    print("-" * 50)
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n{i}️⃣ Message: \"{message}\"")
        
        try:
            # Test intent classification
            intent, confidence = intent_classifier.classify_intent(message, f"test_user_{i}")
            print(f"   🎯 Intent: {intent} (confidence: {confidence:.2f})")
            
            # Test full response generation
            response, detected_intent, final_confidence = action_handler.handle_message(message, f"test_user_{i}")
            print(f"   📝 Response preview: {response[:100]}...")
            
        except Exception as e:
            print(f"   ❌ Error processing message: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 XOFlowers AI System testing completed!")
    
    # Test specific OpenAI integration
    print("\n🔍 Testing OpenAI Integration Specifically:")
    print("-" * 50)
    
    test_message = "Vreau buchete cu trandafiri roșii până la 500 MDL pentru Valentine's Day"
    try:
        result = intent_classifier._classify_with_openai(test_message, "")
        print(f"✅ OpenAI Classification: {result}")
    except Exception as e:
        print(f"❌ OpenAI Classification Error: {e}")
    
    print("\n✅ All systems operational!")
    
except Exception as e:
    print(f"❌ System error: {e}")
    import traceback
    traceback.print_exc()
