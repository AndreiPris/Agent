#!/usr/bin/env python3
"""
Quick test script to verify the XOFlowers agent is working
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

print("🌸 XOFlowers Agent Test Script")
print("=" * 50)

# Test 1: Basic imports
print("\n1. Testing basic imports...")
try:
    from src.intelligence.action_handler import ActionHandler
    print("✅ ActionHandler imported successfully")
except Exception as e:
    print(f"❌ ActionHandler import failed: {e}")

# Test 2: Database connection
print("\n2. Testing database setup...")
try:
    from src.database.manager import DatabaseManager
    db = DatabaseManager()
    print("✅ Database manager created")
except Exception as e:
    print(f"❌ Database manager failed: {e}")

# Test 3: Product search
print("\n3. Testing product search...")
try:
    from src.intelligence.product_search import ProductSearchEngine
    search = ProductSearchEngine()
    print("✅ Product search engine created")
except Exception as e:
    print(f"❌ Product search failed: {e}")

# Test 4: Intent classification
print("\n4. Testing intent classification...")
try:
    from src.intelligence.intent_classifier import IntentClassifier
    classifier = IntentClassifier()
    print("✅ Intent classifier created")
except Exception as e:
    print(f"❌ Intent classifier failed: {e}")

# Test 5: Basic message handling
print("\n5. Testing basic message handling...")
try:
    handler = ActionHandler()
    test_message = "Salut! Caut un buchet de trandafiri pentru iubita mea."
    response, intent, confidence = handler.handle_message(test_message, "test_user")
    print(f"✅ Message handled successfully")
    print(f"   Intent: {intent}")
    print(f"   Confidence: {confidence:.2f}")
    print(f"   Response preview: {response[:100]}...")
except Exception as e:
    print(f"❌ Message handling failed: {e}")

print("\n" + "=" * 50)
print("🌸 Test completed!")
