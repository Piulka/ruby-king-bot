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
    
    def switch_to_next_alive_target(self) -> Optional['Mob']:
        """Switch to the next alive mob target, skipping dead ones"""
        for i, mob in enumerate(self.mobs):
            if mob.hp > 0:
                self.current_target_index = i
                return mob
        return None
    
    def has_more_alive_targets(self) -> bool:
        """Check if there are more alive mobs to fight"""
        logger.debug(f"Checking for more alive targets. Current index: {self.current_target_index}, Total mobs: {len(self.mobs)}")
        
        for i in range(self.current_target_index + 1, len(self.mobs)):
            mob = self.mobs[i]
            logger.debug(f"Mob {i}: {mob.name} HP: {mob.hp} (alive: {mob.hp > 0})")
            if mob.hp > 0:
                logger.debug(f"Found alive mob: {mob.name}")
                return True
        
        logger.debug("No more alive targets found")
        return False
    
    def is_empty(self) -> bool:
        """Check if all mobs in the group are dead"""
        for mob in self.mobs:
            if mob.hp > 0:
                return False
        return True
    
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
        # Обновляем всех мобов в группе, но mobTargetHP применяется только к текущему мобу
        current_target = self.get_current_target()
        
        for mob in self.mobs:
            if mob == current_target:
                # Для текущего моба используем полную логику обновления
                mob.update_from_combat_response(response_data)
            else:
                # Для остальных мобов используем только данные из массива mobs
                mobs_array = response_data.get('mobs', [])
                if isinstance(mobs_array, list):
                    for mob_info in mobs_array:
                        if mob_info.get('farmId') == mob.farm_id:
                            old_hp = mob.hp
                            if 'stats' in mob_info and 'userCurrentHP' in mob_info['stats']:
                                hp_data = mob_info['stats']['userCurrentHP']
                                if isinstance(hp_data, list) and len(hp_data) > 0:
                                    mob.hp = hp_data[0]
                                else:
                                    mob.hp = hp_data if isinstance(hp_data, (int, float)) else mob.hp
                            elif 'hp' in mob_info:
                                mob.hp = mob_info.get('hp', mob.hp)
                            
                            if mob.hp <= 0:
                                mob.is_alive = False
                            else:
                                mob.is_alive = True
                            
                            logger.debug(f"Other mob HP updated: {mob.name} HP {old_hp} -> {mob.hp}/{mob.max_hp}")
                            break
    
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
        self.drops = []  # Дроп моба
        
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
        
        # Пытаемся извлечь HP из различных возможных мест
        # В ответе исследования территории HP находится в stats.userCurrentHP
        
        # Проверяем, есть ли HP в stats.userCurrentHP
        stats = mob_data.get('stats', {})
        if 'userCurrentHP' in stats:
            hp_data = stats.get('userCurrentHP', [100, 0])
            # HP приходит в формате [текущее_HP, 0], берем первый элемент
            if isinstance(hp_data, list) and len(hp_data) > 0:
                self.hp = hp_data[0]
                self.max_hp = hp_data[0]  # max_hp обычно равен текущему HP при инициализации
            else:
                self.hp = hp_data if isinstance(hp_data, (int, float)) else 100
                self.max_hp = self.hp
            logger.debug(f"Mob HP from stats.userCurrentHP: {self.name} HP {self.hp}/{self.max_hp}")
        elif 'hp' in mob_data:
            # Fallback: HP в корне объекта
            self.hp = mob_data.get('hp', 100)
            self.max_hp = mob_data.get('maxHp', mob_data.get('hp', 100))
        else:
            # Устанавливаем разумные значения по умолчанию
            # Уровень моба влияет на его HP
            level = mob_data.get('lvl', mob_data.get('level', 1))
            base_hp = 50 + (level * 25)  # Базовая формула HP
            self.hp = base_hp
            self.max_hp = base_hp
            logger.debug(f"Mob HP set to default: {self.name} HP {self.hp}/{self.max_hp}")
        
        self.level = mob_data.get('lvl', mob_data.get('level', self.level))
        
        # Извлекаем дроп моба
        self.drops = mob_data.get('drop', [])
        if not self.drops:
            # Пробуем альтернативные ключи
            self.drops = mob_data.get('drops', [])
        
        # Update alive status
        self.is_alive = self.hp > 0
        
        logger.debug(f"Mob updated: {self.name} HP {self.hp}/{self.max_hp} farmId: {self.farm_id} drops: {len(self.drops)}")
    
    def update_from_combat_response(self, response_data: Dict[str, Any]):
        """
        Update mob data from combat response
        
        Args:
            response_data: Combat API response
        """
        logger.debug(f"Updating mob {self.name} from combat response")
        logger.debug(f"Response keys: {list(response_data.keys())}")
        
        # Try to get mob data from different sources in attack response
        mob_data = None
        
        # First try: mobTargetHP (direct HP info)
        mob_target_hp = response_data.get('mobTargetHP', {})
        if mob_target_hp and isinstance(mob_target_hp, dict):
            mob_id = mob_target_hp.get('id', '')
            mob_hp = mob_target_hp.get('hp', 0)
            if mob_id and mob_hp is not None:
                # Update HP directly from mobTargetHP
                old_hp = self.hp
                self.hp = mob_hp
                logger.debug(f"Mob HP updated from mobTargetHP: {self.name} HP {old_hp} -> {self.hp}/{self.max_hp}")
                # Check if mob died
                if self.hp <= 0:
                    logger.info(f"Mob {self.name} defeated!")
                    self.is_alive = False
                return
        
        # Second try: mobs array
        mobs_array = response_data.get('mobs', [])
        if isinstance(mobs_array, list) and len(mobs_array) > 0:
            logger.debug(f"Found {len(mobs_array)} mobs in response")
            # Find mob with matching farm_id
            for mob_info in mobs_array:
                if mob_info.get('farmId') == self.farm_id:
                    mob_data = mob_info
                    logger.debug(f"Found matching mob: {mob_info.get('name', 'Unknown')}")
                    break
        
        # Third try: direct mob data
        if not mob_data:
            mob_data = response_data.get('mob', {})
            if mob_data:
                logger.debug(f"Found direct mob data")
        
        if mob_data:
            # Update only HP and max_hp, don't call update_from_data
            old_hp = self.hp
            if 'hp' in mob_data:
                self.hp = mob_data.get('hp', self.hp)
            if 'maxHp' in mob_data:
                self.max_hp = mob_data.get('maxHp', self.max_hp)
            
            logger.debug(f"Mob HP updated from mob data: {self.name} HP {old_hp} -> {self.hp}/{self.max_hp}")
            
            # Check if mob died
            if self.hp <= 0:
                logger.info(f"Mob {self.name} defeated!")
                self.is_alive = False
            else:
                self.is_alive = True
        else:
            logger.debug(f"No mob data found in response for {self.name}")
    
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