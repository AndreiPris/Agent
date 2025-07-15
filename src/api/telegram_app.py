#!/usr/bin/env python3
"""
Enhanced XOFlowers Telegram Bot
Advanced conversational AI with context awareness and personalization
"""

import os
import logging
import sys
from typing import Dict, List
import asyncio
from telegram import Update, BotCommand
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    filters, 
    ContextTypes,
    CallbackContext
)
from dotenv import load_dotenv
import json
from datetime import datetime

# Add path to our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from intelligence.intent_classifier import IntentClassifier
    from intelligence.action_handler import ActionHandler
    from intelligence.conversation_context import ConversationContext
    from security.filters import SecurityFilter
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure all modules exist in the new structure")
    sys.exit(1)

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class XOFlowersTelegramBot:
    """Enhanced Telegram Bot with AI-powered conversations and context awareness"""
    
    def __init__(self, debug: bool = False):
        """Initialize the enhanced Telegram bot"""
        self.debug = debug
        
        # Get bot token from environment
        token = os.getenv('TELEGRAM_BOT_TOKEN')
        
        if not token:
            raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables")
        
        self.token = token
        self.application = Application.builder().token(token).build()
        
        # Initialize AI components
        self.intent_classifier = IntentClassifier()
        self.action_handler = ActionHandler()
        self.context_manager = ConversationContext()
        self.security_filter = SecurityFilter()
        
        # User statistics
        self.user_stats = {}
        
        # Setup handlers
        self.setup_handlers()
        
        logger.info("🤖 Enhanced XOFlowers Telegram Bot initialized successfully")
    
    def setup_handlers(self):
        """Setup all message and command handlers"""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("menu", self.menu_command))
        self.application.add_handler(CommandHandler("contact", self.contact_command))
        self.application.add_handler(CommandHandler("oferinte", self.offers_command))
        self.application.add_handler(CommandHandler("preturi", self.prices_command))
        
        # Message handlers
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )
        
        # Error handler
        self.application.add_error_handler(self.error_handler)
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Enhanced start command with personalized greeting"""
        user = update.effective_user
        user_id = str(user.id)
        
        # Register user
        if user_id not in self.user_stats:
            self.user_stats[user_id] = {
                'name': user.first_name,
                'messages_count': 0,
                'started_at': datetime.now().isoformat()
            }
        
        # Get personalized greeting
        greeting = self.context_manager.get_personalized_greeting(user_id)
        
        welcome_message = f"""🌸 **Bună, {user.first_name}!** 

{greeting}

**🌺 Cum te pot ajuta:**
💐 Căutare produse: "Vreau trandafiri roșii"
❓ Întrebări: "Ce program aveți?"
📧 Abonamente: "Vreau să mă abonez"
💳 Comenzi: "Cum pot plăti?"

**🌸 Comenzi disponibile:**
• /menu - Meniul principal
• /oferinte - Oferte speciale
• /preturi - Lista prețuri
• /contact - Informații contact

Începe conversația spunându-mi ce cauți! 🌺"""
        
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
        logger.info(f"👤 Start command: {user.first_name} (ID: {user_id})")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Enhanced message handler with AI and context awareness"""
        user = update.effective_user
        user_id = str(user.id)
        message = update.message.text
        
        # Update user stats
        if user_id not in self.user_stats:
            self.user_stats[user_id] = {
                'name': user.first_name,
                'messages_count': 0,
                'started_at': datetime.now().isoformat()
            }
        self.user_stats[user_id]['messages_count'] += 1
        
        try:
            # Security check
            if not self.security_filter.is_safe_message(message):
                await update.message.reply_text(
                    "🌸 Îmi pare rău, dar prefer să păstrăm conversația profesională și elegantă. \n\nCum vă pot ajuta cu serviciile XOFlowers?"
                )
                return
            
            # Process message with enhanced AI
            response, intent, confidence = self.action_handler.handle_message(message, user_id)
            
            # Log interaction
            logger.info(f"📨 Message from {user.first_name}: '{message}' -> Intent: {intent} (confidence: {confidence:.2f})")
            
            # Send response
            await update.message.reply_text(response, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"❌ Error handling message: {e}")
            await update.message.reply_text(
                "🌸 Îmi pare rău, am întâmpinat o problemă tehnică. Vă rugăm să încercați din nou sau contactați direct +373 22 123 456."
            )
    
    async def menu_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Main menu command"""
        menu_text = """
🌸 **Meniul Principal XOFlowers**

🌺 **Servicii disponibile:**
• 💐 Căutare produse și recomandări
• 📋 Verificare comenzi și status
• 💰 Informații prețuri și oferte
• 🚚 Detalii livrare
• 📞 Contact și suport

🌸 **Comenzi rapide:**
• /oferinte - Oferte speciale actuale
• /preturi - Lista completă prețuri
• /contact - Informații contact

💫 *Sau începeți direct conversația spunându-mi ce căutați!*
        """
        await update.message.reply_text(menu_text, parse_mode='Markdown')
    
    async def offers_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Special offers command"""
        response = self.action_handler.handle_seasonal_offers("oferte speciale")
        await update.message.reply_text(response, parse_mode='Markdown')
    
    async def prices_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Prices command"""
        response = self.action_handler.handle_price_inquiry("prețuri")
        await update.message.reply_text(response, parse_mode='Markdown')
    
    async def contact_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Contact information command"""
        contact_text = """
📞 **Contact XOFlowers**

🌸 **Informații contact:**
• **Telefon:** +373 22 123 456
• **Email:** hello@xoflowers.md
• **Website:** www.xoflowers.md

📍 **Locația magazinului:**
• Strada Florilor 25, Chișinău, Moldova
• Luni-Vineri: 9:00-20:00
• Sâmbătă: 10:00-18:00
• Duminică: 11:00-17:00

🚚 **Livrări:**
• Gratuit peste 500 MDL în Chișinău
• Livrare expresă disponibilă
• Acoperim toată Moldova

💐 *Suntem aici pentru dumneavoastră!*
        """
        await update.message.reply_text(contact_text, parse_mode='Markdown')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Help command"""
        help_text = """
🌸 **Ghid de utilizare XOFlowers Bot**

**🌺 Cum să interacționați cu mine:**

💐 **Pentru căutare produse:**
• "Vreau trandafiri roșii pentru Valentine"
• "Caut buchete sub 500 MDL"
• "Arată-mi florile albe disponibile"

❓ **Pentru întrebări:**
• "Ce program aveți?"
• "Cât costă livrarea?"
• "Unde sunteți localizați?"

📧 **Pentru abonamente:**
• "Vreau să mă abonez la newsletter"
• "Cum funcționează abonamentele?"

💳 **Pentru comenzi:**
• "Vreau să comand acest buchet"
• "Cum pot plăti?"

🌸 **Comenzi disponibile:**
• /start - Pornire bot
• /menu - Meniul principal
• /oferinte - Oferte speciale
• /preturi - Lista prețuri
• /contact - Informații contact
• /help - Acest ghid

💫 *Sunt aici 24/7 pentru a vă ajuta!*
        """
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors"""
        logger.error(f"Update {update} caused error {context.error}")
        
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "🌸 A apărut o problemă tehnică. Vă rugăm să încercați din nou sau contactați suportul la +373 22 123 456."
            )

def main():
    """Main function to run the bot"""
    try:
        # Create and run bot
        bot = XOFlowersTelegramBot(debug=True)
        
        print("🌸 XOFlowers Telegram Bot Starting...")
        print("🤖 Enhanced AI system with context awareness")
        print("💫 Press Ctrl+C to stop the bot")
        
        # Set bot commands
        async def setup_and_run():
            commands = [
                BotCommand("start", "Pornire bot și salut"),
                BotCommand("help", "Ghid de utilizare"),
                BotCommand("menu", "Meniul principal"),
                BotCommand("oferinte", "Oferte speciale"),
                BotCommand("preturi", "Lista prețuri"),
                BotCommand("contact", "Informații contact"),
            ]
            await bot.application.bot.set_my_commands(commands)
            
            # Run the bot
            await bot.application.run_polling(
                allowed_updates=Update.ALL_TYPES,
                drop_pending_updates=True
            )
        
        # Start the bot with command setup
        asyncio.run(setup_and_run())
        
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
