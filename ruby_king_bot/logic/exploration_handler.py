"""
Exploration Handler - Manages territory exploration
"""

import time
import logging
from typing import Optional, Dict, Any
from ruby_king_bot.api.client import APIClient
from ruby_king_bot.ui.display import GameDisplay
from ruby_king_bot.core.player import Player

logger = logging.getLogger(__name__)

class ExplorationHandler:
    """Handles territory exploration and related actions"""
    
    def __init__(self, api_client: APIClient, display: GameDisplay, player: Player = None):
        self.api_client = api_client
        self.display = display
        self.player = player
    
    def explore_territory(self) -> Optional[Dict[str, Any]]:
        """
        Explore territory to find mobs
        
        Returns:
            API response data or None if exploration failed
        """
        try:
            # Выбираем локацию в зависимости от уровня персонажа
            if self.player and self.player.level < 10:
                # Для персонажей ниже 10 уровня используем loco_0
                self.display.print_message(f"🔍 Исследуем loco_0 (уровень {self.player.level} < 10)...", "info")
                explore_result = self.api_client.explore_territory("loco_0", "south")
            else:
                # Для персонажей 10+ уровня используем loco_3
                if self.player:
                    self.display.print_message(f"🔍 Исследуем loco_3 (уровень {self.player.level} >= 10)...", "info")
                else:
                    self.display.print_message("🔍 Исследуем loco_3 (уровень не определен)...", "info")
                explore_result = self.api_client.explore_territory("loco_3", "south")
            
            self._log_api_response(explore_result, "explore_territory")
            
            return explore_result
            
        except Exception as e:
            self.display.print_message(f"Network error: {e}. Waiting 60 seconds before retry...", "error")
            time.sleep(60)
            return None
    
    def _log_api_response(self, response: Dict[str, Any], context: str = ""):
        """Log API response to file"""
        import json
        with open("logs/api_responses.log", "a", encoding="utf-8") as f:
            f.write(f"\n--- {context} ---\n")
            f.write(json.dumps(response, ensure_ascii=False, indent=2))
            f.write("\n") 