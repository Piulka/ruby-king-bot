import json
import os
import time
from copy import deepcopy
from Found_bot.api.client import APIClient
from Found_bot.config.token import GAME_TOKEN

WORLD_MAP_PATH = "world_map_viewer/data/complete_world_map.json"
SIDE_KEYS = ["north", "south", "east", "west"]
SIDE_RU = {"north": "Север", "south": "Юг", "east": "Восток", "west": "Запад"}


def load_world_map():
    if not os.path.exists(WORLD_MAP_PATH):
        return {"world_map": {}}
    with open(WORLD_MAP_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_world_map(data):
    with open(WORLD_MAP_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_all_locations():
    # Берём все loco_id из текущей карты (можно расширить при необходимости)
    wm = load_world_map().get("world_map", {})
    return list(wm.keys())

def collect_all_squares():
    api = APIClient()
    world_map = load_world_map().get("world_map", {})
    updated_map = deepcopy(world_map)
    changed = []
    for loco_id in get_all_locations():
        for side in SIDE_KEYS:
            # Переходим в нужную локацию и сторону
            try:
                geo_result = api.change_geo(loco_id, side)
                time.sleep(1.5)  # Даем серверу обработать переход
            except Exception as e:
                print(f"[ERROR] Не удалось перейти в {loco_id}/{side}: {e}")
                continue
            # Получаем список квадратов
            try:
                user_info = api.get_user_info()
                squares = user_info.get("squares", [])
            except Exception as e:
                print(f"[ERROR] Не удалось получить squares для {loco_id}/{side}: {e}")
                continue
            # Обновляем карту
            loco_obj = updated_map.setdefault(loco_id, {})
            loco_obj.setdefault("name", loco_id)
            directions = loco_obj.setdefault("directions", {})
            dir_obj = directions.setdefault(side, {"name": side, "squares": {}})
            squares_dict = dir_obj.setdefault("squares", {})
            for sq in squares:
                sq_name = sq.get("position")
                if not sq_name:
                    continue
                old = squares_dict.get(sq_name, {})
                new = {
                    "mob_level": sq.get("lvlMobs"),
                    "has_mobs": sq.get("hasMobs", False),
                    "mob_count": sq.get("mobCount"),
                    "loco_id": sq.get("locoId"),
                    "loco_name": sq.get("locoName"),
                    "raw_data": sq
                }
                if old != new:
                    changed.append((loco_id, side, sq_name))
                squares_dict[sq_name] = new
    # Обновляем метаданные
    meta = {
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "total_locations": len(updated_map),
        "total_directions": len(SIDE_KEYS),
        "stats": {
            "locations_visited": len(updated_map),
            "directions_visited": len(updated_map) * len(SIDE_KEYS),
            "squares_visited": sum(len(dir_obj.get("squares", {})) for loco in updated_map.values() for dir_obj in loco.get("directions", {}).values()),
            "mobs_found": 0,
            "errors": 0
        }
    }
    result = {"metadata": meta, "world_map": updated_map}
    return result, changed

def diff_maps(old_map, new_map):
    """Возвращает список изменённых квадратов (location, direction, square)"""
    old_wm = old_map.get("world_map", {})
    new_wm = new_map.get("world_map", {})
    changed = []
    for loco_id, loco_obj in new_wm.items():
        for side, dir_obj in loco_obj.get("directions", {}).items():
            old_dir = old_wm.get(loco_id, {}).get("directions", {}).get(side, {})
            for sq, sq_data in dir_obj.get("squares", {}).items():
                old_sq = old_dir.get("squares", {}).get(sq)
                if old_sq != sq_data:
                    changed.append((loco_id, side, sq))
    return changed

if __name__ == "__main__":
    print("Сбор всех квадратов по всем локациям и сторонам света...")
    old_map = load_world_map()
    new_map, changed = collect_all_squares()
    diff = diff_maps(old_map, new_map)
    if diff:
        print(f"Изменены квадраты: {diff}")
    else:
        print("Изменений не было")
    save_world_map(new_map)
    print("Карта мира обновлена!") 