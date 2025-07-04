"""
API client for Ruby King game
"""

import time
import logging
from typing import Dict, Any, Optional
import requests

from Found_bot.config.settings import Settings
from Found_bot.config.token import GAME_TOKEN
from Found_bot.api.endpoints import Endpoints

logger = logging.getLogger(__name__)

class APIClient:
    """HTTP client for making requests to Ruby King API"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(Settings.DEFAULT_HEADERS)
        self.token = GAME_TOKEN
        self._last_request_time = 0  # Throttle: время последнего запроса
        
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                     retries: int = None, headers: Optional[dict] = None) -> Dict[str, Any]:
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
        
        # --- THROTTLE: ограничение частоты запросов ---
        now = time.time()
        elapsed = now - self._last_request_time
        if elapsed < 1:
            time.sleep(1 - elapsed)
        self._last_request_time = time.time()
        # --- конец throttle ---
        
        for attempt in range(retries + 1):
            try:
                logger.debug(f"Making {method} request to {endpoint} (attempt {attempt + 1})")
                
                if method.upper() == "POST":
                    response = self.session.post(
                        url,
                        json=data,
                        timeout=Settings.REQUEST_TIMEOUT,
                        headers=headers
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
        headers = self.get_custom_headers(self.token)
        result = self._make_request("POST", Endpoints.EXPLORE_TERRITORY, data, headers=headers)
        
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
        headers = self.get_custom_headers(self.token)
        result = self._make_request("POST", Endpoints.ATTACK_MOB, data, headers=headers)
        
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
        headers = self.get_custom_headers(self.token)
        result = self._make_request("POST", Endpoints.USE_SKILL, data, headers=headers)
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
    
    def get_custom_headers(self, token: str) -> dict:
        return {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'ru,en;q=0.9,en-US;q=0.8,de;q=0.7',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'Origin': 'https://ruby-king.ru',
            'Referer': f'https://ruby-king.ru/city?name={token}&timeEnd=1751300208114',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
        }

    def change_main_geo(self, position: str) -> dict:
        """
        Change main geographical position (city/farm) с кастомными headers
        """
        data = {"position": position}
        token = self.token
        url = f"https://ruby-king.ru/api/farm/change-main-geo?name={token}"
        headers = self.get_custom_headers(token)
        logger.info(f"[API] change_main_geo: {url} data={data}")
        resp = self.session.post(url, json=data, headers=headers)
        return resp.json()

    def change_geo(self, loco: str, direction: str, type_action: str = "change") -> dict:
        """
        Change geo (location/direction) с кастомными headers
        """
        data = {"loco": loco, "direction": direction, "typeAction": type_action}
        token = self.token
        url = f"https://ruby-king.ru/api/farm/change-geo?name={token}"
        headers = self.get_custom_headers(token)
        logger.info(f"[API] change_geo: {url} data={data}")
        resp = self.session.post(url, json=data, headers=headers)
        return resp.json()

    def reset_geo(self) -> dict:
        """
        Reset geo (typeAction=reset) с кастомными headers
        """
        data = {"loco": "", "direction": "", "typeAction": "reset"}
        token = self.token
        url = f"https://ruby-king.ru/api/farm/change-geo?name={token}"
        headers = self.get_custom_headers(token)
        logger.info(f"[API] reset_geo: {url} data={data}")
        resp = self.session.post(url, json=data, headers=headers)
        return resp.json()

    def complete_bats_event(self) -> Dict[str, Any]:
        """
        Завершить событие SPEC_BATS (летучие мыши) — отправить POST на /api/user/vesna
        """
        endpoint = f"/user/vesna?name={self.token}"
        logger.info("Completing SPEC_BATS event via /api/user/vesna ...")
        result = self._make_request("POST", endpoint, data={})
        return result

    def change_square(self, square: str) -> dict:
        """
        Change to a specific square on the map (маршрут)
        """
        data = {"square": square}
        token = self.token
        url = f"https://ruby-king.ru/api/farm/change-square?name={token}"
        headers = self.get_custom_headers(token)
        logger.info(f"[API] change_square: {url} data={data}")
        resp = self.session.post(url, json=data, headers=headers)
        return resp.json() 