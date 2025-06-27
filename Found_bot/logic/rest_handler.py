"""
Rest Handler - Manages rest actions at campfire
"""

import time
import logging
from typing import Optional, Dict, Any
from api.client import APIClient
from ui.display import GameDisplay

logger = logging.getLogger(__name__)

class RestHandler:
    """Handles rest actions and campfire management"""
    
    def __init__(self, api_client: APIClient, display: GameDisplay):
        self.api_client = api_client
        self.display = display
    
    def start_rest(self) -> Optional[Dict[str, Any]]:
        """
        Start resting at campfire
        
        Returns:
            API response data or None if rest failed
        """
        try:
            rest_result = self.api_client.rest_at_fire()
            self._log_api_response(rest_result, "rest_at_fire")
            
            self.display.print_message("🔥 Отдыхаем у костра...", "info")
            
            return rest_result
            
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