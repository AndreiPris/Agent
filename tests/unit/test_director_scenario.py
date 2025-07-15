#!/usr/bin/env python3
"""
Test the specific scenario: "flori pentru ziua de naștere a unei directoare"
Verify that the bot provides high-profile bouquets with empathetic, personalized message
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from intelligence.action_handler import ActionHandler

def test_director_birthday_scenario():
    """Test the specific director birthday scenario"""
    
    print("=== Testing Director Birthday Scenario ===\n")
    
    # Initialize the action handler
    handler = ActionHandler()
    
    # Test the exact scenario from the task
    message = "flori pentru ziua de naștere a unei directoare"
    
    print(f"Testing message: '{message}'")
    print("Expected behavior: High-profile bouquets with empathetic, personalized message")
    print("Should sound like a real florist, not a generic bot\n")
    
    # Get response
    response, intent, confidence = handler.handle_message(message, "director_client")
    
    print(f"Intent: {intent}")
    print(f"Confidence: {confidence:.2f}")
    print(f"\nResponse:\n{response}")
    print("\n" + "="*80)
    
    # Analyze the response
    print("\n=== ANALYSIS ===")
    
    # Check for empathetic elements
    empathetic_phrases = [
        "înțeleg", "perfect", "desigur", "absolut", "important", "special",
        "memorabil", "rafinat", "elegant", "respect", "statutul", "impresie"
    ]
    
    found_empathy = [phrase for phrase in empathetic_phrases if phrase in response.lower()]
    print(f"✅ Empathetic phrases found: {found_empathy}")
    
    # Check for high-profile recommendations
    high_profile_indicators = [
        "premium", "important", "directoare", "memorabil", "impresie", 
        "elegant", "rafinat", "respect", "calitate", "profesional"
    ]
    
    found_high_profile = [indicator for indicator in high_profile_indicators if indicator in response.lower()]
    print(f"✅ High-profile indicators: {found_high_profile}")
    
    # Check for personalized advice
    advice_indicators = [
        "sfatul", "recomand", "sugerez", "experiență", "înțeleg", 
        "perfect", "ideal", "potrivit"
    ]
    
    found_advice = [indicator for indicator in advice_indicators if indicator in response.lower()]
    print(f"✅ Personalized advice indicators: {found_advice}")
    
    # Check for emotional/conversational tone
    conversational_indicators = [
        "să găsim", "să alegem", "împreună", "din inimă", "din experiență",
        "creez", "știu", "am văzut", "îmi place", "ce frumos"
    ]
    
    found_conversational = [indicator for indicator in conversational_indicators if indicator in response.lower()]
    print(f"✅ Conversational tone indicators: {found_conversational}")
    
    # Check for premium product prices (should be high-end)
    import re
    prices = re.findall(r'(\d+)\s*MDL', response)
    if prices:
        price_values = [int(p) for p in prices]
        avg_price = sum(price_values) / len(price_values)
        print(f"✅ Product prices: {price_values} MDL (average: {avg_price:.0f} MDL)")
        
        if avg_price > 3000:
            print("✅ GOOD: High-end products suitable for director")
        else:
            print("⚠️  CONCERN: Prices might be too low for high-profile person")
    
    # Overall assessment
    print(f"\n=== OVERALL ASSESSMENT ===")
    
    strengths = []
    if found_empathy:
        strengths.append("✅ Shows empathy and understanding")
    if found_high_profile:
        strengths.append("✅ Recognizes high-profile context")
    if found_advice:
        strengths.append("✅ Provides personalized advice")
    if found_conversational:
        strengths.append("✅ Uses conversational, human-like tone")
    if intent == "find_product":
        strengths.append("✅ Correctly identifies product search intent")
    if confidence > 0.7:
        strengths.append("✅ High confidence in intent classification")
    
    print("STRENGTHS:")
    for strength in strengths:
        print(f"  {strength}")
    
    if len(strengths) >= 5:
        print(f"\n🎉 EXCELLENT: The bot responds like a real, empathetic florist!")
        print("✅ Perfect for director birthday scenario")
    elif len(strengths) >= 3:
        print(f"\n👍 GOOD: The bot shows good conversational skills")
        print("✅ Suitable for director birthday scenario")
    else:
        print(f"\n⚠️  NEEDS IMPROVEMENT: The bot lacks conversational depth")
        print("❌ May not be suitable for high-profile scenarios")

if __name__ == "__main__":
    test_director_birthday_scenario()
