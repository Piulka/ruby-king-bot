"""
Player data management
"""

import logging
from typing import Dict, Any, Optional
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
        self.stats = PlayerStats()
        self.inventory = {}  # Добавлено для хранения инвентаря
        
        # Cooldown tracking
        self.last_heal_time = 0
        self.last_attack_time = 0
        self.heal_cooldown_end = 0
        self.attack_cooldown_end = 0
    
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
        from ..config.settings import Settings
        return self.get_hp_percentage() < Settings.HEAL_THRESHOLD
    
    def needs_rest(self) -> bool:
        """Check if player needs rest (stamina <= threshold)"""
        from ..config.settings import Settings
        return self.stamina <= Settings.STAMINA_THRESHOLD
    
    def can_heal(self, current_time: float) -> bool:
        """
        Check if player can use healing potion (cooldown check)
        
        Args:
            current_time: Current timestamp
            
        Returns:
            True if can heal, False otherwise
        """
        from ..config.settings import Settings
        time_since_last_heal = current_time - self.last_heal_time
        return time_since_last_heal >= Settings.HEAL_COOLDOWN
    
    def can_attack(self, current_time: float) -> bool:
        """
        Check if player can attack (cooldown check)
        
        Args:
            current_time: Current timestamp
            
        Returns:
            True if can attack, False otherwise
        """
        from ..config.settings import Settings
        time_since_last_attack = current_time - self.last_attack_time
        return time_since_last_attack >= Settings.ATTACK_COOLDOWN
    
    def record_heal(self, current_time: float):
        """Record healing potion usage"""
        from ..config.settings import Settings
        self.last_heal_time = current_time
        self.heal_cooldown_end = current_time + Settings.HEAL_COOLDOWN
        logger.debug("Healing potion used, cooldown started")
    
    def record_attack(self, current_time: float):
        """Record attack usage"""
        from ..config.settings import Settings
        self.last_attack_time = current_time
        self.attack_cooldown_end = current_time + Settings.ATTACK_COOLDOWN
        logger.debug("Attack performed, cooldown started")
    
    def get_stats_summary(self) -> Dict[str, Any]:
        """Get player stats summary"""
        return {
            'hp': f"{self.hp}/{self.max_hp} ({self.get_hp_percentage():.1f}%)",
            'mp': f"{self.mp}/{self.max_mp} ({self.get_mp_percentage():.1f}%)",
            'stamina': f"{self.stamina}/{self.max_stamina} ({self.get_stamina_percentage():.1f}%)",
            'level': self.stats.level,
            'experience': f"{self.stats.experience}/{self.stats.experience_to_next}",
            'gold': self.stats.gold,
            'mobs_killed': self.stats.mobs_killed,
            'needs_healing': self.needs_healing(),
            'needs_rest': self.needs_rest()
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