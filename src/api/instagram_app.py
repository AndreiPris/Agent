#!/usr/bin/env python3
"""
XOFlowers Instagram Bot
Task Lucian: Conectează core_logic.py cu Instagram prin webhooks

Autor: Lucian (Webhook)
Data: 2025
"""

import os
import sys
import logging
import json
import hashlib
import hmac
from typing import Dict, Any, Optional, List
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import requests
import time

# Adaugă calea către modulele noastre
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from intelligence.intent_classifier import IntentClassifier
    from intelligence.action_handler import ActionHandler
    from security.filters import SecurityFilter
except ImportError as e:
    print(f"❌ Eroare la importul modulelor: {e}")
    print("Asigură-te că toate modulele există în structura nouă")
    sys.exit(1)

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class XOFlowersInstagramBot:
    """
    Botul Instagram pentru XOFlowers
    Gestionează webhook-urile de la Meta și conectează cu AI-ul
    """
    
    def __init__(self, debug: bool = False):
        # Store debug flag
        self.debug = debug
        
        # Configurări Instagram/Meta
        self.access_token = os.getenv('INSTAGRAM_PAGE_ACCESS_TOKEN')
        self.verify_token = os.getenv('INSTAGRAM_VERIFY_TOKEN')
        self.app_secret = os.getenv('META_APP_SECRET')
        self.app_id = os.getenv('INSTAGRAM_APP_ID')
        
        # Validare configurații
        if not self.access_token:
            raise ValueError("INSTAGRAM_PAGE_ACCESS_TOKEN lipsește din .env")
        if not self.verify_token:
            raise ValueError("INSTAGRAM_VERIFY_TOKEN lipsește din .env")
        if not self.app_secret:
            raise ValueError("META_APP_SECRET lipsește din .env")
            
        # Conversații active pentru context
        self.active_conversations = {}
        
        # Store conversation history for each user (similar to Telegram bot)
        self.user_conversations = {}
        
        # Initialize AI components
        try:
            self.intent_classifier = IntentClassifier()
            self.action_handler = ActionHandler()
            self.security_filter = SecurityFilter()
            logger.info("✅ AI Components inițializate cu succes")
        except Exception as e:
            logger.error(f"❌ Eroare la inițializarea AI: {e}")
            raise
        
        # Flask app pentru webhook-uri
        self.app = Flask(__name__)
        
        # Middleware pentru ngrok compatibility
        @self.app.before_request
        def handle_ngrok_headers():
            """
            Gestionează header-ele ngrok pentru compatibilitate cu Meta webhooks
            """
            # Adaugă header-ul pentru a omite warning page-ul ngrok
            if 'ngrok-free.app' in request.url or 'ngrok.io' in request.url:
                request.environ['HTTP_NGROK_SKIP_BROWSER_WARNING'] = 'true'
        
        @self.app.after_request
        def add_ngrok_headers(response):
            """
            Adaugă header-e pentru compatibilitate cu ngrok
            """
            if 'ngrok-free.app' in request.url or 'ngrok.io' in request.url:
                response.headers['ngrok-skip-browser-warning'] = 'true'
                response.headers['Access-Control-Allow-Origin'] = '*'
                response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
                response.headers['Access-Control-Allow-Headers'] = 'Content-Type, ngrok-skip-browser-warning'
            return response
        
        # Statistici
        self.message_count = 0
        
        # Configurează rutele
        self._setup_routes()
        
        logger.info("📱 XOFlowers Instagram Bot inițializat")
    
    def _setup_routes(self):
        """
        Configurează rutele Flask pentru webhook-uri
        """
        
        @self.app.route('/webhook', methods=['GET'])
        def verify_webhook():
            """
            Verifică webhook-ul la configurare (Meta requirement)
            """
            mode = request.args.get('hub.mode')
            token = request.args.get('hub.verify_token')
            challenge = request.args.get('hub.challenge')
            
            if mode == 'subscribe' and token == self.verify_token:
                logger.info("✅ Webhook verificat cu succes")
                return challenge
            else:
                logger.warning("❌ Verificarea webhook-ului a eșuat")
                return 'Failed verification', 403
        
        @self.app.route('/webhook', methods=['POST'])
        def handle_webhook():
            """
            Gestionează webhook-urile primite de la Instagram
            """
            try:
                # Validează semnătura (opțional, dar recomandat pentru securitate)
                if self.app_secret:
                    if not self._verify_signature(request.data, request.headers.get('X-Hub-Signature-256')):
                        logger.warning("❌ Semnătură invalidă pentru webhook")
                        return 'Invalid signature', 403
                
                # Procesează datele
                data = request.get_json()
                logger.info(f"📨 Webhook primit: {json.dumps(data, indent=2)}")
                
                # Procesează mesajele
                if data.get('object') == 'instagram':
                    for entry in data.get('entry', []):
                        self._process_entry(entry)
                
                return 'OK', 200
                
            except Exception as e:
                logger.error(f"❌ Eroare la procesarea webhook-ului: {e}")
                return 'Internal Server Error', 500
        
        @self.app.route('/health', methods=['GET'])
        def health_check():
            """
            Health check pentru monitoring
            """
            return jsonify({
                'status': 'healthy',
                'service': 'XOFlowers Instagram Bot',
                'messages_processed': self.message_count,
                'active_conversations': len(self.user_conversations)
            })
        
        @self.app.route('/stats', methods=['GET'])
        def get_stats():
            """
            Statistici detaliate
            """
            return jsonify({
                'total_messages': self.message_count,
                'active_users': len(self.user_conversations),
                'ai_status': 'enhanced_core_logic_active',
                'instagram_configured': bool(self.access_token and self.verify_token)
            })
    
    def _verify_signature(self, payload: bytes, signature: str) -> bool:
        """
        Verifică semnătura webhook-ului pentru securitate
        """
        if not signature or not self.app_secret:
            return True  # Skip validation if not configured
        
        try:
            # Calculează semnătura așteptată
            expected_signature = 'sha256=' + hmac.new(
                self.app_secret.encode('utf-8'),
                payload,
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(expected_signature, signature)
        except Exception as e:
            logger.error(f"Eroare la verificarea semnăturii: {e}")
            return False
    
    def _process_entry(self, entry: Dict[str, Any]):
        """
        Procesează o intrare din webhook
        """
        try:
            # Verifică dacă sunt mesaje
            messaging = entry.get('messaging', [])
            
            for message_event in messaging:
                if 'message' in message_event:
                    self._handle_message(message_event)
                elif 'postback' in message_event:
                    self._handle_postback(message_event)
                    
        except Exception as e:
            logger.error(f"Eroare la procesarea intrării: {e}")
    
    def _handle_message(self, message_event: Dict[str, Any]):
        """
        Gestionează mesajele primite
        AICI SE CONECTEAZĂ CU ENHANCED_CORE_LOGIC.PY!
        """
        try:
            sender_id = message_event['sender']['id']
            message_data = message_event.get('message', {})
            
            # Verifică dacă e mesaj text
            if 'text' in message_data:
                user_message = message_data['text']
                self.message_count += 1
                
                logger.info(f"👤 Mesaj de la {sender_id}: {user_message}")
                
                # Initialize conversation history if needed
                if sender_id not in self.user_conversations:
                    self.user_conversations[sender_id] = []
                
                # Get conversation history for this user
                chat_history = self.user_conversations[sender_id]
                
                # AICI SE ÎNTÂMPLĂ MAGIA - Apelăm sistemul AI enhanced!
                # 1. Verifică securitatea mesajului
                if not self.security_filter.is_message_safe(user_message):
                    ai_response = "❌ Mesajul tău conține conținut nepermis. Te rog să reformulezi."
                else:
                    # 2. Clasifică intenția
                    intent = self.intent_classifier.classify_intent(user_message)
                    
                    # 3. Procesează acțiunea
                    ai_response = self.action_handler.handle_action(intent, user_message)
                
                # Add messages to conversation history
                self.user_conversations[sender_id].append(f"User: {user_message}")
                self.user_conversations[sender_id].append(f"Bot: {ai_response}")
                
                # Keep conversation history manageable (last 20 messages)
                if len(self.user_conversations[sender_id]) > 20:
                    self.user_conversations[sender_id] = self.user_conversations[sender_id][-20:]
                
                # Trimite răspunsul înapoi
                self._send_message(sender_id, ai_response)
                
                logger.info(f"🤖 Răspuns trimis către {sender_id}")
            
            elif 'attachments' in message_data:
                # Gestionează anexele (poze, etc.)
                self._handle_attachment(sender_id, message_data['attachments'])
            
        except Exception as e:
            logger.error(f"Eroare la gestionarea mesajului: {e}")
            # Trimite mesaj de eroare
            self._send_error_message(sender_id)
    
    def _handle_postback(self, postback_event: Dict[str, Any]):
        """
        Gestionează postback-urile (butoane apăsate)
        """
        try:
            sender_id = postback_event['sender']['id']
            postback_payload = postback_event['postback'].get('payload', '')
            
            logger.info(f"🔘 Postback de la {sender_id}: {postback_payload}")
            
            # Procesează diferite tipuri de postback-uri
            if postback_payload == 'GET_STARTED':
                response = self._get_welcome_message()
            elif postback_payload == 'VIEW_CATALOG':
                response = self._get_catalog_message()
            elif postback_payload == 'CONTACT_INFO':
                response = self._get_contact_message()
            else:
                # Initialize conversation history if needed
                if sender_id not in self.user_conversations:
                    self.user_conversations[sender_id] = []
                
                # Tratează ca mesaj normal cu enhanced core logic
                postback_message = f"Utilizatorul a apăsat: {postback_payload}"
                
                # Verifică securitatea și procesează
                if not self.security_filter.is_message_safe(postback_message):
                    response = "❌ Acțiunea nu este permisă."
                else:
                    intent = self.intent_classifier.classify_intent(postback_message)
                    response = self.action_handler.handle_action(intent, postback_message)
            
            self._send_message(sender_id, response)
            
        except Exception as e:
            logger.error(f"Eroare la gestionarea postback-ului: {e}")
    
    def _handle_attachment(self, sender_id: str, attachments: List[Dict]):
        """
        Gestionează anexele (poze, stickere, etc.)
        """
        attachment_types = [att.get('type') for att in attachments]
        
        if 'image' in attachment_types:
            message = """📸 Îmi pare rău, momentan nu pot analiza imagini, dar pot să te ajut cu descrieri text!

Spune-mi ce fel de flori cauți și îți voi găsi exact ce ai nevoie! 🌸

Exemple:
• "Vreau trandafiri roșii pentru Valentine"
• "Buchete albe pentru nuntă"
• "Ceva frumos sub 1000 lei" """
        else:
            message = """🤖 Îmi pare rău, momentan pot răspunde doar la mesaje text.

Scrie-mi în cuvinte ce flori cauți și îți voi găsi exact ce ai nevoie! 🌸"""
        
        self._send_message(sender_id, message)
    
    def _send_message(self, recipient_id: str, message_text: str):
        """
        Trimite un mesaj către utilizator prin Instagram API
        """
        if not self.access_token:
            logger.warning("⚠️  Access token pentru Instagram nu este configurat")
            return
        
        url = f"https://graph.facebook.com/v18.0/me/messages"
        
        payload = {
            'recipient': {'id': recipient_id},
            'message': {'text': message_text},
            'access_token': self.access_token
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                logger.info(f"✅ Mesaj trimis cu succes către {recipient_id}")
            else:
                logger.error(f"❌ Eroare la trimiterea mesajului: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"❌ Eroare la apelul API Instagram: {e}")
    
    def _send_error_message(self, recipient_id: str):
        """
        Trimite mesaj de eroare către utilizator
        """
        error_message = """😔 Îmi pare rău, am întâmpinat o mică problemă tehnică.

Te rog să încerci din nou sau contactează-ne direct:
📞 [Numărul de telefon]
🌐 xoflowers.md

Îmi pare rău pentru inconvenient! 🌸"""
        
        self._send_message(recipient_id, error_message)
    
    def _get_welcome_message(self) -> str:
        """
        Mesajul de bun venit pentru utilizatorii noi
        """
        return """🌸 **Bună și bun venit la XOFlowers!** 🌸

Eu sunt asistentul tău virtual și sunt aici să te ajut să găsești florile perfecte pentru orice ocazie specială.

**Ce pot face pentru tine:**
🔍 Căutare flori după preferințe
💰 Recomandări în orice buget  
🎨 Filtrare după culori
🎉 Sugestii pentru ocazii speciale

**Începe pur și simplu să îmi spui ce cauți!**

*Exemple:*
• "Vreau trandafiri roșii pentru Valentine"
• "Caut buchete albe sub 1000 lei"
• "Am nevoie de flori pentru aniversare"

Cu ce te pot ajuta? 😊"""
    
    def _get_catalog_message(self) -> str:
        """
        Mesajul cu catalogul
        """
        return """🌸 **Catalogul XOFlowers** 🌸

**Categoriile noastre principale:**

🌹 **Trandafiri** - Clasici și eleganți
🌺 **Bujori** - Pentru ocazii speciale  
🌼 **Buchete Mixte** - Combinații creative
🎁 **Premium** - Aranjamente exclusive
💍 **Pentru Ocazii** - Valentine, Nunți, Aniversări

Spune-mi ce te interesează și îți voi arăta opțiunile perfecte! 🌟

Sau vizitează: xoflowers.md"""
    
    def _get_contact_message(self) -> str:
        """
        Mesajul cu informațiile de contact
        """
        return """📞 **Contactează XOFlowers** 📞

🏪 **Magazin:** Chișinău, Moldova
⏰ **Program:** 08:00 - 20:00 (Lun-Dom)
🌐 **Website:** xoflowers.md
📧 **Email:** comenzi@xoflowers.md

🚚 **Livrare rapidă în toată Moldova**
💳 **Plata: numerar sau card**

Pentru comenzi urgente, contactează-ne direct! 🌹"""
    
    def run(self, host='0.0.0.0', port=5000, debug=False):
        """
        Pornește serverul Flask pentru webhook-uri
        """
        logger.info(f"🚀 Pornesc Instagram Bot server pe {host}:{port}")
        
        if not self.access_token:
            logger.warning("⚠️  Instagram nu este configurat complet - bot în modul demo")
        
        self.app.run(host=host, port=port, debug=debug)

def main():
    """
    Funcția principală - Instagram Bot cu Enhanced AI
    """
    print("📱 XOFlowers Instagram Bot - Enhanced cu OpenAI + Gemini")
    print("=" * 60)
    
    try:
        # Verifică configurările
        access_token = os.getenv('INSTAGRAM_PAGE_ACCESS_TOKEN')
        verify_token = os.getenv('INSTAGRAM_VERIFY_TOKEN')
        
        if not verify_token:
            print("❌ INSTAGRAM_VERIFY_TOKEN nu este setat în .env!")
            print("\nPentru a configura Instagram Bot:")
            print("   1. Creează o aplicație Meta/Facebook")
            print("   2. Configurează Instagram Basic Display")
            print("   3. Adaugă token-urile în .env")
            print("   4. Configurează webhook-ul să pointeze către acest server")
            return
        
        # Creează botul
        bot = XOFlowersInstagramBot()
        
        print("\n🎉 Instagram Bot configurat cu Enhanced AI!")
        print(f"   Verify Token: {verify_token[:10]}...")
        if access_token:
            print(f"   Access Token: {access_token[:10]}...")
        else:
            print("   ⚠️  Access Token nu este setat - modul demo")
        
        print("\n🌐 Pornesc serverul webhook...")
        print("   URL pentru Meta: https://your-domain.com/webhook")
        print("   Health check: http://localhost:5001/health")
        print("   Statistici: http://localhost:5001/stats")
        
        # Pornește serverul pe portul specificat în .env
        port = int(os.getenv('WEBHOOK_PORT', 5001))
        bot.run(port=port, debug=os.getenv('DEBUG', 'False').lower() == 'true')
        
    except KeyboardInterrupt:
        print("\n⏹️  Server oprit de utilizator")
    except Exception as e:
        logger.error(f"❌ Eroare critică: {e}")
        print(f"\n❌ Eroare: {e}")

if __name__ == "__main__":
    main()
