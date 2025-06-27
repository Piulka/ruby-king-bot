"""
Route Manager - Manages farming routes based on world_map_data.json
"""

import json
import logging
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

@dataclass
class MobInfo:
    """Information about a mob"""
    name: str
    level: int
    hp: int
    max_hp: int
    farm_id: str
    exp_reward: int = 0
    gold_reward: int = 0
    drop_items: List[Dict[str, Any]] = None

class MobDatabase:
    """Database for storing mob information and drops"""
    
    def __init__(self, db_file: str = "mob_database.json"):
        self.db_file = db_file
        self.data = self._load_database()
    
    def _load_database(self) -> Dict[str, Any]:
        """Load database from file"""
        try:
            with open(self.db_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "locations": {},
                "mobs": {},
                "statistics": {
                    "total_mobs_found": 0,
                    "total_locations_visited": 0,
                    "total_directions_visited": 0,
                    "total_squares_visited": 0
                }
            }
    
    def _save_database(self):
        """Save database to file"""
        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def add_mob_info(self, location: str, direction: str, square: str, 
                    mob_info: MobInfo, drop_data: Dict[str, Any] = None):
        """Add mob information to database"""
        # Create location structure if it doesn't exist
        if location not in self.data["locations"]:
            self.data["locations"][location] = {}
        
        if direction not in self.data["locations"][location]:
            self.data["locations"][location][direction] = {}
        
        if square not in self.data["locations"][location][direction]:
            self.data["locations"][location][direction][square] = {
                "mobs": [],
                "visits": 0
            }
        
        # Add mob information
        mob_data = {
            "name": mob_info.name,
            "level": mob_info.level,
            "hp": mob_info.hp,
            "max_hp": mob_info.max_hp,
            "farm_id": mob_info.farm_id,
            "exp_reward": mob_info.exp_reward,
            "gold_reward": mob_info.gold_reward,
            "drop_items": drop_data or [],
            "first_seen": datetime.now().isoformat(),
            "last_seen": datetime.now().isoformat()
        }
        
        # Check if mob already exists
        existing_mob = None
        for mob in self.data["locations"][location][direction][square]["mobs"]:
            if mob["name"] == mob_info.name and mob["level"] == mob_info.level:
                existing_mob = mob
                break
        
        if existing_mob:
            # Update existing mob
            existing_mob.update(mob_data)
            existing_mob["last_seen"] = datetime.now().isoformat()
        else:
            # Add new mob
            self.data["locations"][location][direction][square]["mobs"].append(mob_data)
            self.data["statistics"]["total_mobs_found"] += 1
        
        # Increment visit counter
        self.data["locations"][location][direction][square]["visits"] += 1
        
        self._save_database()

class RouteManager:
    """Manages farming routes based on world map data"""
    
    def __init__(self, player_level: int, map_path: str = "world_map_data.json"):
        self.player_level = player_level
        self.map_path = map_path
        self.route: List[RoutePoint] = []
        self.current_route_index = 0
        self.mobs_killed_on_current_square = 0
        self.mobs_per_square = 10
        self.mob_database = MobDatabase()
        
        # Build route
        self._build_route()
    
    def _build_route(self):
        """Build route from world map data"""
        try:
            logger.info(f"Starting to build route from {self.map_path}")
            with open(self.map_path, 'r', encoding='utf-8') as f:
                world_map_data = json.load(f)
            logger.info(f"Successfully loaded world map data")
            world_map = world_map_data.get("world_map", {})
            min_level = max(1, self.player_level - 9)
            max_level = min(self.player_level, 20)  # Ограничиваем верхнюю границу 20 уровнем
            logger.info(f"Building route for player level {self.player_level} (mobs {min_level}-{max_level})")
            logger.info(f"Found {len(world_map)} locations")
            filtered_route = []
            
            for location, location_data in world_map.items():
                location_name = location_data.get("name", location)
                directions = location_data.get("directions", {})
                
                for direction, direction_data in directions.items():
                    direction_name = direction_data.get("name", direction)
                    squares = direction_data.get("squares", {})
                    
                    for square, square_data in squares.items():
                        # Получаем уровень моба из квадрата
                        mob_level = square_data.get("mob_level")
                        
                        if mob_level is None:
                            continue
                        
                        # Обрабатываем уровень моба
                        mob_levels = []
                        if isinstance(mob_level, int):
                            mob_levels.append(mob_level)
                        elif isinstance(mob_level, str) and '-' in mob_level:
                            # Обрабатываем диапазон уровней (например, "18-21")
                            try:
                                l1, l2 = map(int, mob_level.split('-'))
                                mob_levels.extend(range(l1, l2 + 1))
                            except (ValueError, IndexError):
                                logger.warning(f"Invalid level format: {mob_level}")
                                continue
                        elif isinstance(mob_level, str):
                            # Обрабатываем одиночный уровень в строке
                            try:
                                mob_levels.append(int(mob_level))
                            except ValueError:
                                logger.warning(f"Invalid level format: {mob_level}")
                                continue
                        
                        if not mob_levels:
                            continue
                        
                        # Проверяем, что ВСЕ мобы в квадрате подходят по уровню
                        # Квадрат подходит только если ВСЕ мобы в диапазоне [min_level, max_level]
                        all_mobs_suitable = all(min_level <= lvl <= max_level for lvl in mob_levels)
                        
                        if all_mobs_suitable:
                            # Создаем RoutePoint для квадрата
                            route_point = RoutePoint(
                                location=location,
                                location_name=location_name,
                                direction=direction,
                                direction_name=direction_name,
                                square=square,
                                mob_level=min(mob_levels)  # Используем минимальный уровень для отображения
                            )
                            filtered_route.append(route_point)
            
            self.route = filtered_route
            logger.info(f"Route built successfully with {len(self.route)} squares")
            
        except Exception as e:
            logger.error(f"Failed to build route: {e}")
            self.route = []
    
    def get_current_point(self) -> Optional[RoutePoint]:
        """Get current route point"""
        if not self.route:
            return None
        return self.route[self.current_route_index]
    
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