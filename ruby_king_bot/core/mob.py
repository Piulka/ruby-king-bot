"""
Mob data management
"""

import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class MobGroup:
    """Group of mobs in a single battle"""
    
    def __init__(self, mobs_data: List[Dict[str, Any]]):
        self.mobs = [Mob(mob_data) for mob_data in mobs_data]
        self.current_target_index = 0
    
    def get_current_target(self) -> Optional['Mob']:
        """Get the current target mob"""
        if 0 <= self.current_target_index < len(self.mobs):
            return self.mobs[self.current_target_index]
        return None
    
    def switch_to_next_target(self) -> Optional['Mob']:
        """Switch to the next mob target"""
        self.current_target_index += 1
        return self.get_current_target()
    
    def has_more_targets(self) -> bool:
        """Check if there are more mobs to fight"""
        return self.current_target_index < len(self.mobs)
    
    def get_all_mobs(self) -> List['Mob']:
        """Get all mobs in the group"""
        return self.mobs
    
    def get_all_mobs_with_status(self) -> List[Dict[str, Any]]:
        """Get all mobs with display status including is_dead flag"""
        mobs_data = []
        for i, mob in enumerate(self.mobs):
            mobs_data.append({
                'name': mob.name,
                'hp': f"{mob.hp}/{mob.max_hp}",
                'level': mob.level,
                'is_current_target': i == self.current_target_index,
                'is_dead': mob.hp <= 0
            })
        return mobs_data
    
    def update_from_combat_response(self, response_data: Dict[str, Any]):
        """Update all mobs from combat response"""
        current_target = self.get_current_target()
        if current_target:
            current_target.update_from_combat_response(response_data)
    
    def get_display_data(self) -> List[Dict[str, Any]]:
        """Get display data for all mobs"""
        return [mob.get_info() for mob in self.mobs]

class Mob:
    """Mob enemy data and management"""
    
    def __init__(self, mob_data: Optional[Dict[str, Any]] = None):
        self.id = ""
        self.farm_id = ""  # farmId для атаки
        self.name = "Unknown"
        self.hp = 0
        self.max_hp = 0
        self.level = 1
        self.is_alive = True
        
        if mob_data:
            self.update_from_data(mob_data)
    
    def update_from_data(self, mob_data: Dict[str, Any]):
        """
        Update mob data from API response
        
        Args:
            mob_data: Mob data from API response
        """
        self.id = mob_data.get('id', self.id)
        self.farm_id = mob_data.get('farmId', self.farm_id)  # farmId для атаки
        self.name = mob_data.get('name', self.name)
        
        # Extract HP from stats structure
        stats = mob_data.get('stats', {})
        if stats:
            # HP is in stats.userCurrentHP[0], max HP in stats.userMaxHP[0]
            current_hp_list = stats.get('userCurrentHP', [0, 0])
            max_hp_list = stats.get('userMaxHP', [0, 0])
            
            if isinstance(current_hp_list, list) and len(current_hp_list) > 0:
                self.hp = current_hp_list[0]
            else:
                self.hp = mob_data.get('hp', self.hp)
                
            if isinstance(max_hp_list, list) and len(max_hp_list) > 0:
                self.max_hp = max_hp_list[0]
            else:
                self.max_hp = mob_data.get('maxHp', self.max_hp)
        else:
            # Fallback to direct fields
            self.hp = mob_data.get('hp', self.hp)
            self.max_hp = mob_data.get('maxHp', self.max_hp)
        
        self.level = mob_data.get('lvl', mob_data.get('level', self.level))
        
        # Update alive status
        self.is_alive = self.hp > 0
        
        logger.debug(f"Mob updated: {self.name} HP {self.hp}/{self.max_hp} farmId: {self.farm_id}")
    
    def update_from_combat_response(self, response_data: Dict[str, Any]):
        """
        Update mob data from combat response
        
        Args:
            response_data: Combat API response
        """
        # Try to get mob data from different sources in attack response
        mob_data = None
        
        # First try: mobTargetHP (direct HP info)
        mob_target_hp = response_data.get('mobTargetHP', {})
        if mob_target_hp and isinstance(mob_target_hp, dict):
            mob_id = mob_target_hp.get('id', '')
            mob_hp = mob_target_hp.get('hp', 0)
            if mob_id and mob_hp is not None:
                # Update HP directly from mobTargetHP
                self.hp = mob_hp
                logger.debug(f"Mob HP updated from mobTargetHP: {self.name} HP {self.hp}/{self.max_hp}")
                # Check if mob died
                if not self.is_alive:
                    logger.info(f"Mob {self.name} defeated!")
                return
        
        # Second try: mobs array
        mobs_array = response_data.get('mobs', [])
        if isinstance(mobs_array, list) and len(mobs_array) > 0:
            mob_data = mobs_array[0]
        else:
            # Third try: direct mob data
            mob_data = response_data.get('mob', {})
        
        if mob_data:
            self.update_from_data(mob_data)
            
            # Check if mob died
            if not self.is_alive:
                logger.info(f"Mob {self.name} defeated!")
    
    def get_hp_percentage(self) -> float:
        """Get current HP as percentage"""
        if self.max_hp > 0:
            return (self.hp / self.max_hp) * 100
        return 0
    
    def is_dead(self) -> bool:
        """Check if mob is dead"""
        return self.hp <= 0
    
    def get_health_bar(self, width: int = 20) -> str:
        """
        Get visual health bar for mob
        
        Args:
            width: Width of health bar
            
        Returns:
            String representation of health bar
        """
        if self.max_hp <= 0:
            return "█" * width
        
        filled = int((self.hp / self.max_hp) * width)
        empty = width - filled
        
        bar = "█" * filled + "░" * empty
        return f"[{bar}] {self.hp}/{self.max_hp}"
    
    def get_info(self) -> Dict[str, Any]:
        """Get mob information summary"""
        return {
            'id': self.id,
            'name': self.name,
            'hp': f"{self.hp}/{self.max_hp} ({self.get_hp_percentage():.1f}%)",
            'level': self.level,
            'is_alive': self.is_alive,
            'health_bar': self.get_health_bar()
        }
    
    def __str__(self) -> str:
        return f"Mob({self.name}, HP: {self.hp}/{self.max_hp}, Level: {self.level})"
    
    def __repr__(self) -> str:
        return self.__str__() 