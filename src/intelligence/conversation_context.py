"""
Conversation Context System
Manages conversation history, context, and memory for personalized interactions
"""

import os
import json
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict


@dataclass
class ConversationTurn:
    """Single conversation turn"""
    user_message: str
    bot_response: str
    intent: str
    timestamp: datetime
    user_id: str
    confidence: float = 0.0
    metadata: Dict[str, Any] = None


@dataclass
class UserProfile:
    """User profile with preferences and history"""
    user_id: str
    name: Optional[str] = None
    preferences: Dict[str, Any] = None
    purchase_history: List[Dict[str, Any]] = None
    conversation_count: int = 0
    first_interaction: datetime = None
    last_interaction: datetime = None
    favorite_products: List[str] = None
    budget_range: Optional[str] = None
    special_occasions: List[str] = None


class ConversationContext:
    """
    Manages conversation context and user profiles
    """
    
    def __init__(self, storage_path: str = "data"):
        """
        Initialize conversation context manager
        
        Args:
            storage_path (str): Path to store conversation data
        """
        self.storage_path = storage_path
        self.contexts: Dict[str, List[ConversationTurn]] = {}
        self.user_profiles: Dict[str, UserProfile] = {}
        self.max_context_length = 20  # Keep last 20 turns
        self.context_window = timedelta(hours=2)  # Context expires after 2 hours
        
        # Ensure storage directory exists
        os.makedirs(storage_path, exist_ok=True)
        
        # Load existing data
        self._load_contexts()
        self._load_user_profiles()
    
    def add_turn(self, user_id: str, user_message: str, bot_response: str, 
                 intent: str, confidence: float = 0.0, metadata: Dict[str, Any] = None):
        """
        Add a conversation turn to context
        
        Args:
            user_id (str): User identifier
            user_message (str): User's message
            bot_response (str): Bot's response
            intent (str): Classified intent
            confidence (float): Classification confidence
            metadata (Dict): Additional metadata
        """
        turn = ConversationTurn(
            user_message=user_message,
            bot_response=bot_response,
            intent=intent,
            timestamp=datetime.now(),
            user_id=user_id,
            confidence=confidence,
            metadata=metadata or {}
        )
        
        if user_id not in self.contexts:
            self.contexts[user_id] = []
        
        self.contexts[user_id].append(turn)
        
        # Maintain context window
        self._cleanup_old_context(user_id)
        
        # Update user profile
        self._update_user_profile(user_id, turn)
        
        # Persist data
        self._save_contexts()
        self._save_user_profiles()
    
    def get_context(self, user_id: str, limit: int = 5) -> List[ConversationTurn]:
        """
        Get conversation context for a user
        
        Args:
            user_id (str): User identifier
            limit (int): Number of recent turns to return
            
        Returns:
            List[ConversationTurn]: Recent conversation turns
        """
        if user_id not in self.contexts:
            return []
        
        # Filter recent context within time window
        now = datetime.now()
        recent_turns = [
            turn for turn in self.contexts[user_id]
            if now - turn.timestamp < self.context_window
        ]
        
        return recent_turns[-limit:] if recent_turns else []
    
    def get_context_string(self, user_id: str, limit: int = 5) -> str:
        """
        Get formatted context string for AI prompts
        
        Args:
            user_id (str): User identifier
            limit (int): Number of recent turns to include
            
        Returns:
            str: Formatted context string
        """
        context = self.get_context(user_id, limit)
        
        if not context:
            return "No previous conversation context."
        
        context_lines = []
        for turn in context:
            context_lines.append(f"User: {turn.user_message}")
            context_lines.append(f"Bot: {turn.bot_response}")
            context_lines.append(f"Intent: {turn.intent}")
            context_lines.append("---")
        
        return "\n".join(context_lines)
    
    def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """
        Get user profile
        
        Args:
            user_id (str): User identifier
            
        Returns:
            Optional[UserProfile]: User profile if exists
        """
        return self.user_profiles.get(user_id)
    
    def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]):
        """
        Update user preferences
        
        Args:
            user_id (str): User identifier
            preferences (Dict): User preferences to update
        """
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = UserProfile(user_id=user_id)
        
        profile = self.user_profiles[user_id]
        if profile.preferences is None:
            profile.preferences = {}
        
        profile.preferences.update(preferences)
        self._save_user_profiles()
    
    def get_user_intent_history(self, user_id: str, limit: int = 10) -> List[str]:
        """
        Get user's recent intent history
        
        Args:
            user_id (str): User identifier
            limit (int): Number of recent intents to return
            
        Returns:
            List[str]: Recent intents
        """
        context = self.get_context(user_id, limit)
        return [turn.intent for turn in context]
    
    def is_returning_user(self, user_id: str) -> bool:
        """
        Check if user is returning (has previous conversations)
        
        Args:
            user_id (str): User identifier
            
        Returns:
            bool: True if returning user
        """
        profile = self.get_user_profile(user_id)
        return profile is not None and profile.conversation_count > 0
    
    def get_personalized_greeting(self, user_id: str) -> str:
        """
        Get personalized greeting based on user history
        
        Args:
            user_id (str): User identifier
            
        Returns:
            str: Personalized greeting
        """
        profile = self.get_user_profile(user_id)
        
        if not profile or profile.conversation_count == 0:
            return "🌸 Bună ziua! Bine ați venit la XOFlowers! Sunt aici să vă ajut să găsiți florile perfecte."
        
        name_part = f" {profile.name}" if profile.name else ""
        
        if profile.conversation_count == 1:
            return f"🌸 Bună ziua din nou{name_part}! Mă bucur să vă revăd la XOFlowers!"
        
        return f"🌸 Bună ziua{name_part}! Îmi pare bine să vă revăd! Cum vă pot ajuta astăzi?"
    
    def _cleanup_old_context(self, user_id: str):
        """Clean up old context entries"""
        if user_id not in self.contexts:
            return
        
        # Remove entries older than context window
        now = datetime.now()
        self.contexts[user_id] = [
            turn for turn in self.contexts[user_id]
            if now - turn.timestamp < self.context_window
        ]
        
        # Limit to max context length
        if len(self.contexts[user_id]) > self.max_context_length:
            self.contexts[user_id] = self.contexts[user_id][-self.max_context_length:]
    
    def _update_user_profile(self, user_id: str, turn: ConversationTurn):
        """Update user profile with new turn"""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = UserProfile(
                user_id=user_id,
                first_interaction=turn.timestamp,
                preferences={},
                purchase_history=[],
                favorite_products=[],
                special_occasions=[]
            )
        
        profile = self.user_profiles[user_id]
        profile.last_interaction = turn.timestamp
        profile.conversation_count += 1
        
        # Extract preferences from conversation
        if turn.intent == "find_product":
            self._extract_product_preferences(profile, turn)
        elif turn.intent == "gift_suggestions":
            self._extract_gift_preferences(profile, turn)
    
    def _extract_product_preferences(self, profile: UserProfile, turn: ConversationTurn):
        """Extract product preferences from conversation"""
        message = turn.user_message.lower()
        
        # Extract flower types
        flowers = ["trandafir", "bujor", "garoafa", "lalele", "crizanteme"]
        for flower in flowers:
            if flower in message:
                if flower not in profile.favorite_products:
                    profile.favorite_products.append(flower)
        
        # Extract colors
        colors = ["roșu", "roz", "alb", "galben", "violet"]
        for color in colors:
            if color in message:
                if "favorite_colors" not in profile.preferences:
                    profile.preferences["favorite_colors"] = []
                if color not in profile.preferences["favorite_colors"]:
                    profile.preferences["favorite_colors"].append(color)
    
    def _extract_gift_preferences(self, profile: UserProfile, turn: ConversationTurn):
        """Extract gift preferences from conversation"""
        message = turn.user_message.lower()
        
        occasions = ["aniversare", "valentine", "mama", "dragobete", "zi de naștere"]
        for occasion in occasions:
            if occasion in message:
                if occasion not in profile.special_occasions:
                    profile.special_occasions.append(occasion)
    
    def _load_contexts(self):
        """Load conversation contexts from storage"""
        context_file = os.path.join(self.storage_path, "contexts.json")
        try:
            if os.path.exists(context_file):
                with open(context_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for user_id, turns_data in data.items():
                        self.contexts[user_id] = [
                            ConversationTurn(
                                user_message=turn['user_message'],
                                bot_response=turn['bot_response'],
                                intent=turn['intent'],
                                timestamp=datetime.fromisoformat(turn['timestamp']),
                                user_id=turn['user_id'],
                                confidence=turn.get('confidence', 0.0),
                                metadata=turn.get('metadata', {})
                            )
                            for turn in turns_data
                        ]
        except Exception as e:
            print(f"❌ Error loading contexts: {e}")
    
    def _save_contexts(self):
        """Save conversation contexts to storage"""
        context_file = os.path.join(self.storage_path, "contexts.json")
        try:
            data = {}
            for user_id, turns in self.contexts.items():
                data[user_id] = [
                    {
                        'user_message': turn.user_message,
                        'bot_response': turn.bot_response,
                        'intent': turn.intent,
                        'timestamp': turn.timestamp.isoformat(),
                        'user_id': turn.user_id,
                        'confidence': turn.confidence,
                        'metadata': turn.metadata
                    }
                    for turn in turns
                ]
            
            with open(context_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ Error saving contexts: {e}")
    
    def _load_user_profiles(self):
        """Load user profiles from storage"""
        profile_file = os.path.join(self.storage_path, "profiles.json")
        try:
            if os.path.exists(profile_file):
                with open(profile_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for user_id, profile_data in data.items():
                        self.user_profiles[user_id] = UserProfile(
                            user_id=profile_data['user_id'],
                            name=profile_data.get('name'),
                            preferences=profile_data.get('preferences', {}),
                            purchase_history=profile_data.get('purchase_history', []),
                            conversation_count=profile_data.get('conversation_count', 0),
                            first_interaction=datetime.fromisoformat(profile_data['first_interaction']) if profile_data.get('first_interaction') else None,
                            last_interaction=datetime.fromisoformat(profile_data['last_interaction']) if profile_data.get('last_interaction') else None,
                            favorite_products=profile_data.get('favorite_products', []),
                            budget_range=profile_data.get('budget_range'),
                            special_occasions=profile_data.get('special_occasions', [])
                        )
        except Exception as e:
            print(f"❌ Error loading profiles: {e}")
    
    def _save_user_profiles(self):
        """Save user profiles to storage"""
        profile_file = os.path.join(self.storage_path, "profiles.json")
        try:
            data = {}
            for user_id, profile in self.user_profiles.items():
                data[user_id] = {
                    'user_id': profile.user_id,
                    'name': profile.name,
                    'preferences': profile.preferences,
                    'purchase_history': profile.purchase_history,
                    'conversation_count': profile.conversation_count,
                    'first_interaction': profile.first_interaction.isoformat() if profile.first_interaction else None,
                    'last_interaction': profile.last_interaction.isoformat() if profile.last_interaction else None,
                    'favorite_products': profile.favorite_products,
                    'budget_range': profile.budget_range,
                    'special_occasions': profile.special_occasions
                }
            
            with open(profile_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ Error saving profiles: {e}")
