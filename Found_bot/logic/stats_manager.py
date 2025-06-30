"""
Модуль для централизованного учёта статистики Ruby King Bot
"""
from typing import Dict

class StatsManager:
    def __init__(self):
        self.stats = {
            'total_exp': 0,
            'session_gold': 0,
            'session_start': 0,
            'events_found': 0,
            'total_damage_dealt': 0,
            'total_attacks': 0,
            'city_visits': 0,
            'items_sold': 0,
            'gold_from_sales': 0,
            'hp_potions_used': 0,
            'mp_potions_used': 0,
            'bats_events': 0,
            'mobs_killed': 0
        }
        self.killed_mobs = {}
    def update(self, **kwargs):
        for key, value in kwargs.items():
            if key in self.stats:
                self.stats[key] += value
            elif key == 'killed_mob':
                mob_name = value
                self.killed_mobs[mob_name] = self.killed_mobs.get(mob_name, 0) + 1
    def get_stats(self) -> Dict:
        return self.stats.copy()
    def get_killed_mobs(self) -> Dict:
        return self.killed_mobs.copy() 