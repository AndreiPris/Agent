#!/usr/bin/env python3
"""
Comprehensive test script for the enhanced conversational agent
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'config'))

from dotenv import load_dotenv
load_dotenv()

from intelligence.intent_classifier import IntentClassifier
from intelligence.action_handler import ActionHandler
from security.filters import SecurityFilter

def test_enhanced_agent():
    """Test the enhanced conversational agent with new intent types"""
    
    # Initialize components
    intent_classifier = IntentClassifier()
    action_handler = ActionHandler()
    security_filter = SecurityFilter()
    
    # Comprehensive test messages covering all intent types
    test_messages = [
        # Core intents
        ("Vreau flori pentru soția mea", "find_product"),
        ("Ce program aveți?", "ask_question"),
        ("Vreau să mă abonez la newsletter", "subscribe"),
        ("Cum pot să plătesc?", "pay_for_product"),
        
        # New intents
        ("Bună ziua!", "greeting"),
        ("Unde este comanda mea?", "order_status"),
        ("Florile au venit ofilite", "complaint"),
        ("Ce îmi recomandați?", "recommendation"),
        ("Aveți trandafiri roșii în stoc?", "availability"),
        ("Cât costă livrarea?", "delivery_info"),
        ("Vreau să anulez comanda", "cancel_order"),
        ("Cât costă buchetele?", "price_inquiry"),
        ("Aveți oferte speciale?", "seasonal_offers"),
        ("Ce cadou pentru aniversare?", "gift_suggestions"),
        ("Cum să păstrez florile?", "care_instructions"),
        ("Vreau să comand pentru firmă", "bulk_orders"),
        ("Mulțumesc, la revedere!", "farewell"),
    ]
    
    print("🧪 Testing Enhanced XOFlowers Conversational Agent")
    print("=" * 60)
    
    correct_predictions = 0
    total_tests = len(test_messages)
    
    for i, (message, expected_intent) in enumerate(test_messages, 1):
        print(f"\n{i:2d}. Message: '{message}'")
        
        # Security check
        is_safe = security_filter.is_message_safe(message)
        print(f"    Security: {'✅ Safe' if is_safe else '❌ Blocked'}")
        
        if is_safe:
            # Intent classification
            predicted_intent, confidence = intent_classifier.classify_intent(message)
            print(f"    Expected: {expected_intent}")
            print(f"    Predicted: {predicted_intent}")
            print(f"    Confidence: {confidence:.2f}")
            
            # Check if prediction is correct
            if predicted_intent == expected_intent:
                print("    Result: ✅ CORRECT")
                correct_predictions += 1
            else:
                print("    Result: ❌ INCORRECT")
            
            # Get response
            response, intent_returned, confidence_returned = action_handler.handle_message(message, "test_user")
            print(f"    Response: {response[:80]}...")
        
        print("-" * 50)
    
    # Final statistics
    accuracy = (correct_predictions / total_tests) * 100
    print(f"\n📊 FINAL RESULTS:")
    print(f"✅ Correct predictions: {correct_predictions}/{total_tests}")
    print(f"📈 Accuracy: {accuracy:.1f}%")
    
    if accuracy >= 80:
        print("🎉 EXCELLENT! The conversational agent is working well!")
    elif accuracy >= 60:
        print("👍 GOOD! Some improvements needed.")
    else:
        print("⚠️ NEEDS IMPROVEMENT! Intent classification needs work.")
    
    return accuracy

if __name__ == "__main__":
    test_enhanced_agent()
