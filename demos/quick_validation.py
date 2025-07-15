#!/usr/bin/env python3
"""
Quick validation test for the specific issues mentioned by the user.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from intelligence.action_handler import ActionHandler

def test_specific_issues():
    """Test the specific issues mentioned by the user."""
    print("🎯 Testing Specific Issues Fix")
    print("=" * 50)
    
    action_handler = ActionHandler()
    
    # Test the exact query mentioned by the user
    print("\n🔍 Testing: 'anniversary flowers for mom'")
    print("-" * 40)
    
    response, intent, confidence = action_handler.handle_message("anniversary flowers for mom", "test_user")
    
    print(f"Intent: {intent}")
    print(f"Confidence: {confidence}")
    print(f"Response preview: {response[:200]}...")
    
    # Check if the response contains fertilizer or other non-flower products
    if "fertilizer" in response.lower():
        print("❌ ERROR: Found fertilizer in response!")
    else:
        print("✅ No fertilizer found in response")
    
    if "greeting card" in response.lower():
        print("❌ ERROR: Found greeting card in response!")
    else:
        print("✅ No greeting card found in response")
    
    if "vase" in response.lower():
        print("❌ ERROR: Found vase in response!")
    else:
        print("✅ No vase found in response")
    
    # Count unique products in response
    products_mentioned = []
    lines = response.split('\n')
    for line in lines:
        if '**' in line and 'MDL' not in line:
            # Extract product name
            parts = line.split('**')
            if len(parts) >= 3:
                product_name = parts[1].strip()
                if product_name and product_name not in products_mentioned:
                    products_mentioned.append(product_name)
    
    print(f"\n📊 Found {len(products_mentioned)} unique products:")
    for i, product in enumerate(products_mentioned, 1):
        print(f"  {i}. {product}")
    
    # Check for duplicates
    if len(products_mentioned) != len(set(products_mentioned)):
        print("❌ ERROR: Duplicates detected!")
    else:
        print("✅ No duplicates detected")
    
    print("\n" + "=" * 50)
    print("🎉 Specific Issues Test Complete")

if __name__ == "__main__":
    test_specific_issues()
