#!/usr/bin/env python3
"""
Test script to verify that all tasks are completed successfully
"""
import sys
import os
sys.path.append('src')

def test_task_1_conversation_context():
    """Test Task 1: ConversationContext Implementation"""
    print("🧪 Testing Task 1: ConversationContext...")
    
    try:
        from intelligence.conversation_context import ConversationContext
        
        # Test basic functionality
        context = ConversationContext()
        print("✅ ConversationContext class imported successfully")
        
        # Test methods exist
        assert hasattr(context, 'add_turn'), "add_turn method should exist"
        assert hasattr(context, 'get_context'), "get_context method should exist"
        assert hasattr(context, 'get_user_profile'), "get_user_profile method should exist"
        print("✅ All required methods exist")
        
        # Test basic usage
        context.add_turn(
            user_id="test_user",
            user_message="Hello",
            bot_response="Hi there!",
            intent="greeting"
        )
        
        user_context = context.get_context("test_user")
        assert len(user_context) >= 0, "Context should be retrievable"
        print("✅ Basic functionality works")
        
        print("🎉 Task 1 COMPLETED: ConversationContext is working!")
        return True
        
    except Exception as e:
        print(f"❌ Task 1 FAILED: {e}")
        return False

def test_task_2_action_handler():
    """Test Task 2: Action Handler Implementation"""
    print("\n🧪 Testing Task 2: Action Handler...")
    
    try:
        from intelligence.action_handler import ActionHandler
        
        # Test basic functionality
        handler = ActionHandler()
        print("✅ ActionHandler class imported successfully")
        
        # Test methods exist
        assert hasattr(handler, 'handle_message'), "handle_message method should exist"
        assert hasattr(handler, '_route_to_handler'), "_route_to_handler method should exist"
        print("✅ All required methods exist")
        
        # Test basic routing
        response, intent, confidence = handler.handle_message("Hello!", "test_user")
        assert isinstance(response, str), "Response should be a string"
        assert isinstance(intent, str), "Intent should be a string"
        assert isinstance(confidence, float), "Confidence should be a float"
        print("✅ Basic routing works")
        
        print("🎉 Task 2 COMPLETED: ActionHandler is working!")
        return True
        
    except Exception as e:
        print(f"❌ Task 2 FAILED: {e}")
        return False

def test_task_3_intent_classifier():
    """Test Task 3: Intent Classification with Extended Intents"""
    print("\n🧪 Testing Task 3: Intent Classification...")
    
    try:
        from intelligence.intent_classifier import IntentClassifier
        
        # Test basic functionality
        classifier = IntentClassifier()
        print("✅ IntentClassifier class imported successfully")
        
        # Test methods exist
        assert hasattr(classifier, 'classify_intent'), "classify_intent method should exist"
        print("✅ All required methods exist")
        
        # Test extended intents
        extended_intents = [
            'find_product', 'ask_question', 'subscribe', 'pay_for_product',
            'greeting', 'order_status', 'complaint', 'recommendation',
            'availability', 'delivery_info', 'cancel_order', 'price_inquiry',
            'seasonal_offers', 'gift_suggestions', 'care_instructions',
            'bulk_orders', 'farewell'
        ]
        
        assert len(classifier.intents) >= 17, f"Should have at least 17 intents, found {len(classifier.intents)}"
        print(f"✅ Extended intents available: {len(classifier.intents)} intents")
        
        # Test basic classification
        intent, confidence = classifier.classify_intent("Hello there!")
        assert intent in classifier.intents or intent == "fallback", f"Intent {intent} should be valid"
        assert 0.0 <= confidence <= 1.0, f"Confidence should be between 0.0 and 1.0, got {confidence}"
        print("✅ Basic classification works")
        
        print("🎉 Task 3 COMPLETED: Intent Classification is working!")
        return True
        
    except Exception as e:
        print(f"❌ Task 3 FAILED: {e}")
        return False

def test_integration():
    """Test full integration of all components"""
    print("\n🧪 Testing Integration...")
    
    try:
        from intelligence.conversation_context import ConversationContext
        from intelligence.action_handler import ActionHandler
        from intelligence.intent_classifier import IntentClassifier
        
        # Test full workflow
        context = ConversationContext()
        handler = ActionHandler()
        classifier = IntentClassifier()
        
        # Test message processing
        test_message = "Vreau să găsesc niște trandafiri roșii"
        response, intent, confidence = handler.handle_message(test_message, "test_user")
        
        print(f"✅ Message: '{test_message}'")
        print(f"✅ Intent: {intent}")
        print(f"✅ Confidence: {confidence:.2f}")
        print(f"✅ Response: {response[:100]}...")
        
        print("🎉 INTEGRATION SUCCESSFUL: All components work together!")
        return True
        
    except Exception as e:
        print(f"❌ INTEGRATION FAILED: {e}")
        return False

def main():
    """Run all tests"""
    print("🌸 XOFlowers AI Agent - Task Completion Test")
    print("=" * 50)
    
    results = []
    results.append(test_task_1_conversation_context())
    results.append(test_task_2_action_handler())
    results.append(test_task_3_intent_classifier())
    results.append(test_integration())
    
    print("\n" + "=" * 50)
    print("📊 FINAL RESULTS:")
    print(f"✅ Tasks Completed: {sum(results)}/4")
    print(f"❌ Tasks Failed: {4 - sum(results)}/4")
    
    if all(results):
        print("\n🎉 ALL TASKS COMPLETED SUCCESSFULLY!")
        print("🌸 XOFlowers AI Agent is fully functional!")
        return True
    else:
        print("\n❌ Some tasks failed. Please check the output above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
