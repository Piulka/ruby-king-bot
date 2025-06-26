"""
API endpoints definitions for Ruby King
"""

class Endpoints:
    # Base API URL
    BASE_URL = "https://ruby-king.ru/api"
    
    # User endpoints
    USER_INFO = "/user/info"
    USER_STATS = "/user/stats"
    
    # Game endpoints
    EXPLORE_TERRITORY = "/farm/farm-mob-one"
    ATTACK_MOB = "/battle/user-attack"
    USE_SKILL = "/battle/user-attack"  # Тот же endpoint, но с skillId
    USE_HEALING_POTION = "/user/inventory/use-potion"
    USE_MANA_POTION = "/user/inventory/use-potion"
    START_REST = "/farm/add-fire"
    END_REST = "/farm/add-fire-end"
    STOP_REST = "/rest/stop"
    
    # Shop endpoints
    SELL_ITEMS = "/trader/sell"
    BUY_ITEMS = "/trader/buy"
    
    # Location endpoints
    CHANGE_MAIN_GEO = "/farm/change-main-geo"
    CHANGE_GEO = "/farm/change-geo"
    CHANGE_SQUARE = "/farm/change-square"
    
    @classmethod
    def get_full_url(cls, endpoint: str) -> str:
        """Get full URL for endpoint"""
        return f"{cls.BASE_URL}{endpoint}"
    
    @classmethod
    def get_url_with_token(cls, endpoint: str, token: str) -> str:
        """Get full URL with token parameter"""
        return f"{cls.get_full_url(endpoint)}?name={token}" 