"""
XOFlowers AI Agent Configuration Settings
Contains all constants, model configurations, and system parameters
"""

# AI Model Configuration
AI_MODEL = {
    'primary': 'openai',  # Primary AI service
    'fallback': 'gemini',  # Fallback AI service
    'ollama_model': 'llama3',  # Local Ollama model (if used)
    'temperature': 0.7,
    'max_tokens': 1000
}

# Database Configuration
DATABASE = {
    'chromadb_path': './chroma_db_flowers',
    'embedding_model': 'all-MiniLM-L6-v2',
    'collections': {
        'bouquets': 'bouquets_collection',
        'boxes': 'boxes_collection', 
        'compositions': 'compositions_collection',
        'plants': 'plants_collection',
        'gifts': 'gifts_collection'
    }
}

# API Configuration
API_CONFIG = {
    'instagram': {
        'webhook_port': 5001,
        'webhook_path': '/webhook',
        'health_path': '/health'
    },
    'telegram': {
        'polling_interval': 1.0
    }
}

# Intent Classification
INTENTS = {
    'find_product': {
        'description': 'User wants to search for or get product recommendations',
        'keywords': ['search', 'find', 'recommend', 'bouquet', 'flowers', 'gift']
    },
    'ask_question': {
        'description': 'User asks general questions about the business',
        'keywords': ['hours', 'location', 'delivery', 'policy', 'when', 'where']
    },
    'subscribe': {
        'description': 'User wants to subscribe to flower plans or updates',
        'keywords': ['subscribe', 'updates', 'newsletter', 'plan', 'monthly']
    },
    'pay_for_product': {
        'description': 'User expresses intention to pay for a product',
        'keywords': ['pay', 'buy', 'purchase', 'order', 'checkout']
    }
}

# Security Configuration
SECURITY = {
    'enable_censorship': True,
    'enable_jailbreak_protection': True,
    'rate_limiting': {
        'max_requests_per_minute': 10,
        'max_requests_per_hour': 100
    }
}

# Business Information
BUSINESS_INFO = {
    'name': 'XOFlowers',
    'location': 'Chișinău, Moldova',
    'website': 'https://xoflowers.md',
    'phone': '+373 XX XXX XXX',
    'email': 'contact@xoflowers.md'
}

# Response Configuration
RESPONSE_CONFIG = {
    'max_product_results': 5,
    'response_timeout': 30,
    'enable_typing_indicator': True
}

# Logging Configuration
LOGGING = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': './logs/xoflowers_agent.log'
}
