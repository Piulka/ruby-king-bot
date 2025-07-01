"""
Settings configuration for Ruby King Bot
"""

class Settings:
    # API Configuration
    API_BASE_URL = "https://ruby-king.ru/api"
    GAME_URL = "https://ruby-king.ru/city"
    TOKEN_PARAM = "name"
    
    # Request Configuration
    REQUEST_TIMEOUT = 30
    MAX_RETRIES = 3
    RETRY_DELAY = 2  # Base delay for exponential backoff
    
    # Game Mechanics
    ATTACK_COOLDOWN = 5.1  # seconds between attacks
    SKILL_COOLDOWN = 11.0  # seconds between skills
    HEAL_COOLDOWN = 5.5  # seconds between healing potions
    MANA_COOLDOWN = 5.5  # seconds between mana potions
    REST_DURATION = 1200  # 20 minutes in seconds
    HEAL_THRESHOLD = 85  # HP percentage threshold for healing
    MANA_THRESHOLD = 50  # Mana percentage threshold for mana potion
    STAMINA_THRESHOLD = 0  # Stamina threshold for resting
    SKILL_HP_THRESHOLD = 100  # HP threshold for using skill (use skill only if mob HP > 100)
    
    # Combat Configuration (CRITICAL)
    COMBAT_TIMEOUT = 300  # Maximum combat duration (5 minutes)
    FORCE_END_COMBAT = True  # Force end combat if stuck
    COMBAT_RETRY_LIMIT = 10  # Maximum retries in combat
    
    # UI Configuration
    UI_REFRESH_RATE = 1  # seconds between UI updates
    PROGRESS_BAR_WIDTH = 50
    
    # Logging Configuration
    LOG_LEVEL = "DEBUG"  # Temporarily set to DEBUG for troubleshooting
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE = "logs/bot.log"
    
    # HTTP Headers
    DEFAULT_HEADERS = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'ru,en;q=0.9,en-US;q=0.8,de;q=0.7',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
        'Origin': 'https://ruby-king.ru',
        'Referer': 'https://ruby-king.ru/city',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"'
    } 