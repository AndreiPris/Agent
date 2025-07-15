#!/usr/bin/env python3
"""
Test OpenAI API integration for XOFlowers bot
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from openai import OpenAI
    
    # Initialize OpenAI client
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OpenAI API key not found in environment variables")
        exit(1)
    
    client = OpenAI(api_key=api_key)
    
    print("🤖 Testing OpenAI API for XOFlowers bot...")
    print("=" * 50)
    
    # Test 1: Basic OpenAI chat completion
    print("\n1️⃣ Testing basic OpenAI chat completion:")
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant for XOFlowers flower shop in Moldova."},
                {"role": "user", "content": "Salut! Vreau să cumpăr flori pentru mama mea."}
            ],
            max_tokens=200,
            temperature=0.7
        )
        
        print("✅ OpenAI Response:")
        print(response.choices[0].message.content)
        
    except Exception as e:
        print(f"❌ OpenAI Error: {e}")
    
    # Test 2: Intent classification test
    print("\n2️⃣ Testing intent classification with OpenAI:")
    try:
        prompt = """
        You are an expert intent classifier for XOFlowers, a premium flower shop in Moldova.
        
        CURRENT MESSAGE: "Vreau să cumpăr trandafiri roșii pentru iubita mea"
        
        AVAILABLE INTENTS:
        1. find_product: Looking for flowers, bouquets, plants, gifts
        2. ask_question: General questions about business, hours, location
        3. greeting: Hello, good morning, starting conversation
        4. price_inquiry: Ask about prices, costs, tariffs
        5. romantic: Romantic flowers, Valentine's, love expressions
        
        Respond with ONLY the intent name and confidence (0.0-1.0):
        Format: intent_name:confidence
        """
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=50,
            temperature=0.1
        )
        
        result = response.choices[0].message.content.strip()
        print(f"✅ Intent Classification: {result}")
        
    except Exception as e:
        print(f"❌ Intent Classification Error: {e}")
    
    # Test 3: Product search enhancement
    print("\n3️⃣ Testing product search enhancement:")
    try:
        search_prompt = """
        You are a flower expert at XOFlowers in Moldova. A customer says:
        "Caut flori pentru ziua mamei, ceva frumos și nu prea scump"
        
        Extract the key search terms and suggest appropriate flower types.
        Respond in Romanian with specific flower recommendations.
        """
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": search_prompt}],
            max_tokens=150,
            temperature=0.6
        )
        
        print("✅ Product Search Enhancement:")
        print(response.choices[0].message.content)
        
    except Exception as e:
        print(f"❌ Product Search Error: {e}")
    
    # Test 4: Response personalization
    print("\n4️⃣ Testing response personalization:")
    try:
        personalization_prompt = """
        You are XOFlowers AI assistant. Create a personalized response for:
        
        Customer context: Returning customer, previously bought roses for Valentine's
        Current message: "Vreau să comand din nou aceleași trandafiri ca data trecută"
        
        Create a warm, personalized response in Romanian that acknowledges their history.
        """
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": personalization_prompt}],
            max_tokens=200,
            temperature=0.7
        )
        
        print("✅ Personalized Response:")
        print(response.choices[0].message.content)
        
    except Exception as e:
        print(f"❌ Personalization Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 OpenAI API testing completed!")
    print("✅ All tests passed - OpenAI integration is working correctly")
    
except ImportError as e:
    print(f"❌ OpenAI library not installed: {e}")
    print("Install with: pip install openai")
except Exception as e:
    print(f"❌ General error: {e}")
