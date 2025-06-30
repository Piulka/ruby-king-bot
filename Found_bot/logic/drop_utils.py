"""
Модуль для обработки дропа мобов
"""
from typing import List, Dict, Any

def flatten_drop(drop_data) -> List[Dict[str, Any]]:
    flat_drop = []
    if isinstance(drop_data, list):
        for item in drop_data:
            if isinstance(item, list):
                flat_drop.extend([x for x in item if isinstance(x, dict)])
            elif isinstance(item, dict):
                flat_drop.append(item)
    elif isinstance(drop_data, dict):
        flat_drop.append(drop_data)
    return flat_drop

def filter_gold_drop(flat_drop: List[Dict[str, Any]]) -> int:
    return sum(item.get('count', 0) for item in flat_drop if item.get('id') == 'm_0_1') 