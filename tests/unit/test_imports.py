#!/usr/bin/env python3
"""
Simple test script to check individual components
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'config'))

from dotenv import load_dotenv
load_dotenv()

# Test individual imports step by step
print("Testing individual imports...")

try:
    print("1. Testing settings import...")
    sys.path.insert(0, './config')
    from settings import BUSINESS_INFO, RESPONSE_CONFIG, INTENTS
    print("   ✅ Settings imported successfully")
except Exception as e:
    print(f"   ❌ Settings import error: {e}")

try:
    print("2. Testing prompts import...")
    from src.intelligence.prompts import INTENT_RECOGNITION_PROMPT, FALLBACK_PROMPT
    print("   ✅ Prompts imported successfully")
except Exception as e:
    print(f"   ❌ Prompts import error: {e}")

try:
    print("3. Testing intent classifier...")
    from src.intelligence.intent_classifier import IntentClassifier
    ic = IntentClassifier()
    print("   ✅ Intent classifier imported successfully")
except Exception as e:
    print(f"   ❌ Intent classifier import error: {e}")

try:
    print("4. Testing product search...")
    from src.intelligence.product_search import ProductSearchEngine
    ps = ProductSearchEngine()
    print("   ✅ Product search imported successfully")
except Exception as e:
    print(f"   ❌ Product search import error: {e}")

try:
    print("5. Testing action handler...")
    from src.intelligence.action_handler import ActionHandler
    ah = ActionHandler()
    print("   ✅ Action handler imported successfully")
except Exception as e:
    print(f"   ❌ Action handler import error: {e}")

try:
    print("6. Testing security filter...")
    from src.security.filters import SecurityFilter
    sf = SecurityFilter()
    print("   ✅ Security filter imported successfully")
except Exception as e:
    print(f"   ❌ Security filter import error: {e}")

print("\n🎉 Component testing complete!")
