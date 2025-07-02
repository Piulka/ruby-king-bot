"""
Route Manager - Manages farming routes based on world_map_data.json
"""

import json
import logging
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class RoutePoint:
    """A point in the farming route"""
    location: str
    location_name: str
    direction: str
    direction_name: str
    square: str
    mob_level: int
    mob_name: str = "unknown"

class RouteManager:
    """Manages farming routes based on world map data"""
    
    def __init__(self, player_level: int, map_path: str = None):
        self.player_level = player_level
        # Игнорируем map_path, всегда используем нужный файл
        self.map_path = "world_map_viewer/data/complete_world_map.json"
        self.route: List[RoutePoint] = []
        self.current_route_index = 0
        self.mobs_killed_on_current_square = 0
        self.mobs_per_square = 10
        
        # Build route
        self._build_route()
    
    def _build_route(self):
        """Build route from world map data (только по одному наиболее подходящему квадрату на сторону)"""
        try:
            logger.info(f"Starting to build route from {self.map_path}")
            with open(self.map_path, 'r', encoding='utf-8') as f:
                world_map_data = json.load(f)
            logger.info(f"Successfully loaded world map data")
            world_map = world_map_data.get("world_map", {})
            min_level = max(1, self.player_level - 9)
            filtered_route = []
            for location, location_data in world_map.items():
                # Исключаем 'Окрестности поселения'
                # if location == 'loco_0':
                #     continue
                location_name = location_data.get("name", location)
                directions = location_data.get("directions", {})
                for direction, direction_data in directions.items():
                    direction_name = direction_data.get("name", direction)
                    squares = direction_data.get("squares", {})
                    # Собираем кандидатов в диапазоне [min_level, player_level] и mob_lvl <= 20
                    candidates = []
                    lower_candidates = []
                    for square, square_data in squares.items():
                        mob_level = square_data.get("mob_level")
                        # Пропускать внутренние локации
                        if isinstance(mob_level, dict) and (mob_level.get("locoId") or mob_level.get("locoName")):
                            continue
                        # Новый формат: mob_level может быть dict с mobLvl
                        if mob_level is None:
                            continue
                        if isinstance(mob_level, dict):
                            mob_lvl = mob_level.get("mobLvl")
                        else:
                            mob_lvl = mob_level
                        if mob_lvl is None:
                            continue
                        # --- Новый парсинг диапазона ---
                        if isinstance(mob_lvl, str) and '-' in mob_lvl:
                            try:
                                mob_lvl = int(mob_lvl.split('-')[0])
                            except Exception:
                                continue
                        try:
                            mob_lvl = int(mob_lvl)
                        except (ValueError, TypeError):
                            continue
                        if mob_lvl > 20:
                            continue  # Исключаем квадраты с мобами выше 20 уровня
                        if min_level <= mob_lvl <= self.player_level:
                            candidates.append((square, mob_lvl))
                        elif mob_lvl < min_level:
                            lower_candidates.append((square, mob_lvl))
                    best_square = None
                    best_mob_lvl = None
                    if candidates:
                        # Берём минимальный mob_level из диапазона
                        best_square, best_mob_lvl = min(candidates, key=lambda x: x[1])
                    elif lower_candidates:
                        # Если нет кандидатов — берём максимальный из нижних
                        best_square, best_mob_lvl = max(lower_candidates, key=lambda x: x[1])
                    # Если ничего не найдено — best_square останется None
                    if best_square:
                        route_point = RoutePoint(
                            location=location,
                            location_name=location_name,
                            direction=direction,
                            direction_name=direction_name,
                            square=best_square,
                            mob_level=best_mob_lvl if best_mob_lvl is not None else 0
                        )
                        filtered_route.append(route_point)
            self.route = filtered_route
            self.current_route_index = 0  # Сброс на начало маршрута при старте
            logger.info(f"Route built successfully with {len(self.route)} squares")
        except Exception as e:
            logger.error(f"Failed to build route: {e}")
            self.route = []
    
    def get_current_point(self):
        if not self.route:
            logger.warning("[ROUTE] get_current_point: маршрут пуст!")
            return None
        if not (0 <= self.current_route_index < len(self.route)):
            logger.warning(f"[ROUTE] get_current_point: индекс вне диапазона! current_route_index={self.current_route_index}, route_len={len(self.route)}")
            return None
        point = self.route[self.current_route_index]
        logger.debug(f"[ROUTE] get_current_point: возвращаю точку {point}")
        return point
    
    def get_next_point(self) -> Optional[RoutePoint]:
        """Get next route point"""
        if not self.route:
            return None
        next_index = (self.current_route_index + 1) % len(self.route)
        return self.route[next_index]
    
    def move_to_next_square(self, display=None):
        """Move to next square in route and optionally print message"""
        if not self.route:
            return
        prev_index = self.current_route_index
        self.current_route_index = (self.current_route_index + 1) % len(self.route)
        self.mobs_killed_on_current_square = 0
        logger.info(f"Moved to square {self.current_route_index + 1}/{len(self.route)}")
        if display:
            point = self.route[self.current_route_index]
            display.print_message(f"Переход на локацию: {point.location_name}/{point.direction_name}/{point.square}", "info")
    
    def increment_mob_kills(self):
        """Increment mob kill counter for current square"""
        self.mobs_killed_on_current_square += 1
    
    def should_move_to_next_square(self) -> bool:
        """Check if should move to next square"""
        return self.mobs_killed_on_current_square >= self.mobs_per_square
    
    def get_route_display_data(self) -> Dict[str, Any]:
        """Get route data for display with scrolling"""
        if not self.route:
            return {
                "points": [],
                "current_index": 0,
                "total_points": 0,
                "mobs_left": 0
            }
        
        total_points = len(self.route)
        current_index = self.current_route_index
        mobs_left = max(0, self.mobs_per_square - self.mobs_killed_on_current_square)
        
        # Формируем список всех точек для отображения
        display_points = []
        for i, point in enumerate(self.route):
            display_points.append({
                "location": point.location_name,
                "direction": point.direction_name,
                "square": point.square,
                "mob_level": point.mob_level,
                "is_current": (i == current_index)
            })
        
        return {
            "points": display_points,
            "current_index": current_index,
            "total_points": total_points,
            "mobs_left": mobs_left
        }

    def save_current_index(self):
        """Save current route index to file"""
        try:
            with open("route_index.save", "w") as f:
                f.write(str(self.current_route_index))
        except Exception as e:
            logger.error(f"Failed to save route index: {e}")

    def restore_index(self):
        """Restore route index from file if exists"""
        try:
            with open("route_index.save", "r") as f:
                idx = int(f.read().strip())
                if 0 <= idx < len(self.route):
                    self.current_route_index = idx
        except Exception:
            pass  # Если файла нет или ошибка, ничего не делаем 

def parse_mob_level(mob_level):
    """Преобразует mob_level (int или диапазон) в минимальный int"""
    if isinstance(mob_level, int):
        return mob_level
    if isinstance(mob_level, str):
        # Например, '26-32' -> 26
        match = re.match(r"(\d+)", mob_level)
        if match:
            return int(match.group(1))
    return 0

def build_farm_route(player_level: int, world_map_data: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Строит маршрут фарма по всем локациям и сторонам света.
    Для каждой стороны выбирает наиболее подходящий квадрат (уровень моба ≈ player_level-9, либо ближайший выше).
    Возвращает список точек маршрута: {'location': ..., 'side': ..., 'square': ...}
    """
    route = []
    side_ru = {'north': 'Север', 'south': 'Юг', 'east': 'Восток', 'west': 'Запад'}
    for loco_id, loco_obj in world_map_data.get('world_map', {}).items():
        location_name = loco_obj.get('name', loco_id)
        for side_key, side_obj in loco_obj.get('directions', {}).items():
            side_name = side_ru.get(side_key, side_key)
            squares = side_obj.get('squares', {})
            best_square = None
            best_diff = float('inf')
            best_higher = None
            best_higher_diff = float('inf')
            for sq_name, sq_obj in squares.items():
                mob_lvl = parse_mob_level(sq_obj.get('mob_level', 0))
                if isinstance(mob_lvl, dict) and (mob_lvl.get("locoId") or mob_lvl.get("locoName")):
                    continue
                diff = abs(mob_lvl - (player_level - 9))
                if mob_lvl <= player_level - 9 and diff < best_diff:
                    best_square = sq_name
                    best_diff = diff
                elif mob_lvl > player_level - 9 and (mob_lvl - (player_level - 9)) < best_higher_diff:
                    best_higher = sq_name
                    best_higher_diff = mob_lvl - (player_level - 9)
            chosen_square = best_square or best_higher
            if chosen_square:
                route.append({
                    'location': location_name,
                    'side': side_name,
                    'square': chosen_square
                })
    return route 