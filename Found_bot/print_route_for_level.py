import sys
import os

# Добавляем Found_bot в PYTHONPATH
sys.path.append(os.path.join(os.path.dirname(__file__), 'Found_bot'))

from logic.route_manager import RouteManager

if __name__ == "__main__":
    level = 22
    route_manager = RouteManager(player_level=level)
    print(f"Маршрут для уровня {level} (всего {len(route_manager.route)} точек):\n")
    for i, point in enumerate(route_manager.route, 1):
        print(f"{i:2d}. {point.location_name} / {point.direction_name} / {point.square} — уровень моба: {point.mob_level}") 