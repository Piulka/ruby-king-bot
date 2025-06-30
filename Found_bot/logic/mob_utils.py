"""
Модуль вспомогательных функций для работы с мобами и группами мобов
"""
from typing import List, Dict, Optional
from core.mob import Mob, MobGroup

def get_mob_data(mob: Mob) -> Optional[dict]:
    if not mob:
        return None
    return {
        'name': mob.name,
        'hp': mob.hp,
        'max_hp': mob.max_hp,
        'level': mob.level
    }

def get_mob_group_data(mob_group: MobGroup) -> Optional[List[dict]]:
    if not mob_group:
        return None
    return mob_group.get_all_mobs_with_status()

def normalize_mob_name(name: str) -> str:
    return name.strip().lower() if name else ''

def find_current_target(mob_group: MobGroup) -> Optional[Mob]:
    if not mob_group:
        return None
    return mob_group.get_current_target()

def update_mob_hp(mob: Mob, new_hp: int):
    if mob:
        mob.hp = new_hp 