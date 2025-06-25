#!/usr/bin/env python3
"""
Тестовый файл для проверки логики извлечения урона
"""

import re
from typing import Dict, Any

def extract_damage_received(result: Dict[str, Any]) -> int:
    """Extract damage received from combat logs"""
    damage_received = 0
    arr_logs = result.get('arrLogs', [])
    for log_entry in arr_logs:
        # Проверяем поле damage в log_entry
        if 'damage' in log_entry:
            damage_received = log_entry.get('damage', 0)
            break
        # Также проверяем messages на случай если damage нет
        messages = log_entry.get('messages', [])
        for message in messages:
            if 'наносит' in message and 'урон' in message:
                damage_match = re.search(r'наносит (\d+) урон', message)
                if damage_match:
                    damage_received = int(damage_match.group(1))
                    break
    return damage_received

def extract_damage_dealt(result: Dict[str, Any]) -> int:
    """Extract damage dealt from combat logs"""
    damage_dealt = 0
    arr_logs = result.get('arrLogs', [])
    for log_entry in arr_logs:
        # Проверяем поле damage в log_entry
        if 'damage' in log_entry:
            damage_dealt = log_entry.get('damage', 0)
            break
        # Также проверяем messages на случай если damage нет
        messages = log_entry.get('messages', [])
        for message in messages:
            if 'наносит' in message and 'урон' in message:
                damage_match = re.search(r'наносит (\d+) урон', message)
                if damage_match:
                    damage_dealt = int(damage_match.group(1))
                    break
    return damage_dealt

# Тестовые данные
test_result = {
    "arrLogs": [
        {
            "damage": 15,
            "messages": ["Игрок наносит 15 урона мобу"]
        },
        {
            "damage": 8,
            "messages": ["Моб наносит 8 урона игроку"]
        }
    ]
}

print("Тест извлечения урона:")
print(f"Урон нанесенный: {extract_damage_dealt(test_result)}")
print(f"Урон полученный: {extract_damage_received(test_result)}") 