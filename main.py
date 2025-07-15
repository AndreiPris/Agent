#!/usr/bin/env python3
"""
XOFlowers AI Agent - Main Application Entry Point
Instagram AI Agent for XOFlowers built with ChromaDB + LLMs
"""

import os
import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from telegram import Update
except ImportError:
    Update = None

from dotenv import load_dotenv
load_dotenv()

def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(
        description="XOFlowers AI Agent - Instagram & Telegram Bot"
    )
    parser.add_argument(
        "--platform",
        choices=["instagram", "telegram", "both"],
        default="instagram",
        help="Platform to run the bot on (default: instagram)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5001,
        help="Port for Instagram webhook (default: 5001)"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )
    
    args = parser.parse_args()
    
    # Load environment variables
    if not os.path.exists(".env"):
        print("❌ Error: .env file not found!")
        print("Please create a .env file with your API keys.")
        sys.exit(1)
    
    print("🌸 XOFlowers AI Agent Starting...")
    print(f"📱 Platform: {args.platform}")
    print(f"🚀 Port: {args.port}")
    print(f"🔧 Debug: {args.debug}")
    print(f"📁 Structure: New Modular Architecture")
    print("-" * 50)
    
    try:
        if args.platform == "instagram":
            print("📸 Starting Instagram Bot...")
            from src.api.instagram_app import XOFlowersInstagramBot
            app = XOFlowersInstagramBot(debug=args.debug)
            app.run(port=args.port)
            
        elif args.platform == "telegram":
            print("📱 Starting Telegram Bot...")
            from src.api.telegram_app import XOFlowersTelegramBot
            bot = XOFlowersTelegramBot(debug=args.debug)
            
            # Run the bot using application.run_polling() directly
            bot.application.run_polling(
                allowed_updates=Update.ALL_TYPES,
                drop_pending_updates=True
            )
            
        elif args.platform == "both":
            print("🚀 Starting Both Platforms...")
            # This would require threading or multiprocessing
            print("❌ Both platforms mode not yet implemented")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        print(f"❌ Error starting bot: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
