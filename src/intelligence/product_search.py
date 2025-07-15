"""
Product Search Engine Module
Handles product search using real CSV data from chunks_data.csv
"""

import os
import sys
import csv
import re
from typing import List, Dict, Optional, Tuple

# Add config to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'config'))

from settings import DATABASE, RESPONSE_CONFIG


class ProductSearchEngine:
    """
    Handles product search using real CSV data from chunks_data.csv
    """
    
    def __init__(self):
        """Initialize the product search engine"""
        self.db_config = DATABASE
        self.response_config = RESPONSE_CONFIG
        self.products = []
        self.categories = {}
        self._load_products()
        
    def _load_products(self):
        """Load products from chunks_data.csv"""
        try:
            csv_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'chunks_data.csv')
            
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row.get('chunk_type') == 'product':
                        product = {
                            'id': row.get('chunk_id', ''),
                            'name': self._extract_product_name(row.get('primary_text', '')),
                            'description': row.get('primary_text', ''),
                            'price': row.get('price', ''),
                            'category': row.get('category', ''),
                            'collection_id': row.get('collection_id', ''),
                            'flower_type': row.get('flower_type', ''),
                            'url': row.get('url', ''),
                            'keywords': self._extract_keywords(row.get('primary_text', ''))
                        }
                        self.products.append(product)
                        
                        # Group by category
                        category = product['category']
                        if category not in self.categories:
                            self.categories[category] = []
                        self.categories[category].append(product)
                        
            print(f"✅ Loaded {len(self.products)} products from {len(self.categories)} categories")
            
        except Exception as e:
            print(f"❌ Error loading products: {e}")
            self.products = []
            self.categories = {}
    
    def _extract_product_name(self, description: str) -> str:
        """Extract product name from description"""
        # Look for quoted names or capitalize first part
        if '"' in description:
            match = re.search(r'"([^"]+)"', description)
            if match:
                return match.group(1)
        
        # Extract name before first dash or description
        parts = description.split(' - ')
        if len(parts) > 1:
            return parts[0].strip()
        
        # Take first meaningful part
        words = description.split()
        if len(words) > 3:
            return ' '.join(words[:3])
        
        return description[:50] + '...' if len(description) > 50 else description
    
    def _extract_keywords(self, description: str) -> List[str]:
        """Extract keywords from product description"""
        # Convert to lowercase and split
        text = description.lower()
        
        # Common flower terms
        flower_terms = [
            'trandafir', 'bujor', 'peony', 'rose', 'hydrangea', 'gerbera', 'crizantema',
            'lalea', 'narcisă', 'zambile', 'frezii', 'cala', 'orhidee', 'garoafă',
            'lăcrimioare', 'eucalipt', 'viburnum', 'delphinium', 'scabiosa', 'eustoma',
            'anthurium', 'mattiola', 'spray', 'alstroemeria', 'solidago', 'lisianthus',
            'dianthus', 'wax flower', 'gypsophila', 'chrysanthemum', 'freesia', 'tulip'
        ]
        
        # Color terms
        color_terms = [
            'roșu', 'roz', 'alb', 'galben', 'violet', 'albastru', 'portocaliu',
            'verde', 'negru', 'cremă', 'pastel', 'coral', 'liliac', 'lavanda'
        ]
        
        # Occasion terms
        occasion_terms = [
            'nuntă', 'aniversare', 'ziua nașterii', 'valentine', 'mama', 'dragoste',
            'romantic', 'elegant', 'luxury', 'premium', 'corporate', 'funeral',
            'primăvară', 'vară', 'toamnă', 'iarnă', 'cadou', 'surpriză'
        ]
        
        keywords = []
        
        # Find flower terms
        for term in flower_terms:
            if term in text:
                keywords.append(term)
        
        # Find color terms
        for term in color_terms:
            if term in text:
                keywords.append(term)
        
        # Find occasion terms
        for term in occasion_terms:
            if term in text:
                keywords.append(term)
        
        return keywords
    
    def search_products(self, query: str, category: Optional[str] = None, context: Optional[Dict] = None) -> List[Dict]:
        """
        Search for products using keyword matching
        
        Args:
            query (str): Search query
            category (str, optional): Product category to filter by
            context (Dict, optional): Additional context for personalized search
            
        Returns:
            List[Dict]: List of matching products
        """
        if not self.products:
            return []
        
        query_lower = query.lower()
        results = []
        seen_names = set()  # Track seen product names to avoid duplicates
        
        # Filter out non-flower products
        excluded_categories = ['Additional accessories / Vases', 'Greeting card']
        excluded_keywords = ['fertilizer', 'card', 'vase', 'aquabox', 'diffuser']
        
        # Search through all products
        for product in self.products:
            # Skip non-flower products
            if product['category'] in excluded_categories:
                continue
            
            # Skip products with excluded keywords
            if any(keyword in product['name'].lower() for keyword in excluded_keywords):
                continue
            
            # Skip duplicates based on name
            if product['name'] in seen_names:
                continue
            
            score = 0
            
            # Check name match
            if any(word in product['name'].lower() for word in query_lower.split()):
                score += 10
            
            # Check description match
            if any(word in product['description'].lower() for word in query_lower.split()):
                score += 5
            
            # Check flower type match
            if any(word in product['flower_type'].lower() for word in query_lower.split()):
                score += 8
            
            # Check keywords match
            for keyword in product['keywords']:
                if keyword in query_lower:
                    score += 7
            
            # Special matching for common Romanian terms
            romanian_matches = {
                'trandafir': ['rose', 'roses'],
                'bujor': ['peony', 'peonies'],
                'flori': ['flower', 'flowers', 'bouquet'],
                'buchet': ['bouquet'],
                'cutie': ['box'],
                'coș': ['basket'],
                'nuntă': ['bride', 'wedding', 'bridal'],
                'aniversare': ['birthday', 'anniversary'],
                'roșu': ['red', 'scarlet'],
                'roz': ['pink'],
                'alb': ['white'],
                'galben': ['yellow'],
                'violet': ['purple', 'violet'],
                'luxury': ['luxurious', 'premium'],
                'elegant': ['elegant', 'stylish'],
                'lăcrimioare': ['lily of the valley', 'gypsophila']
            }
            
            for romanian_term, english_terms in romanian_matches.items():
                if romanian_term in query_lower:
                    for eng_term in english_terms:
                        if eng_term in product['description'].lower():
                            score += 6
            
            # Category filter
            if category and product['category'].lower() != category.lower():
                score = 0
            
            # Add to results if score is high enough
            if score >= 5:
                product_copy = product.copy()
                product_copy['relevance_score'] = score
                results.append(product_copy)
                seen_names.add(product['name'])  # Mark this name as seen
        
        # Sort by relevance score
        results.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        # Return top 5 unique results
        return results[:5]
    
    def get_product_by_id(self, product_id: str) -> Optional[Dict]:
        """
        Get a specific product by ID
        
        Args:
            product_id (str): Product ID
            
        Returns:
            Optional[Dict]: Product data or None if not found
        """
        for product in self.products:
            if product['id'] == product_id:
                return product
        return None
    
    def get_popular_products(self, limit: int = 5) -> List[Dict]:
        """
        Get popular/featured products (premium and luxury items)
        
        Args:
            limit (int): Number of products to return
            
        Returns:
            List[Dict]: List of popular products
        """
        excluded_categories = ['Additional accessories / Vases', 'Greeting card']
        excluded_keywords = ['fertilizer', 'card', 'vase', 'aquabox', 'diffuser']
        seen_names = set()  # Track seen product names to avoid duplicates
        
        # Filter for premium and luxury products
        premium_products = []
        for p in self.products:
            # Skip non-flower products
            if p['category'] in excluded_categories:
                continue
            
            # Skip products with excluded keywords
            if any(keyword in p['name'].lower() for keyword in excluded_keywords):
                continue
            
            # Skip duplicates
            if p['name'] in seen_names:
                continue
            
            # Include premium categories
            if p['category'] in ['Premium', 'Luxury', 'Peonies', 'Bride\'s bouquet', 'Author\'s bouquets']:
                premium_products.append(p)
                seen_names.add(p['name'])
        
        # Sort by price (higher price = more premium)
        premium_products.sort(key=lambda x: int(x['price']) if x['price'].isdigit() else 0, reverse=True)
        
        return premium_products[:limit]
    
    def get_products_by_category(self, category: str, limit: int = 10) -> List[Dict]:
        """
        Get products by category
        
        Args:
            category (str): Product category
            limit (int): Number of products to return
            
        Returns:
            List[Dict]: List of products in category
        """
        if category in self.categories:
            return self.categories[category][:limit]
        return []
    
    def get_budget_recommendations(self, max_price: int, query: str = "") -> List[Dict]:
        """
        Get product recommendations within budget
        
        Args:
            max_price (int): Maximum price in MDL
            query (str): Optional search query
            
        Returns:
            List[Dict]: List of products within budget
        """
        excluded_categories = ['Additional accessories / Vases', 'Greeting card']
        excluded_keywords = ['fertilizer', 'card', 'vase', 'aquabox', 'diffuser']
        seen_names = set()  # Track seen product names to avoid duplicates
        
        if query:
            # If query provided, first search for relevant products, then filter by budget
            all_results = self.search_products(query, context={'budget': max_price})
            
            # Filter results by budget
            budget_results = []
            for product in all_results:
                try:
                    price = int(product['price'])
                    if price <= max_price and product['name'] not in seen_names:
                        budget_results.append(product)
                        seen_names.add(product['name'])
                except (ValueError, TypeError):
                    continue
            
            # If we have budget-appropriate results, return them
            if budget_results:
                return budget_results[:5]
            
            # If no results within budget, find closest matches under budget
            budget_products = []
            for product in self.products:
                # Skip non-flower products
                if product['category'] in excluded_categories:
                    continue
                
                # Skip products with excluded keywords
                if any(keyword in product['name'].lower() for keyword in excluded_keywords):
                    continue
                
                # Skip duplicates
                if product['name'] in seen_names:
                    continue
                
                try:
                    price = int(product['price'])
                    if price <= max_price:
                        # Calculate relevance score for this product
                        score = self._calculate_relevance_score(product, query.lower())
                        if score >= 5:  # Only include relevant products
                            product_copy = product.copy()
                            product_copy['relevance_score'] = score
                            budget_products.append(product_copy)
                            seen_names.add(product['name'])
                except (ValueError, TypeError):
                    continue
            
            # Sort by relevance, then by price
            budget_products.sort(key=lambda x: (x['relevance_score'], -int(x['price']) if x['price'].isdigit() else 0), reverse=True)
            return budget_products[:5]
        
        else:
            # No specific query, just return products within budget
            budget_products = []
            for product in self.products:
                # Skip non-flower products
                if product['category'] in excluded_categories:
                    continue
                
                # Skip products with excluded keywords
                if any(keyword in product['name'].lower() for keyword in excluded_keywords):
                    continue
                
                # Skip duplicates
                if product['name'] in seen_names:
                    continue
                
                try:
                    price = int(product['price'])
                    if price <= max_price:
                        budget_products.append(product)
                        seen_names.add(product['name'])
                except (ValueError, TypeError):
                    continue
            
            # Sort by price (ascending)
            budget_products.sort(key=lambda x: int(x['price']) if x['price'].isdigit() else 0)
            return budget_products[:5]
    
    def _calculate_relevance_score(self, product: Dict, query_lower: str) -> int:
        """Calculate relevance score for a product based on query"""
        score = 0
        
        # Check name match
        if any(word in product['name'].lower() for word in query_lower.split()):
            score += 10
        
        # Check description match
        if any(word in product['description'].lower() for word in query_lower.split()):
            score += 5
        
        # Check flower type match
        if any(word in product['flower_type'].lower() for word in query_lower.split()):
            score += 8
        
        # Check keywords match
        for keyword in product['keywords']:
            if keyword in query_lower:
                score += 7
        
        # Special matching for common Romanian terms
        romanian_matches = {
            'trandafir': ['rose', 'roses'],
            'bujor': ['peony', 'peonies'],
            'flori': ['flower', 'flowers', 'bouquet'],
            'buchet': ['bouquet'],
            'cutie': ['box'],
            'coș': ['basket'],
            'nuntă': ['bride', 'wedding', 'bridal'],
            'aniversare': ['birthday', 'anniversary'],
            'roșu': ['red', 'scarlet'],
            'roz': ['pink'],
            'alb': ['white'],
            'galben': ['yellow'],
            'violet': ['purple', 'violet'],
            'luxury': ['luxurious', 'premium'],
            'elegant': ['elegant', 'stylish'],
            'lăcrimioare': ['lily of the valley', 'gypsophila']
        }
        
        for romanian_term, english_terms in romanian_matches.items():
            if romanian_term in query_lower:
                for eng_term in english_terms:
                    if eng_term in product['description'].lower():
                        score += 6
        
        return score
