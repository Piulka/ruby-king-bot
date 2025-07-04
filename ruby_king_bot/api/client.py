"""
API client for Ruby King game
"""

import time
import logging
from typing import Dict, Any, Optional
import requests

from ruby_king_bot.config.settings import Settings
from ruby_king_bot.config.token import GAME_TOKEN
from ruby_king_bot.api.endpoints import Endpoints

logger = logging.getLogger(__name__)

class APIClient:
    """HTTP client for making requests to Ruby King API"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(Settings.DEFAULT_HEADERS)
        self.token = GAME_TOKEN
        
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                     retries: int = None) -> Dict[str, Any]:
        """
        Make HTTP request with retry logic
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            data: Request data for POST requests
            retries: Number of retries (defaults to Settings.MAX_RETRIES)
            
        Returns:
            Response data as dictionary
            
        Raises:
            requests.RequestException: If all retries fail
        """
        if retries is None:
            retries = Settings.MAX_RETRIES
            
        url = Endpoints.get_url_with_token(endpoint, self.token)
        
        for attempt in range(retries + 1):
            try:
                logger.debug(f"Making {method} request to {endpoint} (attempt {attempt + 1})")
                
                if method.upper() == "POST":
                    response = self.session.post(
                        url, 
                        json=data, 
                        timeout=Settings.REQUEST_TIMEOUT
                    )
                else:
                    response = self.session.get(
                        url, 
                        timeout=Settings.REQUEST_TIMEOUT
                    )
                
                response.raise_for_status()
                result = response.json()
                
                # DEBUG: Log the response structure
                logger.debug(f"API Response type: {type(result)}")
                logger.debug(f"API Response: {result}")
                
                # Handle different response formats
                if isinstance(result, list):
                    # If response is a list, convert to dict with first item
                    if len(result) > 0:
                        result = result[0]
                    else:
                        result = {}
                elif not isinstance(result, dict):
                    # If response is not dict or list, create empty dict
                    logger.warning(f"Unexpected response type: {type(result)}")
                    result = {}
                
                logger.debug(f"Request successful: {endpoint}")
                return result
                
            except requests.RequestException as e:
                logger.warning(f"Request failed (attempt {attempt + 1}): {e}")
                
                if attempt == retries:
                    logger.error(f"All retries failed for {endpoint}")
                    raise
                
                # Exponential backoff
                delay = Settings.RETRY_DELAY * (2 ** attempt)
                logger.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)
    
    def explore_territory(self, loco: str = "loco_0", direction: str = "north") -> Dict[str, Any]:
        """
        Explore territory to find mobs or events
        
        CRITICAL: This automatically puts the player in combat if a mob is found
        
        Args:
            loco: Location parameter
            direction: Direction to explore
            
        Returns:
            Response data containing mob information if found
        """
        data = {
            "loco": loco,
            "direction": direction
        }
        
        logger.info("Exploring territory...")
        result = self._make_request("POST", Endpoints.EXPLORE_TERRITORY, data)
        
        # CRITICAL: Log if mob was found (player is now in combat)
        if "mob" in result:
            mob_data = result['mob']
            if isinstance(mob_data, list) and len(mob_data) > 0:
                mob_name = mob_data[0].get('name', 'Unknown')
            elif isinstance(mob_data, dict):
                mob_name = mob_data.get('name', 'Unknown')
            else:
                mob_name = 'Unknown'
            logger.info(f"Found mob: {mob_name}")
        else:
            logger.info("No mob found, exploring event or empty area")
            
        return result
    
    def attack_mob(self, mob_id: str) -> Dict[str, Any]:
        """
        Attack a mob
        
        Args:
            mob_id: ID of the mob to attack
            
        Returns:
            Response data with combat results
        """
        data = {"mobId": mob_id}
        
        logger.info(f"Attacking mob: {mob_id}")
        result = self._make_request("POST", Endpoints.ATTACK_MOB, data)
        
        return result
    
    def use_healing_potion(self) -> Dict[str, Any]:
        """
        Use healing potion to restore HP
        
        Args:
            None
            
        Returns:
            Response data with healing results
        """
        data = {"elemId": "m_1"}
        
        logger.info("Using healing potion...")
        result = self._make_request("POST", Endpoints.USE_HEALING_POTION, data)
        
        return result
    
    def start_rest(self) -> Dict[str, Any]:
        """
        Start resting at campfire
        
        Args:
            None
            
        Returns:
            Response data with rest start information
        """
        data = {}
        
        logger.info("Starting rest at campfire...")
        result = self._make_request("POST", Endpoints.START_REST, data)
        
        return result
    
    def end_rest(self) -> Dict[str, Any]:
        """
        End resting at campfire
        
        Args:
            None
            
        Returns:
            Response data with rest end information
        """
        data = {}
        
        logger.info("Ending rest at campfire...")
        result = self._make_request("POST", Endpoints.END_REST, data)
        
        return result

    def use_mana_potion(self) -> Dict[str, Any]:
        """
        Use mana potion to restore MP
        """
        data = {"elemId": "m_3"}
        logger.info("Using mana potion...")
        result = self._make_request("POST", Endpoints.USE_MANA_POTION, data)
        return result

    def use_skill(self, mob_id: str, skill_id: str = "skill_0_1") -> Dict[str, Any]:
        """
        Use skill on mob
        """
        data = {"mobId": mob_id, "skillId": skill_id}
        logger.info(f"Using skill {skill_id} on mob: {mob_id}")
        result = self._make_request("POST", Endpoints.USE_SKILL, data)
        return result

    def get_user_info(self) -> Dict[str, Any]:
        """
        Get user information
        
        Returns:
            Response data with user information
        """
        logger.info("Getting user info...")
        result = self._make_request("GET", Endpoints.USER_INFO)
        return result
    
    def get_user_city_info(self) -> Dict[str, Any]:
        """
        Get user information from city (for initialization)
        
        Returns:
            Response data with user information from city
        """
        logger.info("Getting user city info...")
        result = self._make_request("GET", Endpoints.USER_CITY)
        return result
    
    def sell_items(self, items: list[dict]) -> dict:
        """
        Sell items (оружие, броня, бижутерия)
        Args:
            items: List of dicts {"id": uniqueId, "count": 1}
        Returns:
            Response data
        """
        data = {"items": items}
        logger.info(f"Selling items: {items}")
        result = self._make_request("POST", Endpoints.SELL_ITEMS, data)
        logger.info(f"Sell items response: {result}")
        return result

    def buy_items(self, elem_id: str, name_collection: str, count: int) -> dict:
        """
        Buy items (зелья и др.)
        Args:
            elem_id: id предмета (например, m_1)
            name_collection: коллекция (обычно 'resources')
            count: сколько купить
        Returns:
            Response data
        """
        data = {"elemId": elem_id, "nameCollection": name_collection, "count": count}
        logger.info(f"Buying {count} of {elem_id} from {name_collection}")
        result = self._make_request("POST", Endpoints.BUY_ITEMS, data)
        logger.info(f"Buy items response: {result}")
        return result
    
    def change_main_geo(self, position: str) -> Dict[str, Any]:
        """
        Change main geographical position (city/farm)
        
        Args:
            position: Position to change to ("city" or "farm")
            
        Returns:
            Response data with position change results
        """
        data = {"position": position}
        logger.info(f"Changing main geo to: {position}")
        result = self._make_request("POST", Endpoints.CHANGE_MAIN_GEO, data)
        return result
    
    def change_geo(self, loco: str, direction: str, type_action: str = "change") -> Dict[str, Any]:
        """
        Change geographical location within farm
        
        Args:
            loco: Location name (e.g., "loco_3")
            direction: Direction (e.g., "south", "north")
            type_action: Action type (default: "change")
            
        Returns:
            Response data with location change results
        """
        data = {
            "loco": loco,
            "direction": direction,
            "typeAction": type_action
        }
        logger.info(f"Changing geo to {loco} {direction}")
        result = self._make_request("POST", Endpoints.CHANGE_GEO, data)
        return result
    
    def change_square(self, square: str) -> Dict[str, Any]:
        """
        Change square within current location
        
        Args:
            square: Square position (e.g., "G4", "G3")
            
        Returns:
            Response data with square change results
        """
        data = {"square": square}
        logger.info(f"Changing square to: {square}")
        result = self._make_request("POST", Endpoints.CHANGE_SQUARE, data)
        return result 