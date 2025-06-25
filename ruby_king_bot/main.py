"""
Main entry point for Ruby King Bot
Refactored to use modular architecture
"""

import logging
import os
import sys
from rich.console import Console

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ruby_king_bot.logic.game_engine import GameEngine

console = Console()

def setup_logging():
    """Setup logging configuration"""
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/bot.log'),
            # Убираем StreamHandler чтобы логи не появлялись в консоли
            # logging.StreamHandler()
        ]
    )

def main():
    """Main entry point"""
    # Setup logging first
    setup_logging()
    
    # Create and run game engine
    engine = GameEngine()
    engine.initialize()
    engine.run()

if __name__ == "__main__":
    main() 