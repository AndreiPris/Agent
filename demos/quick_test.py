#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from intelligence.product_search import ProductSearchEngine

engine = ProductSearchEngine()
results = engine.search_products('flori pentru aniversarea mamei')
print('=== Anniversary flowers for mom ===')
for i, product in enumerate(results, 1):
    print(f'{i}. {product["name"]} - {product["price"]} MDL')
    print(f'   Category: {product["category"]}')
    print()

print('=== Budget test (500 MDL) ===')
budget_results = engine.get_budget_recommendations(500, 'buchet')
for i, product in enumerate(budget_results, 1):
    print(f'{i}. {product["name"]} - {product["price"]} MDL')
    print(f'   Category: {product["category"]}')
    print()
