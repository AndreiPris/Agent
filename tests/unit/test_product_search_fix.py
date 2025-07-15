#!/usr/bin/env python3
"""
Test script to verify the product search fix for:
1. No fertilizer products in results
2. No duplicate bouquets
3. Relevant results for "anniversary flowers for mom"
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from intelligence.product_search import ProductSearchEngine

def test_product_search_fix():
    """Test the product search fix for the specific issues mentioned."""
    print("🧪 Testing Product Search Fix")
    print("=" * 50)
    
    # Initialize the search engine
    search_engine = ProductSearchEngine()
    
    # Test 1: Anniversary flowers for mom
    print("\n1. Testing 'anniversary flowers for mom' query:")
    print("-" * 40)
    
    results = search_engine.search_products("anniversary flowers for mom")
    
    print(f"Found {len(results)} products:")
    
    product_names = []
    for i, product in enumerate(results, 1):
        print(f"{i}. {product['name']}")
        print(f"   Price: {product['price']} MDL")
        print(f"   Category: {product['category']}")
        print(f"   Relevance Score: {product.get('relevance_score', 'N/A')}")
        product_names.append(product['name'])
        print()
    
    # Check for duplicates
    duplicates = [name for name in product_names if product_names.count(name) > 1]
    if duplicates:
        print(f"❌ FOUND DUPLICATES: {duplicates}")
    else:
        print("✅ No duplicates found")
    
    # Check for non-flower products
    non_flower_found = []
    for product in results:
        name_lower = product['name'].lower()
        if any(keyword in name_lower for keyword in ['fertilizer', 'card', 'vase', 'aquabox', 'diffuser']):
            non_flower_found.append(product['name'])
    
    if non_flower_found:
        print(f"❌ FOUND NON-FLOWER PRODUCTS: {non_flower_found}")
    else:
        print("✅ No non-flower products found")
    
    # Test 2: Budget recommendations
    print("\n2. Testing budget recommendations:")
    print("-" * 40)
    
    budget_results = search_engine.get_budget_recommendations(1000, "anniversary flowers")
    
    print(f"Found {len(budget_results)} budget products:")
    
    budget_names = []
    for i, product in enumerate(budget_results, 1):
        print(f"{i}. {product['name']}")
        print(f"   Price: {product['price']} MDL")
        print(f"   Category: {product['category']}")
        budget_names.append(product['name'])
        print()
    
    # Check for duplicates in budget results
    budget_duplicates = [name for name in budget_names if budget_names.count(name) > 1]
    if budget_duplicates:
        print(f"❌ FOUND BUDGET DUPLICATES: {budget_duplicates}")
    else:
        print("✅ No budget duplicates found")
    
    # Test 3: Popular products
    print("\n3. Testing popular products:")
    print("-" * 40)
    
    popular_results = search_engine.get_popular_products(5)
    
    print(f"Found {len(popular_results)} popular products:")
    
    popular_names = []
    for i, product in enumerate(popular_results, 1):
        print(f"{i}. {product['name']}")
        print(f"   Price: {product['price']} MDL")
        print(f"   Category: {product['category']}")
        popular_names.append(product['name'])
        print()
    
    # Check for duplicates in popular results
    popular_duplicates = [name for name in popular_names if popular_names.count(name) > 1]
    if popular_duplicates:
        print(f"❌ FOUND POPULAR DUPLICATES: {popular_duplicates}")
    else:
        print("✅ No popular duplicates found")
    
    # Test 4: Search for specific problematic terms
    print("\n4. Testing search for problematic terms:")
    print("-" * 40)
    
    problematic_queries = ["fertilizer", "greeting card", "vase", "aquabox"]
    
    for query in problematic_queries:
        print(f"\nSearching for '{query}':")
        problem_results = search_engine.search_products(query)
        if problem_results:
            print(f"❌ FOUND {len(problem_results)} results for '{query}' (should be 0)")
            for product in problem_results:
                print(f"   - {product['name']}")
        else:
            print(f"✅ No results for '{query}' (correct)")
    
    print("\n" + "=" * 50)
    print("🎯 Product Search Fix Test Complete")

if __name__ == "__main__":
    test_product_search_fix()
