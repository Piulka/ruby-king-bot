"""
Player class for Ruby King game
"""

import logging
from typing import Dict, Any, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class PlayerStats:
    """Player statistics data"""
    level: int = 1
    experience: int = 0
    experience_to_next: int = 100
    gold: int = 0
    mobs_killed: int = 0

class Player:
    """Player character data and management"""
    
    def __init__(self):
        self.hp = 100
        self.max_hp = 100
        self.mp = 100
        self.max_mp = 100
        self.stamina = 100
        self.max_stamina = 100
        self.morale = 0  # Добавлено для хранения морали
        self.inventory_weight = 0  # Текущий вес рюкзака
        self.max_inventory_weight = 0  # Максимальный вес рюкзака
        self.stats = PlayerStats()
        self.inventory = {}  # Добавлено для хранения инвентаря
        # Новые поля для локации
        self.current_location = None
        self.current_direction = None
        self.current_square = None
        
        # Поля для позиции возврата после похода в город
        self.return_location = None
        self.return_direction = None
        self.return_square = None
        
        # Cooldowns
        self.last_attack_time = 0
        self.last_skill_time = 0
        self.last_heal_time = 0
        self.last_mana_time = 0
        
        # Cooldown durations (in seconds)
        self.GLOBAL_COOLDOWN = 5.3  # Global cooldown between combat actions
        self.SKILL_COOLDOWN = 11.0  # Skill personal cooldown
        self.HEAL_COOLDOWN = 5.5    # Healing potion cooldown
        self.MANA_COOLDOWN = 5.5    # Mana potion cooldown
    
    @property
    def level(self) -> int:
        """Get player level"""
        return self.stats.level
    
    @property
    def xp(self) -> int:
        """Get player experience"""
        return self.stats.experience
    
    @property
    def gold(self) -> int:
        """Get player gold"""
        return self.stats.gold
    
    def update_from_api_response(self, response_data: Dict[str, Any]):
        """
        Update player data from API response
        
        Args:
            response_data: API response data
        """
        # Extract HP from user.stats if available (attack response)
        user_data = response_data.get('user', {})
        if user_data:
            stats = user_data.get('stats', {})
            if stats:
                current_hp_list = stats.get('userCurrentHP', [0, 0])
                max_hp_list = stats.get('userMaxHP', [0, 0])
                current_mp_list = stats.get('userCurrentMP', [0, 0])
                max_mp_list = stats.get('userMaxMP', [0, 0])
                stamina_val = stats.get('userStamina', [self.stamina, 0])
                max_stamina_val = stats.get('userMaxStamina', [self.max_stamina, 0])
                # HP
                if isinstance(current_hp_list, list) and len(current_hp_list) > 0:
                    self.hp = current_hp_list[0]
                else:
                    self.hp = user_data.get('hp', self.hp)
                if isinstance(max_hp_list, list) and len(max_hp_list) > 0:
                    self.max_hp = max_hp_list[0]
                else:
                    self.max_hp = user_data.get('maxHp', self.max_hp)
                # MP
                if isinstance(current_mp_list, list) and len(current_mp_list) > 0:
                    self.mp = current_mp_list[0]
                else:
                    self.mp = user_data.get('mp', self.mp)
                if isinstance(max_mp_list, list) and len(max_mp_list) > 0:
                    self.max_mp = max_mp_list[0]
                else:
                    self.max_mp = user_data.get('maxMp', self.max_mp)
                # Stamina
                if isinstance(stamina_val, list) and len(stamina_val) > 0:
                    self.stamina = stamina_val[0]
                else:
                    self.stamina = user_data.get('stamina', self.stamina)
                if isinstance(max_stamina_val, list) and len(max_stamina_val) > 0:
                    self.max_stamina = max_stamina_val[0]
                else:
                    self.max_stamina = user_data.get('maxStamina', self.max_stamina)
            else:
                # Fallback to direct user data
                self.hp = user_data.get('hp', self.hp)
                self.max_hp = user_data.get('maxHp', self.max_hp)
                self.mp = user_data.get('mp', self.mp)
                self.max_mp = user_data.get('maxMp', self.max_mp)
                self.stamina = user_data.get('stamina', self.stamina)
                self.max_stamina = user_data.get('maxStamina', self.max_stamina)
            # Gold
            self.stats.gold = user_data.get('gold', self.stats.gold)
            # Level and XP
            self.stats.level = user_data.get('lvl', self.stats.level)
            self.stats.experience = user_data.get('userCurrentXP', self.stats.experience)
            self.stats.experience_to_next = user_data.get('userNextXP', self.stats.experience_to_next)
            # Morale (возможно, это стамина)
            self.morale = user_data.get('morale', getattr(self, 'morale', 0))
            # Inventory weight - inventoryWeight это максимальный вес
            self.max_inventory_weight = user_data.get('inventoryWeight', 0)
            # Текущий вес пока не найден, устанавливаем 0
            self.inventory_weight = 0  # TODO: найти поле с текущим весом
            # Inventory
            if 'inventory' in user_data:
                self.inventory = user_data['inventory']
        else:
            player_data = response_data.get('player', {})
            stats = response_data.get('stats', {})
            if stats:
                current_hp_list = stats.get('userCurrentHP', [0, 0])
                max_hp_list = stats.get('userMaxHP', [0, 0])
                current_mp_list = stats.get('userCurrentMP', [0, 0])
                max_mp_list = stats.get('userMaxMP', [0, 0])
                stamina_val = stats.get('userStamina', [self.stamina, 0])
                max_stamina_val = stats.get('userMaxStamina', [self.max_stamina, 0])
                if isinstance(current_hp_list, list) and len(current_hp_list) > 0:
                    self.hp = current_hp_list[0]
                else:
                    self.hp = player_data.get('hp', self.hp)
                if isinstance(max_hp_list, list) and len(max_hp_list) > 0:
                    self.max_hp = max_hp_list[0]
                else:
                    self.max_hp = player_data.get('maxHp', self.max_hp)
                if isinstance(current_mp_list, list) and len(current_mp_list) > 0:
                    self.mp = current_mp_list[0]
                else:
                    self.mp = player_data.get('mp', self.mp)
                if isinstance(max_mp_list, list) and len(max_mp_list) > 0:
                    self.max_mp = max_mp_list[0]
                else:
                    self.max_mp = player_data.get('maxMp', self.max_mp)
                if isinstance(stamina_val, list) and len(stamina_val) > 0:
                    self.stamina = stamina_val[0]
                else:
                    self.stamina = player_data.get('stamina', self.stamina)
                if isinstance(max_stamina_val, list) and len(max_stamina_val) > 0:
                    self.max_stamina = max_stamina_val[0]
                else:
                    self.max_stamina = player_data.get('maxStamina', self.max_stamina)
            else:
                self.hp = player_data.get('hp', self.hp)
                self.max_hp = player_data.get('maxHp', self.max_hp)
                self.mp = player_data.get('mp', self.mp)
                self.max_mp = player_data.get('maxMp', self.max_mp)
                self.stamina = player_data.get('stamina', self.stamina)
                self.max_stamina = player_data.get('maxStamina', self.max_stamina)
            self.stats.gold = player_data.get('gold', self.stats.gold)
            self.stats.level = player_data.get('lvl', self.stats.level)
            self.stats.experience = player_data.get('userCurrentXP', self.stats.experience)
            self.stats.experience_to_next = player_data.get('userNextXP', self.stats.experience_to_next)
            self.morale = player_data.get('morale', getattr(self, 'morale', 0))
            # Inventory weight - inventoryWeight это максимальный вес
            self.max_inventory_weight = player_data.get('inventoryWeight', 0)
            # Текущий вес пока не найден, устанавливаем 0
            self.inventory_weight = 0  # TODO: найти поле с текущим весом
            if 'inventory' in player_data:
                self.inventory = player_data['inventory']
        
        logger.debug(f"Player updated: HP {self.hp}/{self.max_hp}, MP {self.mp}/{self.max_mp}, Stamina {self.stamina}/{self.max_stamina}")
    
    def update_combat_result(self, response_data: Dict[str, Any]):
        """
        Update player data from combat result
        
        Args:
            response_data: Combat API response
        """
        # Update from player data in response
        self.update_from_api_response(response_data)
        
        # Check if mob was killed (victory)
        mob_data = response_data.get('mob', {})
        if mob_data and mob_data.get('hp', 1) <= 0:
            self.stats.mobs_killed += 1
            logger.info(f"Victory! Mobs killed: {self.stats.mobs_killed}")
    
    def get_hp_percentage(self) -> float:
        """Get current HP as percentage"""
        if self.max_hp > 0:
            return (self.hp / self.max_hp) * 100
        return 0
    
    def get_stamina_percentage(self) -> float:
        """Get current stamina as percentage"""
        if self.max_stamina > 0:
            return (self.stamina / self.max_stamina) * 100
        return 0
    
    def get_mp_percentage(self) -> float:
        """Get current MP as percentage"""
        if self.max_mp > 0:
            return (self.mp / self.max_mp) * 100
        return 0
    
    def needs_healing(self) -> bool:
        """Check if player needs healing (HP < threshold)"""
        from config.settings import Settings
        return self.get_hp_percentage() < Settings.HEAL_THRESHOLD
    
    def needs_rest(self) -> bool:
        """Check if player needs rest (stamina <= threshold)"""
        from config.settings import Settings
        return self.stamina <= Settings.STAMINA_THRESHOLD
    
    def can_attack(self, current_time: float) -> bool:
        """Check if player can attack (respects global cooldown only)"""
        # Атака не имеет собственного КД, только ГКД между боевыми навыками
        last_combat_time = max(self.last_attack_time, self.last_skill_time)
        return current_time - last_combat_time >= self.GLOBAL_COOLDOWN
    
    def can_use_skill(self, current_time: float) -> bool:
        """Check if player can use skill (respects both personal and global cooldowns)"""
        # Скилл имеет собственный КД + ГКД между боевыми навыками
        skill_cd_ready = current_time - self.last_skill_time >= self.SKILL_COOLDOWN
        last_combat_time = max(self.last_attack_time, self.last_skill_time)
        global_cd_ready = current_time - last_combat_time >= self.GLOBAL_COOLDOWN
        return skill_cd_ready and global_cd_ready
    
    def can_use_heal_potion(self, current_time: float) -> bool:
        """Check if player can use healing potion (only personal cooldown)"""
        # Зелья не зависят от ГКД, только от собственного КД
        return current_time - self.last_heal_time >= self.HEAL_COOLDOWN
    
    def can_use_mana_potion(self, current_time: float) -> bool:
        """Check if player can use mana potion (only personal cooldown)"""
        # Зелья не зависят от ГКД, только от собственного КД
        return current_time - self.last_mana_time >= self.MANA_COOLDOWN
    
    def record_attack(self, current_time: float):
        """Record attack time"""
        self.last_attack_time = current_time
    
    def record_skill(self, current_time: float):
        """Record skill usage time"""
        self.last_skill_time = current_time
        # Скилл также запускает ГКД для боевых навыков
        self.last_attack_time = current_time
    
    def record_heal(self, current_time: float):
        """Record healing potion usage time"""
        self.last_heal_time = current_time
    
    def record_mana(self, current_time: float):
        """Record mana potion usage time"""
        self.last_mana_time = current_time
    
    def set_location(self, location: str, direction: str = None, square: str = None):
        self.current_location = location
        self.current_direction = direction
        self.current_square = square

    def set_square(self, square: str):
        self.current_square = square

    def save_return_position(self):
        """Сохранить текущую позицию для возврата после похода в город"""
        self.return_location = self.current_location
        self.return_direction = self.current_direction
        self.return_square = self.current_square
        logger.info(f"Return position saved: {self.return_location} -> {self.return_direction} -> {self.return_square}")
    
    def has_return_position(self) -> bool:
        """Проверить есть ли сохраненная позиция возврата"""
        return all([self.return_location, self.return_direction, self.return_square])
    
    def restore_return_position(self):
        """Восстановить позицию возврата"""
        if self.has_return_position():
            self.current_location = self.return_location
            self.current_direction = self.return_direction
            self.current_square = self.return_square
            logger.info(f"Return position restored: {self.current_location} -> {self.current_direction} -> {self.current_square}")
            return True
        return False

    def get_stats_summary(self) -> Dict[str, Any]:
        """Get player stats summary"""
        return {
            'hp': self.hp,
            'max_hp': self.max_hp,
            'mana': self.mp,
            'max_mana': self.max_mp,
            'stamina': self.stamina,
            'max_stamina': self.max_stamina,
            'level': self.stats.level,
            'xp': self.stats.experience,
            'xp_next': self.stats.experience_to_next,
            'gold': self.get_gold_count(),
            'heal_potions': self.get_heal_potions_count(),
            'mana_potions': self.get_mana_potions_count(),
            'skulls': self.get_skulls_count(),
            'morale': getattr(self, 'morale', 0),
            'inventory_weight': getattr(self, 'inventory_weight', 0),
            'max_inventory_weight': getattr(self, 'max_inventory_weight', 0),
            'location': self.current_location,
            'direction': self.current_direction,
            'square': self.current_square
        }
    
    def get_heal_potions_count(self) -> int:
        """Возвращает количество хилок (m_1) в инвентаре"""
        if hasattr(self, 'inventory') and self.inventory:
            potion = self.inventory.get('m_1')
            if potion and isinstance(potion, dict):
                return potion.get('count', 0)
        return 0
    
    def get_gold_count(self) -> int:
        """Возвращает количество золота (m_0_1) в инвентаре"""
        if hasattr(self, 'inventory') and self.inventory:
            gold = self.inventory.get('m_0_1')
            if gold and isinstance(gold, dict):
                return gold.get('count', 0)
        return 0
    
    def get_skulls_count(self) -> int:
        """Возвращает количество черепов (m_0_2) в инвентаре"""
        if hasattr(self, 'inventory') and self.inventory:
            skulls = self.inventory.get('m_0_2')
            if skulls and isinstance(skulls, dict):
                return skulls.get('count', 0)
        return 0
    
    def get_mana_potions_count(self) -> int:
        """Возвращает количество банок маны (m_3) в инвентаре"""
        if hasattr(self, 'inventory') and self.inventory:
            potion = self.inventory.get('m_3')
            if potion and isinstance(potion, dict):
                return potion.get('count', 0)
        return 0
    
    def initialize(self, api_client):
        """Initialize player data from API"""
        try:
            # Получаем данные игрока из города
            player_info = api_client.get_user_city_info()
            if player_info and 'user' in player_info:
                self.update_from_api_response(player_info)
                logger.info("Player data initialized successfully")
            else:
                logger.warning("Could not get player data, using defaults")
        except Exception as e:
            logger.error(f"Failed to get player data: {e}, using defaults")
    
    def set_level(self, level: int):
        """Set player level"""
        self.stats.level = level 