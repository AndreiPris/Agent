"""
Security Filters Module
Handles censorship, jailbreak protection, and rate limiting
"""

import os
import sys
import re
from typing import Dict, List, Optional
from datetime import datetime, timedelta

# Add config to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'config'))

from settings import SECURITY


class SecurityFilter:
    """
    Handles security filtering and protection mechanisms
    """
    
    def __init__(self):
        """Initialize security filter"""
        self.security_config = SECURITY
        self.censorship_keywords = self._load_censorship_keywords()
        self.jailbreak_patterns = self._load_jailbreak_patterns()
        self.rate_limiter = RateLimiter()
        
    def _load_censorship_keywords(self) -> List[str]:
        """Load censorship keywords"""
        return [
            "cuvint_ofensator_1",
            "cuvint_ofensator_2",
            # Add more offensive words as needed
        ]
    
    def _load_jailbreak_patterns(self) -> List[str]:
        """Load jailbreak detection patterns"""
        return [
            r"ignore\s+previous\s+instructions",
            r"ignore\s+all\s+previous",
            r"forget\s+everything",
            r"you\s+are\s+now",
            r"new\s+role",
            r"pretend\s+to\s+be",
            r"act\s+as\s+if",
        ]
    
    def is_safe_message(self, message: str) -> bool:
        """
        Alias for is_message_safe for backward compatibility
        
        Args:
            message (str): User message to check
            
        Returns:
            bool: True if message is safe
        """
        return self.is_message_safe(message)
    
    def is_message_safe(self, message: str) -> bool:
        """
        Check if message is safe (no offensive content or jailbreak attempts)
        
        Args:
            message (str): User message to check
            
        Returns:
            bool: True if message is safe
        """
        if not self.security_config['enable_censorship']:
            return True
            
        # Check for offensive content
        if self._contains_offensive_content(message):
            return False
            
        # Check for jailbreak attempts
        if self.security_config['enable_jailbreak_protection']:
            if self._is_jailbreak_attempt(message):
                return False
        
        return True
    
    def _contains_offensive_content(self, message: str) -> bool:
        """
        Check if message contains offensive content
        
        Args:
            message (str): Message to check
            
        Returns:
            bool: True if offensive content found
        """
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in self.censorship_keywords)
    
    def _is_jailbreak_attempt(self, message: str) -> bool:
        """
        Check if message is a jailbreak attempt
        
        Args:
            message (str): Message to check
            
        Returns:
            bool: True if jailbreak attempt detected
        """
        message_lower = message.lower()
        return any(re.search(pattern, message_lower) for pattern in self.jailbreak_patterns)
    
    def check_rate_limit(self, user_id: str) -> bool:
        """
        Check if user has exceeded rate limits
        
        Args:
            user_id (str): User identifier
            
        Returns:
            bool: True if within rate limits
        """
        return self.rate_limiter.is_allowed(user_id)
    
    def get_violation_response(self, violation_type: str) -> str:
        """
        Get appropriate response for security violations
        
        Args:
            violation_type (str): Type of violation (censorship, jailbreak, rate_limit)
            
        Returns:
            str: Response message
        """
        responses = {
            "censorship": "Îmi pare rău, nu pot răspunde la acest tip de mesaj. Sunt aici să vă ajut cu produsele și serviciile XOFlowers! 🌸",
            "jailbreak": "Sunt aici să vă ajut doar cu XOFlowers! 🌸 Cum vă pot ajuta cu florile noastre?",
            "rate_limit": "Vă rugăm să așteptați puțin înainte de a trimite alt mesaj. Mulțumesc pentru înțelegere! 🌸"
        }
        return responses.get(violation_type, "Vă rugăm să respectați regulile de utilizare.")


class RateLimiter:
    """
    Simple rate limiting implementation
    """
    
    def __init__(self):
        """Initialize rate limiter"""
        self.user_requests = {}
        self.config = SECURITY['rate_limiting']
    
    def is_allowed(self, user_id: str) -> bool:
        """
        Check if user is within rate limits
        
        Args:
            user_id (str): User identifier
            
        Returns:
            bool: True if allowed
        """
        now = datetime.now()
        
        if user_id not in self.user_requests:
            self.user_requests[user_id] = []
        
        # Clean old requests
        self.user_requests[user_id] = [
            req_time for req_time in self.user_requests[user_id]
            if now - req_time < timedelta(hours=1)
        ]
        
        # Check limits
        minute_ago = now - timedelta(minutes=1)
        recent_requests = [
            req_time for req_time in self.user_requests[user_id]
            if req_time > minute_ago
        ]
        
        # Check minute limit
        if len(recent_requests) >= self.config['max_requests_per_minute']:
            return False
            
        # Check hour limit
        if len(self.user_requests[user_id]) >= self.config['max_requests_per_hour']:
            return False
        
        # Add current request
        self.user_requests[user_id].append(now)
        return True
