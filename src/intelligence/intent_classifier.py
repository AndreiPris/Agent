"""
Enhanced Intent Classification Module
Advanced AI-powered intent recognition with context awareness and conversation memory
"""

import os
import sys
import re
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# Add config to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'config'))

from settings import INTENTS, AI_MODEL
from .prompts import ENHANCED_INTENT_RECOGNITION_PROMPT, JAILBREAK_RESPONSE
from .conversation_context import ConversationContext

# Import AI libraries
try:
    from openai import OpenAI
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        openai_client = OpenAI(api_key=api_key)
        HAS_OPENAI = True
    else:
        openai_client = None
        HAS_OPENAI = False
except ImportError:
    openai_client = None
    HAS_OPENAI = False
except Exception as e:
    print(f"OpenAI client initialization error: {e}")
    openai_client = None
    HAS_OPENAI = False

try:
    import google.generativeai as genai
    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
    HAS_GEMINI = True
except ImportError:
    genai = None
    HAS_GEMINI = False


class IntentClassifier:
    """
    Advanced AI-powered intent classifier with context awareness
    """
    
    def __init__(self):
        """Initialize the enhanced intent classifier"""
        self.intents = {
            # Core business intents
            'find_product': {
                'keywords': ['vreau', 'caut', 'arată', 'flori', 'buchet', 'cutie', 'cadou', 'plante', 'trandafir', 'bujor', 'aniversare', 'zi de naștere', 'mama', 'nuntă', 'directoare', 'înmormântare', 'funeral', 'comemorare', 'aranjament'],
                'context': 'User is looking for flowers, bouquets, or gifts',
                'priority': 10
            },
            'ask_question': {
                'keywords': ['ce', 'cum', 'când', 'unde', 'program', 'orar', 'locație', 'contact', 'despre'],
                'context': 'User has general questions about the business',
                'priority': 7
            },
            'subscribe': {
                'keywords': ['abonez', 'newsletter', 'actualizări', 'notificări', 'planuri', 'mă înscriu'],
                'context': 'User wants to subscribe to services or updates',
                'priority': 8
            },
            'pay_for_product': {
                'keywords': ['plată', 'plătesc', 'card', 'comanda', 'cumpăr', 'finalizez', 'plătire'],
                'context': 'User wants to make a payment or purchase',
                'priority': 9
            },
            
            # Enhanced interaction intents
            'greeting': {
                'keywords': ['bună', 'salut', 'hello', 'hey', 'noroc', 'servus', 'bună ziua', 'bună dimineața'],
                'context': 'User is greeting or starting conversation',
                'priority': 5
            },
            'order_status': {
                'keywords': ['comandă', 'status', 'starea', 'verifică', 'livrat', 'unde este', 'când ajunge'],
                'context': 'User wants to check order status',
                'priority': 9
            },
            'complaint': {
                'keywords': ['reclamație', 'problemă', 'nemulțumit', 'calitate', 'rău', 'ofilite', 'stricat'],
                'context': 'User has a complaint or issue',
                'priority': 10
            },
            'recommendation': {
                'keywords': ['recomandă', 'sugerează', 'cea mai bună', 'popular', 'ce îmi recomandați'],
                'context': 'User asks for recommendations',
                'priority': 8
            },
            'availability': {
                'keywords': ['disponibil', 'stoc', 'există', 'aveți', 'în stoc'],
                'context': 'User checks product availability',
                'priority': 8
            },
            'delivery_info': {
                'keywords': ['livrare', 'transport', 'când ajunge', 'cost livrare', 'cât costă livrarea'],
                'context': 'User asks about delivery information',
                'priority': 7
            },
            'cancel_order': {
                'keywords': ['anulat', 'renunt', 'să nu mai', 'anulez', 'schimb părerea'],
                'context': 'User wants to cancel an order',
                'priority': 9
            },
            'price_inquiry': {
                'keywords': ['preț', 'cost', 'cât costă', 'tarif', 'prețuri'],
                'context': 'User asks about prices',
                'priority': 7
            },
            'seasonal_offers': {
                'keywords': ['oferte', 'reduceri', 'promoții', 'special', 'discount'],
                'context': 'User asks about special offers',
                'priority': 6
            },
            'gift_suggestions': {
                'keywords': ['cadou', 'valentine', 'dragobete', 'sugestii', 'idei'],
                'context': 'User asks for gift suggestions',
                'priority': 8
            },
            'care_instructions': {
                'keywords': ['îngrijire', 'cum să păstrez', 'conservare', 'durabilitate', 'să țină'],
                'context': 'User asks how to care for flowers',
                'priority': 6
            },
            'bulk_orders': {
                'keywords': ['cantitate mare', 'corporate', 'firmă', 'eveniment', 'multe', 'în număr mare'],
                'context': 'User wants to place bulk orders',
                'priority': 8
            },
            'farewell': {
                'keywords': ['pa', 'la revedere', 'bye', 'mulțumesc', 'să aveți', 'o zi bună'],
                'context': 'User is saying goodbye',
                'priority': 5
            }
        }
        
        self.ai_config = AI_MODEL
        self.context_manager = ConversationContext()
        self.confidence_threshold = 0.6
        
    def classify_intent(self, message: str, user_id: str = None) -> Tuple[str, float]:
        """
        Enhanced intent classification with context awareness
        
        Args:
            message (str): User message to classify
            user_id (str): User identifier for context
            
        Returns:
            Tuple[str, float]: (intent, confidence_score)
        """
        message_lower = message.lower().strip()
        
        # Handle empty messages
        if not message_lower:
            return "fallback", 0.0
        
        # Check for jailbreak attempts first
        if self.is_jailbreak_attempt(message):
            return "jailbreak", 1.0
        
        # Get conversation context if user_id provided
        context = ""
        if user_id:
            context = self.context_manager.get_context_string(user_id, limit=3)
        
        # Try AI classification first (most accurate)
        if HAS_OPENAI or HAS_GEMINI:
            ai_result = self._classify_by_ai(message, context)
            if ai_result[1] >= self.confidence_threshold:
                return ai_result
        
        # Fallback to hybrid approach
        hybrid_result = self._classify_hybrid(message_lower, context)
        if hybrid_result[1] >= self.confidence_threshold:
            return hybrid_result
        
        # Final fallback to keyword matching
        keyword_result = self._classify_by_keywords(message_lower)
        if keyword_result[0] != "fallback":
            return keyword_result[0], max(keyword_result[1], 0.4)
        
        return "fallback", 0.0
    
    def _classify_by_ai(self, message: str, context: str = "") -> Tuple[str, float]:
        """
        Advanced AI-based intent classification
        
        Args:
            message (str): User message
            context (str): Conversation context
            
        Returns:
            Tuple[str, float]: (intent, confidence)
        """
        try:
            # Try OpenAI first
            if HAS_OPENAI and openai_client:
                return self._classify_with_openai(message, context)
            
            # Fallback to Gemini
            if HAS_GEMINI:
                return self._classify_with_gemini(message, context)
                
        except Exception as e:
            print(f"❌ AI classification error: {e}")
            
        return "fallback", 0.0
    
    def _classify_with_openai(self, message: str, context: str = "") -> Tuple[str, float]:
        """Enhanced OpenAI classification with context"""
        
        # Create comprehensive prompt with context
        prompt = f"""
        You are an expert intent classifier for XOFlowers, a premium flower shop in Moldova.
        
        CONVERSATION CONTEXT:
        {context if context else "No previous context"}
        
        CURRENT MESSAGE: "{message}"
        
        AVAILABLE INTENTS:
        1. find_product: Looking for flowers, bouquets, plants, gifts
        2. ask_question: General questions about business, hours, location
        3. subscribe: Want to subscribe to updates, newsletter, plans
        4. pay_for_product: Ready to pay, purchase, buy something
        5. greeting: Hello, good morning, starting conversation
        6. order_status: Check order status, where is my order
        7. complaint: Problems, issues, poor quality, complaints
        8. recommendation: Ask for recommendations, suggestions
        9. availability: Check if products are in stock
        10. delivery_info: Ask about delivery, shipping, costs
        11. cancel_order: Cancel or modify existing order
        12. price_inquiry: Ask about prices, costs, tariffs
        13. seasonal_offers: Ask about promotions, discounts, offers
        14. gift_suggestions: Ask for gift ideas for occasions
        15. care_instructions: How to care for flowers, maintenance
        16. bulk_orders: Large quantity orders, corporate orders
        17. farewell: Goodbye, thank you, ending conversation
        
        CLASSIFICATION RULES:
        - Consider the conversation context
        - Romanian language nuances
        - XOFlowers business context
        - User intent progression
        
        Respond with ONLY the intent name and confidence (0.0-1.0):
        Format: intent_name:confidence
        """
        
        try:
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=50,
                temperature=0.1
            )
            
            result = response.choices[0].message.content.strip()
            
            # Parse response
            if ':' in result:
                intent, confidence_str = result.split(':', 1)
                intent = intent.strip()
                try:
                    confidence = float(confidence_str.strip())
                    if intent in self.intents:
                        return intent, confidence
                except ValueError:
                    pass
            
            # Fallback parsing
            if result in self.intents:
                return result, 0.8
                
        except Exception as e:
            print(f"❌ OpenAI classification error: {e}")
            
        return "fallback", 0.0
    
    def _classify_with_gemini(self, message: str, context: str = "") -> Tuple[str, float]:
        """Enhanced Gemini classification with context"""
        
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f"""
            Classify this Romanian message for XOFlowers flower shop.
            
            Context: {context if context else "No context"}
            Message: "{message}"
            
            Available intents: find_product, ask_question, subscribe, pay_for_product, greeting, order_status, complaint, recommendation, availability, delivery_info, cancel_order, price_inquiry, seasonal_offers, gift_suggestions, care_instructions, bulk_orders, farewell
            
            Respond with: intent_name:confidence_score
            """
            
            response = model.generate_content(prompt)
            result = response.text.strip()
            
            # Parse response
            if ':' in result:
                intent, confidence_str = result.split(':', 1)
                intent = intent.strip()
                try:
                    confidence = float(confidence_str.strip())
                    if intent in self.intents:
                        return intent, confidence
                except ValueError:
                    pass
            
            # Fallback parsing
            if result in self.intents:
                return result, 0.7
                
        except Exception as e:
            print(f"❌ Gemini classification error: {e}")
            
        return "fallback", 0.0
    
    def _classify_hybrid(self, message: str, context: str = "") -> Tuple[str, float]:
        """
        Hybrid classification combining keywords and context
        
        Args:
            message (str): Lowercase message
            context (str): Conversation context
            
        Returns:
            Tuple[str, float]: (intent, confidence)
        """
        # Get keyword scores
        keyword_scores = self._get_keyword_scores(message)
        
        # Apply context boosting
        if context:
            keyword_scores = self._apply_context_boosting(keyword_scores, context)
        
        # Find best intent
        if keyword_scores:
            best_intent = max(keyword_scores, key=keyword_scores.get)
            max_score = keyword_scores[best_intent]
            
            # Normalize score to confidence
            confidence = min(max_score * 0.2, 1.0)  # Scale keyword score to confidence
            
            return best_intent, confidence
        
        return "fallback", 0.0
    
    def _get_keyword_scores(self, message: str) -> Dict[str, float]:
        """Calculate keyword-based scores for all intents"""
        scores = {}
        
        for intent, config in self.intents.items():
            score = 0
            keywords = config['keywords']
            priority = config['priority']
            
            for keyword in keywords:
                if keyword in message:
                    # Exact match gets higher score
                    if f" {keyword} " in f" {message} ":
                        score += 2.0
                    else:
                        score += 1.0
            
            if score > 0:
                # Apply priority weighting
                scores[intent] = score * (priority / 10.0)
        
        return scores
    
    def _apply_context_boosting(self, scores: Dict[str, float], context: str) -> Dict[str, float]:
        """Apply context-based boosting to intent scores"""
        context_lower = context.lower()
        
        # Boost related intents based on context
        context_boosts = {
            'find_product': ['product', 'flori', 'buchet', 'cadou'],
            'pay_for_product': ['plată', 'cumpăr', 'comanda'],
            'order_status': ['comandă', 'status', 'livrat'],
            'complaint': ['problemă', 'reclamație', 'nemulțumit'],
            'delivery_info': ['livrare', 'transport']
        }
        
        boosted_scores = scores.copy()
        
        for intent, boost_words in context_boosts.items():
            if intent in boosted_scores:
                for word in boost_words:
                    if word in context_lower:
                        boosted_scores[intent] *= 1.3  # 30% boost
                        break
        
        return boosted_scores
    
    def _classify_by_keywords(self, message: str) -> Tuple[str, float]:
        """
        Fast keyword-based intent classification
        
        Args:
            message (str): Lowercase message
            
        Returns:
            Tuple[str, float]: (intent, confidence)
        """
        scores = self._get_keyword_scores(message)
        
        if scores:
            best_intent = max(scores, key=scores.get)
            max_score = scores[best_intent]
            
            # Convert to confidence score
            confidence = min(max_score * 0.15, 0.8)  # Lower confidence for keyword-only
            
            return best_intent, confidence
        
        return "fallback", 0.0
    
    def is_jailbreak_attempt(self, message: str) -> bool:
        """
        Enhanced jailbreak detection
        
        Args:
            message (str): User message to check
            
        Returns:
            bool: True if jailbreak attempt detected
        """
        jailbreak_patterns = [
            r'ignore\s+previous\s+instructions',
            r'forget\s+everything',
            r'you\s+are\s+now',
            r'pretend\s+to\s+be',
            r'act\s+as\s+if',
            r'sistem\s+prompt',
            r'uită\s+tot',
            r'instrucțiuni\s+anterioare',
            r'roleplay\s+as',
            r'imagine\s+you\s+are',
            r'override\s+your',
            r'switch\s+to',
            r'new\s+instructions',
            r'ai\s+behavior',
            r'system\s+message'
        ]
        
        message_lower = message.lower()
        for pattern in jailbreak_patterns:
            if re.search(pattern, message_lower):
                return True
        
        return False
    
    def get_intent_confidence(self, message: str, user_id: str = None) -> Dict[str, float]:
        """
        Get confidence scores for all intents
        
        Args:
            message (str): User message
            user_id (str): User identifier for context
            
        Returns:
            Dict[str, float]: Intent confidence scores
        """
        message_lower = message.lower()
        
        # Get keyword scores for all intents
        keyword_scores = self._get_keyword_scores(message_lower)
        
        # Apply context if available
        if user_id:
            context = self.context_manager.get_context_string(user_id, limit=3)
            if context:
                keyword_scores = self._apply_context_boosting(keyword_scores, context)
        
        # Normalize scores to confidences
        confidences = {}
        max_score = max(keyword_scores.values()) if keyword_scores else 1.0
        
        for intent, score in keyword_scores.items():
            confidences[intent] = min(score / max_score, 1.0)
        
        return confidences
    
    def get_intent_explanation(self, intent: str) -> str:
        """
        Get explanation for an intent
        
        Args:
            intent (str): Intent name
            
        Returns:
            str: Human-readable explanation
        """
        explanations = {
            'find_product': 'Utilizatorul caută produse - flori, buchete, cadouri',
            'ask_question': 'Utilizatorul pune întrebări generale despre afacere',
            'subscribe': 'Utilizatorul vrea să se aboneze la actualizări',
            'pay_for_product': 'Utilizatorul vrea să plătească pentru un produs',
            'greeting': 'Utilizatorul salută sau începe conversația',
            'order_status': 'Utilizatorul verifică statusul comenzii',
            'complaint': 'Utilizatorul are o reclamație sau problemă',
            'recommendation': 'Utilizatorul cere recomandări',
            'availability': 'Utilizatorul verifică disponibilitatea produselor',
            'delivery_info': 'Utilizatorul întreabă despre livrare',
            'cancel_order': 'Utilizatorul vrea să anuleze comanda',
            'price_inquiry': 'Utilizatorul întreabă despre prețuri',
            'seasonal_offers': 'Utilizatorul întreabă despre oferte speciale',
            'gift_suggestions': 'Utilizatorul cere sugestii de cadouri',
            'care_instructions': 'Utilizatorul întreabă cum să îngrijească florile',
            'bulk_orders': 'Utilizatorul vrea să facă comenzi în cantități mari',
            'farewell': 'Utilizatorul se ia la revedere'
        }
        
        return explanations.get(intent, 'Intenție necunoscută')
    
    def update_context(self, user_id: str, message: str, intent: str, confidence: float):
        """
        Update conversation context with new interaction
        
        Args:
            user_id (str): User identifier
            message (str): User message
            intent (str): Classified intent
            confidence (float): Classification confidence
        """
        # This will be updated by the action handler with the bot response
        pass
