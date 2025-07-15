#!/usr/bin/env python3
"""
Test the updated product search system
"""

import sys
import os
sys.path.insert(0, 'src')

from intelligence.product_search import ProductSearchEngine

def test_product_search():
    print("🧪 Testing updated product search system...")
    
    # Initialize the engine
    engine = ProductSearchEngine()
    print(f"✅ Loaded {len(engine.products)} products")
    print(f"✅ Categories: {list(engine.categories.keys())}")
    
    # Test searches
    test_queries = [
        "trandafiri roșii",
        "bujori",
        "lăcrimioare",
        "nuntă",
        "aniversare",
        "flori pentru mama",
        "buchet elegant",
        "luxury"
    ]
    
    for query in test_queries:
        results = engine.search_products(query)
        print(f"\\n🔍 Query: '{query}' -> Found {len(results)} results:")
        for i, result in enumerate(results[:3], 1):
            print(f"  {i}. {result['name']} - {result['price']} MDL")
            print(f"     Flowers: {result['flower_type']}")
            print(f"     Category: {result['category']}")
    
    # Test popular products
    print(f"\\n🌟 Popular products:")
    popular = engine.get_popular_products(5)
    for i, product in enumerate(popular, 1):
        print(f"  {i}. {product['name']} - {product['price']} MDL")

if __name__ == "__main__":
    test_product_search()
