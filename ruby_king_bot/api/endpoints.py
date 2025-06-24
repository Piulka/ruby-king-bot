"""
API endpoints definitions for Ruby King
"""

class Endpoints:
    # Base API URL
    BASE_URL = "https://ruby-king.ru/api"
    
    # Game endpoints
    EXPLORE_TERRITORY = "/farm/farm-mob-one"
    ATTACK_MOB = "/battle/user-attack"
    USE_HEALING_POTION = "/user/inventory/use-potion"
    START_REST = "/farm/add-fire"
    END_REST = "/farm/add-fire-end"
    
    @classmethod
    def get_full_url(cls, endpoint: str) -> str:
        """Get full URL for endpoint"""
        return f"{cls.BASE_URL}{endpoint}"
    
    @classmethod
    def get_url_with_token(cls, endpoint: str, token: str) -> str:
        """Get full URL with token parameter"""
        return f"{cls.get_full_url(endpoint)}?name={token}" 