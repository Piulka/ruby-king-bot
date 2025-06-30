"""
Модуль для расчёта и проверки кулдаунов
"""
import time
from core.player import Player

def get_attack_cooldown(player: Player, now: float) -> float:
    return max(0, player.GLOBAL_COOLDOWN - (now - player.last_attack_time))

def get_skill_cooldown(player: Player, now: float) -> float:
    return max(0, player.SKILL_COOLDOWN - (now - player.last_skill_time))

def get_heal_cooldown(player: Player, now: float) -> float:
    return max(0, player.HEAL_COOLDOWN - (now - player.last_heal_time))

def get_mana_cooldown(player: Player, now: float) -> float:
    return max(0, player.MANA_COOLDOWN - (now - player.last_mana_time))

def reset_all_cooldowns(player: Player):
    now = time.time()
    player.last_attack_time = now - player.GLOBAL_COOLDOWN
    player.last_skill_time = now - player.SKILL_COOLDOWN
    player.last_heal_time = now - player.HEAL_COOLDOWN
    player.last_mana_time = now - player.MANA_COOLDOWN 