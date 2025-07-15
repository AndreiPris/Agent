#!/usr/bin/env python3
"""
Test script to verify budget recommendations work correctly
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from intelligence.product_search import ProductSearchEngine

def test_budget_recommendations():
    """Test budget recommendations with specific queries"""
    
    print("=== Testing Budget Recommendations ===\n")
    
    # Initialize the product search engine
    search_engine = ProductSearchEngine()
    
    # Test cases for budget recommendations
    test_cases = [
        {
            "query": "aniversare",
            "budget": 800,
            "description": "Anniversary bouquets under 800 MDL"
        },
        {
            "query": "buchet aniversare",
            "budget": 800,
            "description": "Anniversary bouquets under 800 MDL"
        },
        {
            "query": "trandafiri",
            "budget": 1000,
            "description": "Roses under 1000 MDL"
        },
        {
            "query": "bujori",
            "budget": 1500,
            "description": "Peonies under 1500 MDL"
        },
        {
            "query": "nuntă",
            "budget": 2000,
            "description": "Wedding flowers under 2000 MDL"
        },
        {
            "query": "",
            "budget": 500,
            "description": "Any products under 500 MDL"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"--- Test {i}: {test_case['description']} ---")
        print(f"Query: '{test_case['query']}'")
        print(f"Budget: {test_case['budget']} MDL")
        print()
        
        # Get budget recommendations
        results = search_engine.get_budget_recommendations(test_case['budget'], test_case['query'])
        
        if results:
            print(f"Found {len(results)} products within budget:")
            for j, product in enumerate(results, 1):
                name = product.get('name', 'Unknown')
                price = product.get('price', 'Unknown')
                category = product.get('category', 'Unknown')
                relevance_score = product.get('relevance_score', 'N/A')
                
                print(f"  {j}. {name}")
                print(f"     Price: {price} MDL")
                print(f"     Category: {category}")
                print(f"     Relevance Score: {relevance_score}")
                print()
        else:
            print("❌ No products found within budget!")
            print()
        
        print("=" * 60)
        print()

if __name__ == "__main__":
    test_budget_recommendations()
