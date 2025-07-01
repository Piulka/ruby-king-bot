"""
Game Engine - Main game loop and state management
"""

import time
import logging
from typing import Dict, Any, Optional, List
from rich.console import Console
from rich.table import Table

from ruby_king_bot.api.client import APIClient
from ruby_king_bot.core.game_state import GameState, GameStateManager
from ruby_king_bot.core.player import Player
from ruby_king_bot.core.mob import MobGroup
from ruby_king_bot.ui.display import GameDisplay
from ruby_king_bot.config.settings import Settings
from ruby_king_bot.logic.combat_handler import CombatHandler
from ruby_king_bot.logic.exploration_handler import ExplorationHandler
from ruby_king_bot.logic.rest_handler import RestHandler
from ruby_king_bot.logic.data_extractor import DataExtractor
from ruby_king_bot.logic.low_damage_handler import LowDamageHandler
from ruby_king_bot.config.constants import DIRECTIONS, LOCATION_NAMES, MOBS_PER_DIRECTION, DIRECTION_NAMES
from ruby_king_bot.logic.mob_mapper import MobMapper
from ruby_king_bot.logic.world_map_router import WorldMapRouter, RoutePoint
from ruby_king_bot.ui.display import GameDisplay

logger = logging.getLogger(__name__)
console = Console()

# Конфигурация локаций для фарма кусков лука по уровням
BOW_FARMING_LOCATIONS = {
    # D ранг (21-40) - Лук "Кровавый ворон"
    "D": {
        "location": "loco_4",  # Развалины
        "target_mob": "Древний Каргон",
        "mob_level_range": (15, 20),
        "min_player_level": 18,
        "max_player_level": 40
    },
    # C ранг (41-60) - Лук "Пламенный сумрак" 
    "C": {
        "location": "loco_5",  # Пустыня
        "target_mob": "Ядовитая стрелозубка",
        "mob_level_range": (35, 45),
        "min_player_level": 38,
        "max_player_level": 60
    },
    # B ранг (61-80) - Лук "Лунный стрелок"
    "B": {
        "location": "loco_1",  # Таинственный лес
        "target_mob": "Корневой Гнев", 
        "mob_level_range": (55, 65),
        "min_player_level": 58,
        "max_player_level": 80
    }
}

class GameEngine:
    """Main game engine that manages the game loop and state transitions"""
    
    def __init__(self):
        """Initialize the game engine"""
        self.api_client = APIClient()
        self.player = Player()
        self.display = GameDisplay()
        self.state_manager = GameStateManager()
        self.combat_handler = CombatHandler(self.api_client, self.player, self.display)
        self.exploration_handler = ExplorationHandler(self.api_client, self.display)
        self.rest_handler = RestHandler(self.api_client, self.display)
        self.data_extractor = DataExtractor()
        self.mob_mapper = MobMapper()  # Система картографирования мобов
        
        # Game state variables
        self.current_mob_group = None
        self.explore_done = False
        self.rest_end_time = None
        self.last_display_update = 0  # Track last display update time
        
        # Statistics
        self.session_stats = {
            'mobs_killed': 0,
            'total_exp': 0,
            'session_gold': 0,
            'session_start': time.time(),
            'squares_visited': 0,  # Количество посещенных квадратов
            'directions_visited': 0,  # Количество посещенных направлений
            'locations_visited': 0   # Количество посещенных локаций
        }
        
        # Direction rotation tracking
        self.current_direction_index = 0  # Индекс текущего направления
        self.mobs_killed_in_current_direction = 0  # Количество убитых мобов в текущем направлении
        self.target_mob_found = False  # Найден ли целевой моб
        self.current_farming_config = None  # Текущая конфигурация фарма
        
        # Новый роутер для работы с картой мира
        self.world_router = WorldMapRouter()
        self.current_route: List[RoutePoint] = []
        self.current_route_index = 0
        self.mobs_killed_on_current_square = 0
        self.target_mobs_per_square = 10
        
        # UI
        self.display = GameDisplay()
        
        # Статистика сессии
        self.session_stats = {
            'total_exp': 0,
            'session_gold': 0,
            'session_start': time.time(),
            'events_found': 0,
            'total_damage_dealt': 0,
            'total_attacks': 0,
            'city_visits': 0,
            'items_sold': 0,
            'gold_from_sales': 0,
            'hp_potions_used': 0,
            'mp_potions_used': 0,
            'squares_visited': 0,
            'directions_visited': 0,
            'locations_visited': 0
        }
    
    def initialize(self):
        """Initialize the game engine"""
        console.print("[bold blue]Starting Ruby King Bot...[/bold blue]")
        console.print("[green]Bot initialized successfully[/green]")
        console.print("[yellow]Continuous mode: Bot will explore territory after each victory[/yellow]")
        
        # Initialize player data if needed
        self._initialize_player_data()
        
        # Setup farming environment
        if not self._setup_farming_environment():
            console.print("[red]Failed to setup farming environment, bot may not work correctly[/red]")
            logger.error("Failed to setup farming environment")
        else:
            console.print("[green]Farming environment ready, starting main loop[/green]")
            logger.info("Farming environment ready")
    
    def run(self):
        """Main game loop"""
        console.print("[bold blue]Starting Ruby King Bot...[/bold blue]")
        
        try:
            # Initialize player data
            console.print("[blue]Initializing player data...[/blue]")
            self.player.initialize(self.api_client)
            console.print("[green]Player data initialized successfully[/green]")
            
            # Setup route-based farming
            console.print("[blue]Setting up route-based farming...[/blue]")
            if not self.setup_route_based_farming():
                console.print("[red]Failed to setup route-based farming![/red]")
                return
            
            console.print("[bold green]Route-based farming ready, starting main loop[/bold green]")
            
            # Main game loop with live display
            with self.display.get_live_display() as live:
                while True:
                    try:
                        current_time = time.time()
                        current_state = self.state_manager.get_current_state()
                        
                        # Update display with current route info
                        if self.current_route and self.current_route_index < len(self.current_route):
                            current_point = self.current_route[self.current_route_index]
                            route_progress = f"Маршрут: {self.current_route_index + 1}/{len(self.current_route)} - {current_point.location_name} | {current_point.direction_name} | {current_point.square}"
                            
                            # Update display with current game state
                            player_data = self.player.get_stats_summary()
                            self.display.update_display(
                                current_state=current_state.value,
                                player_data=player_data,
                                mob_data=None,
                                mob_group_data=None,
                                attack_cooldown=0,
                                heal_cooldown=0,
                                skill_cooldown=0,
                                mana_cooldown=0,
                                rest_time=None,
                                player_name="Piulok",
                                last_attack_time=self.player.last_attack_time,
                                last_skill_time=self.player.last_skill_time,
                                location=self.player.current_location,
                                direction=self.player.current_direction,
                                square=self.player.current_square,
                                current_route=self.current_route,
                                current_route_index=self.current_route_index,
                                mobs_killed_on_current_square=self.mobs_killed_on_current_square
                            )
                        
                        # Handle different states
                        if current_state == GameState.CITY:
                            self._handle_city_state()
                        elif current_state == GameState.EXPLORING:
                            self._handle_exploring_state()
                        elif current_state == GameState.COMBAT:
                            self._handle_combat_state()
                        elif current_state == GameState.RESTING:
                            self._handle_resting_state()
                        elif current_state == GameState.HEALING:
                            self._handle_healing_state()
                        
                        # Small delay to prevent excessive API calls
                        time.sleep(1)
                        
                    except KeyboardInterrupt:
                        console.print("\n[yellow]Bot stopped by user[/yellow]")
                        break
                    except Exception as e:
                        logger.error(f"Error in main loop: {e}")
                        console.print(f"[red]Error in main loop: {e}[/red]")
                        time.sleep(5)  # Wait before retrying
                        
        except Exception as e:
            logger.error(f"Fatal error in game engine: {e}")
            console.print(f"[red]Fatal error: {e}[/red]")
    
    def _update_display(self, **kwargs):
        """Update display with current information"""
        try:
            # Обновляем статистику сессии
            self.display.update_stats(
                total_exp=self.session_stats['total_exp'],
                session_gold=self.session_stats['session_gold'],
                events_found=self.session_stats['events_found'],
                total_damage_dealt=self.session_stats['total_damage_dealt'],
                total_attacks=self.session_stats['total_attacks'],
                city_visits=self.session_stats['city_visits'],
                items_sold=self.session_stats['items_sold'],
                gold_from_sales=self.session_stats['gold_from_sales'],
                hp_potions_used=self.session_stats['hp_potions_used'],
                mp_potions_used=self.session_stats['mp_potions_used'],
                squares_visited=self.session_stats['squares_visited'],
                directions_visited=self.session_stats['directions_visited'],
                locations_visited=self.session_stats['locations_visited']
            )
            
            # Обновляем информацию о маршруте
            if 'route_progress' in kwargs:
                self.display.update_route_progress(kwargs['route_progress'])
            
            # Обновляем информацию о бое
            if 'combat_status' in kwargs:
                self.display.update_combat_status(
                    kwargs['combat_status'],
                    self.player.current_location,
                    self.player.current_direction,
                    self.player.current_square
                )
            
            # Обновляем информацию о полученном опыте и золоте
            if 'exp_gained' in kwargs:
                self.display.update_exp_gained(kwargs['exp_gained'])
            if 'gold_gained' in kwargs:
                self.display.update_gold_gained(kwargs['gold_gained'])
            if 'mobs_killed' in kwargs:
                self.display.update_mobs_killed(kwargs['mobs_killed'])
                
        except Exception as e:
            logger.error(f"Error updating display: {e}")
    
    def _handle_city_state(self):
        """Handle city state - exploration and rest management"""
        if not self.explore_done:
            # Try to explore territory
            result = self.exploration_handler.explore_territory()
            
            if result is None:  # Exploration failed
                return
            
            if result.get('status') == 'fail':
                self._handle_exploration_failure(result)
                return
            
            # Extract mob data from response
            mob_data = self.data_extractor.extract_mob_data(result)
            mob_group_data = self.data_extractor.extract_mob_group_data(result)
            
            if mob_data and mob_group_data:
                # Create MobGroup from raw data
                self.current_mob_group = MobGroup(mob_data)
                current_target = self.current_mob_group.get_current_target()
                
                # Update display data from created group
                if current_target:
                    mob_data = {
                        'name': current_target.name,
                        'hp': current_target.hp,
                        'max_hp': current_target.max_hp,
                        'level': current_target.level
                    }
                    mob_group_data = self.current_mob_group.get_all_mobs_with_status()
                
                # Message about found mobs
                mob_names = [mob['name'] for mob in mob_group_data]
                self.display.print_message(f"🔍 Найдены враги: {', '.join(mob_names)}", "info")
                
                # Check and use skill immediately after exploration if conditions are met
                current_time = time.time()
                if current_target and self._should_use_skill_after_exploration(current_target, current_time):
                    self.display.print_message("⚡ Проверяем возможность использования усиленного удара...", "info")
                    skill_result = self.combat_handler._use_skill(current_target, current_time, self.current_mob_group)
                    if skill_result == 'victory':
                        self._handle_combat_victory(skill_result)
                        return
                    elif skill_result == 'failure':
                        self._handle_combat_failure()
                        return
                    # If skill was used successfully, continue to combat state
                
                self.state_manager.change_state(GameState.COMBAT, "Mobs found")
                self.explore_done = True  # Set flag only for mobs found
            else:
                # No mobs found - this means an event was found
                self.display.print_message("🎯 Найдено событие или пустая область", "info")
                # Update events counter
                self.display.update_stats(events_found=1)
                # Don't set explore_done = True for events - continue exploring
    
    def _should_use_skill_after_exploration(self, current_target, current_time: float) -> bool:
        """Check if skill should be used immediately after exploration"""
        return (current_target and 
                current_target.hp > Settings.SKILL_HP_THRESHOLD and 
                self.player.can_use_skill(current_time))
    
    def _handle_exploration_failure(self, result: Dict[str, Any]):
        """Handle exploration failure"""
        message = result.get('message', '')
        
        if 'иссяк боевой дух' in message:
            self.display.print_message("😴 Morale depleted, starting rest...", "warning")
            rest_result = self.rest_handler.start_rest()
            if rest_result:
                self.state_manager.change_state(GameState.RESTING, "Starting rest due to low morale")
                self.rest_end_time = time.time() + (20 * 60)  # 20 minutes
        elif 'Очень быстро совершаете действия' in message:
            self.display.print_message("⏱️ Actions too fast, waiting 5 seconds...", "warning")
            time.sleep(5)
            # Reset exploration flag to try again
            self.explore_done = False
        elif 'Неверное местонахождения' in message:
            self.display.print_message("📍 Location error, waiting 10 seconds...", "warning")
            time.sleep(10)
        else:
            self.display.print_message(f"Exploration failed: {message}", "error")
    
    def _handle_combat_state(self):
        """Handle combat state"""
        try:
            current_time = time.time()
            
            # Check if we need to heal
            if self.player.should_use_healing_potion(current_time):
                self._use_healing_potion()
                return
            
            # Check if we need to use mana potion
            if self.player.should_use_mana_potion(current_time):
                self._use_mana_potion()
                return
            
            # Get current target
            if not self.current_mob_group:
                logger.error("No mob group in combat state")
                self.state_manager.change_state(GameState.CITY, "No mob group")
                return
            
            current_target = self.current_mob_group.get_current_target()
            if not current_target:
                logger.error("No current target in combat")
                self.state_manager.change_state(GameState.CITY, "No current target")
                return

            # Check if we can attack
            if not self.player.can_attack(current_time):
                return  # Wait for cooldown
            
            # Use skill if available and appropriate
            if self._should_use_skill_after_exploration(current_target, current_time):
                skill_result = self.combat_handler._use_skill(current_target, current_time, self.current_mob_group)
                if skill_result == 'victory':
                    self._handle_combat_victory(skill_result)
                    return
                elif skill_result == 'failure':
                    self._handle_combat_failure()
                    return
                # else continue with normal attack
            
            # Perform normal attack
            combat_result = self.combat_handler.handle_combat_round(current_target, current_time, self.current_mob_group)
            if combat_result == 'victory':
                self._handle_combat_victory(combat_result)
                return
            elif combat_result == 'failure':
                self._handle_combat_failure()
                return
            # else continue combat
            
        except Exception as e:
            logger.error(f"Error in combat state: {e}")
            self.state_manager.change_state(GameState.CITY, f"Combat error: {e}")
    
    def _handle_combat_victory(self, combat_result: Dict[str, Any]):
        """Обработка победы в бою"""
        try:
            # Извлекаем данные о победе из текущего состояния
            mobs_killed = 1  # По умолчанию 1 моб за бой
            exp_gained = 0
            gold_gained = 0
            
            # Получаем данные из текущего моба
            if self.current_mob_group:
                current_target = self.current_mob_group.get_current_target()
                if current_target:
                    exp_gained = current_target.exp_reward or 0
                    gold_gained = current_target.gold_reward or 0
                    
                    # Записываем в MobMapper
                    self.mob_mapper.record_mob_kill(
                        current_target.name,
                        current_target.level,
                        current_target.hp,
                        current_target.max_hp
                    )
            
            # Обновляем статистику
            self.session_stats['total_exp'] += exp_gained
            self.session_stats['session_gold'] += gold_gained
            
            # Увеличиваем счетчик убитых мобов на текущем квадрате
            self.mobs_killed_on_current_square += mobs_killed
            
            # Показываем сообщение о победе
            if current_target:
                self.display.print_victory(current_target.name, exp_gained, [])
            
            # Проверяем, нужно ли переходить к следующему квадрату
            if self.mobs_killed_on_current_square >= self.target_mobs_per_square:
                console.print(f"[green]✅ Квадрат завершен! Убито {self.mobs_killed_on_current_square} мобов[/green]")
                self._move_to_next_route_point()
            else:
                # Показываем прогресс на текущем квадрате
                if self.current_route and self.current_route_index < len(self.current_route):
                    current_point = self.current_route[self.current_route_index]
                    console.print(f"[blue]📊 Прогресс: {self.mobs_killed_on_current_square}/{self.target_mobs_per_square} мобов на квадрате {current_point.square}[/blue]")
            
            # Переходим в состояние города для следующего исследования
            self.state_manager.change_state(GameState.CITY, "Combat victory")
            self.current_mob_group = None
            self.explore_done = False
                
        except Exception as e:
            logger.error(f"Ошибка обработки победы в бою: {e}")
            console.print(f"[red]Ошибка обработки победы: {e}[/red]")
    
    def _handle_combat_failure(self):
        """Handle combat failure"""
        self.state_manager.change_state(GameState.CITY, "Combat ended - failure")
        self.current_mob_group = None
        self.explore_done = False  # Reset exploration flag
        self.display.print_message("🔄 Начинаем новое исследование...", "info")
    
    def _handle_resting_state(self):
        """Handle resting state"""
        current_time = time.time()
        if self.rest_end_time and current_time >= self.rest_end_time:
            self.display.print_rest_complete()
            self.state_manager.change_state(GameState.CITY, "Rest completed")
            self.rest_end_time = None
            self.explore_done = False  # Reset exploration flag
        elif not self.rest_end_time:
            # No rest time set, go back to city
            self.display.print_message("No rest time set, returning to city", "warning")
            self.state_manager.change_state(GameState.CITY, "No rest time set")
            self.explore_done = False  # Reset exploration flag
    
    def _handle_exploring_state(self):
        """Handle exploring state"""
        try:
            # Explore territory to find mobs
            result = self.exploration_handler.explore_territory()
            
            if result.get("status") == "success":
                # Check if mobs were found
                if "mob" in result:
                    # Mobs found, transition to combat
                    self.current_mob_group = self.exploration_handler.create_mob_group(result)
                    self.state_manager.change_state(GameState.COMBAT, "Mobs found")
                    self.explore_done = True
                else:
                    # No mobs found, continue exploring
                    self.display.print_message("🔍 Исследуем территорию...", "info")
            else:
                # Exploration failed
                self._handle_exploration_failure(result)
                
        except Exception as e:
            logger.error(f"Error in exploring state: {e}")
            self.state_manager.change_state(GameState.CITY, f"Exploration error: {e}")
    
    def _handle_healing_state(self):
        """Handle healing state"""
        # This state is handled by the healing logic in other methods
        pass
    
    def _initialize_player_data(self):
        """Initialize player data from API"""
        try:
            console.print("[blue]Initializing player data...[/blue]")
            logger.info("Initializing player data...")
            
            # Получаем данные игрока из города
            player_info = self.api_client.get_user_city_info()
            if player_info and 'user' in player_info:
                self.player.update_from_api_response(player_info)
                console.print("[green]Player data initialized successfully[/green]")
                logger.info("Player data initialized successfully")
            else:
                console.print("[yellow]Could not get player data, using defaults[/yellow]")
                logger.warning("Could not get player data, using defaults")
            
        except Exception as e:
            console.print(f"[yellow]Failed to get player data: {e}, using defaults[/yellow]")
            logger.error(f"Failed to get player data: {e}, using defaults")
    
    def _setup_farming_environment(self):
        """Setup farming environment - check location and prepare for farming"""
        try:
            console.print("[blue]Setting up farming environment...[/blue]")
            logger.info("Setting up farming environment...")
            
            # 1. Получаем актуальную информацию о игроке
            user_info = self.api_client.get_user_info()
            if not user_info or user_info.get('status') != 'success':
                console.print("[red]Failed to get user info[/red]")
                logger.error("Failed to get user info")
                return False
            
            # Обновляем данные игрока
            if 'user' in user_info:
                self.player.update_from_api_response(user_info)
            
            # Обновляем дисплей с актуальными данными
            self._update_display()
            
            # 2. Проверяем текущую позицию
            geo = user_info.get('geo', 'city')
            console.print(f"[yellow]Current location: {geo}[/yellow]")
            logger.info(f"Current location: {geo}")
            
            if geo == 'city':
                # Если мы пришли из фарм-зоны, сохраняем позицию возврата
                if self.player.current_location and self.player.current_direction and self.player.current_square:
                    self.player.save_return_position()
                # Игрок в городе - нужно купить зелья и перейти в фарм-зону
                console.print("[blue]Player is in city, preparing for farming...[/blue]")
                logger.info("Player is in city, preparing for farming...")
                
                # Покупаем зелья
                if not self._buy_potions_if_needed():
                    console.print("[red]Failed to buy potions[/red]")
                    return False
                
                # Если есть сохранённая позиция возврата, возвращаемся на неё
                if self.player.has_return_position():
                    console.print("[blue]Returning to previous farm position after city...[/blue]")
                    logger.info("Returning to previous farm position after city...")
                    # Сначала сменить локацию, если нужно
                    if self.player.current_location != self.player.return_location:
                        self._go_to_location()
                    # Затем сменить направление
                    if self.player.current_direction != self.player.return_direction:
                        self._move_to_direction(self.player.return_direction)
                    # Затем сменить квадрат
                    if self.player.current_square != self.player.return_square:
                        self._move_to_square(self.player.return_square)
                    # После возврата сбрасываем return_position
                    self.player.return_location = None
                    self.player.return_direction = None
                    self.player.return_square = None
                else:
                    # Начинаем с первой локации на юг
                    console.print("[blue]Starting from first location (south)...[/blue]")
                    logger.info("Starting from first location (south)...")
                
                # Переходим в фарм-зону
                if not self._go_to_farm_zone():
                    console.print("[red]Failed to go to farm zone[/red]")
                    return False
                    
                    # Переходим на первую локацию
                    if not self._go_to_location():
                        console.print("[red]Failed to go to first location[/red]")
                        return False
                    
                    # Переходим на юг
                    if not self._move_to_direction("south"):
                        console.print("[red]Failed to move to south direction[/red]")
                        return False
                    
                    # Переходим на первый подходящий квадрат в последовательности
                    first_square = self.mob_mapper.get_next_suitable_square_in_sequence()
                    if first_square:
                        if not self._move_to_square(first_square):
                            console.print(f"[red]Failed to move to first suitable square: {first_square}[/red]")
                            return False
                    else:
                        console.print("[red]No suitable squares found[/red]")
                        return False
                
                # Получаем обновленную информацию после перехода
                user_info = self.api_client.get_user_info()
                if user_info and 'user' in user_info:
                    self.player.update_from_api_response(user_info)
            
            # 3. Теперь игрок должен быть в фарм-зоне - ищем подходящий квадрат
            if geo == 'farm' or user_info.get('geo') == 'farm':
                console.print("[blue]Player is in farm zone, finding suitable square...[/blue]")
                logger.info("Player is in farm zone, finding suitable square...")
                
                # Сначала переходим на локацию, чтобы загрузить информацию о мобах
                if not self._go_to_location():
                    console.print("[red]Failed to go to location[/red]")
                    return False
                
                if not self._find_and_move_to_suitable_square():
                    console.print("[red]Failed to find suitable square[/red]")
                    return False
            
            console.print("[green]Farming environment setup completed[/green]")
            logger.info("Farming environment setup completed")
            
            # Принудительно устанавливаем позицию в MobMapper
            if self.player.current_location and self.player.current_direction and self.player.current_square:
                self.mob_mapper.set_current_position(
                    self.player.current_location,
                    self.player.current_direction,
                    self.player.current_square
                )
                console.print(f"[blue]MobMapper position set: {self.player.current_location} -> {self.player.current_direction} -> {self.player.current_square}[/blue]")
            
            # Устанавливаем уровень игрока в MobMapper
            self.mob_mapper.set_player_level(self.player.level)
            console.print(f"[blue]MobMapper player level set: {self.player.level}[/blue]")
            
            return True
            
        except Exception as e:
            console.print(f"[red]Error setting up farming environment: {e}[/red]")
            logger.error(f"Error setting up farming environment: {e}")
            return False
    
    def _buy_potions_if_needed(self):
        """Buy potions if needed to reach 300 each"""
        try:
            console.print("[blue]Checking and buying potions...[/blue]")
            logger.info("Checking and buying potions...")
            
            heal_potions = self.player.get_heal_potions_count()
            mana_potions = self.player.get_mana_potions_count()
            
            console.print(f"[yellow]Current potions: HP {heal_potions}, MP {mana_potions}[/yellow]")
            logger.info(f"Current potions: HP {heal_potions}, MP {mana_potions}")
            
            potions_bought = 0
            
            # Покупаем зелья лечения если меньше 300
            if heal_potions < 300:
                to_buy = 300 - heal_potions
                console.print(f"[blue]Buying {to_buy} healing potions...[/blue]")
                logger.info(f"Buying {to_buy} healing potions...")
                
                heal_result = self.api_client.buy_items('m_1', 'resources', to_buy)
                if heal_result and heal_result.get('status') == 'success':
                    potions_bought += to_buy
                    console.print(f"[green]Bought {to_buy} healing potions[/green]")
                    logger.info(f"Bought {to_buy} healing potions")
                else:
                    console.print(f"[red]Failed to buy healing potions: {heal_result}[/red]")
                    logger.error(f"Failed to buy healing potions: {heal_result}")
                
                time.sleep(2)  # Пауза 2 секунды
            
            # Покупаем зелья маны если меньше 300
            if mana_potions < 300:
                to_buy = 300 - mana_potions
                console.print(f"[blue]Buying {to_buy} mana potions...[/blue]")
                logger.info(f"Buying {to_buy} mana potions...")
                
                mana_result = self.api_client.buy_items('m_3', 'resources', to_buy)
                if mana_result and mana_result.get('status') == 'success':
                    potions_bought += to_buy
                    console.print(f"[green]Bought {to_buy} mana potions[/green]")
                    logger.info(f"Bought {to_buy} mana potions")
                else:
                    console.print(f"[red]Failed to buy mana potions: {mana_result}[/red]")
                    logger.error(f"Failed to buy mana potions: {mana_result}")
                
                time.sleep(2)  # Пауза 2 секунды
            
            if potions_bought > 0:
                console.print(f"[green]Total potions bought: {potions_bought}[/green]")
                logger.info(f"Total potions bought: {potions_bought}")
            else:
                console.print("[green]Potions are sufficient[/green]")
                logger.info("Potions are sufficient")
            
            return True
                
        except Exception as e:
            console.print(f"[red]Error checking/buying potions: {e}[/red]")
            logger.error(f"Error checking/buying potions: {e}")
            return False
    
    def _go_to_farm_zone(self):
        """Go to farm zone"""
        try:
            console.print("[blue]Going to farm zone...[/blue]")
            logger.info("Going to farm zone...")
            
            result = self.api_client.change_main_geo("farm")
            
            if result.get("status") == "success":
                console.print("[green]Successfully moved to farm zone[/green]")
                logger.info("Successfully moved to farm zone")
                time.sleep(2)  # Пауза 2 секунды
                return True
            else:
                console.print(f"[red]Failed to move to farm zone: {result.get('message', 'Unknown error')}[/red]")
                logger.error(f"Failed to move to farm zone: {result}")
                return False
            
        except Exception as e:
            console.print(f"[red]Error moving to farm zone: {e}[/red]")
            logger.error(f"Error moving to farm zone: {e}")
            return False
    
    def _go_to_location(self, location: str = "loco_0"):
        """Go to first location for knowledge base creation"""
        try:
            console.print("[blue]Going to first location for knowledge base...[/blue]")
            logger.info("Going to first location for knowledge base...")
            
            # Переходим на первую локацию (loco_0)
            direction = "south"  # Начинаем с юга
            self.player.set_location(location, direction)
            console.print(f"[blue]Going to first location: {location} {direction}[/blue]")
            logger.info(f"Going to first location: {location} {direction}")
            
            result = self.api_client.change_geo(location, direction)
            
            if result.get("status") == "success":
                console.print(f"[green]Successfully moved to first location[/green]")
                logger.info("Successfully moved to first location")
                # Увеличиваем статистику локаций
                self.session_stats['locations_visited'] += 1
                time.sleep(2)  # Задержка 2 секунды после перехода в локацию
                return True
            else:
                console.print(f"[red]Failed to move to first location: {result.get('message', 'Unknown error')}[/red]")
                logger.error(f"Failed to move to first location: {result}")
                return False
            
        except Exception as e:
            console.print(f"[red]Error moving to first location: {e}[/red]")
            logger.error(f"Error moving to first location: {e}")
            return False
    
    def _get_bow_farming_location(self) -> Optional[Dict[str, Any]]:
        """Get the best bow farming location based on player level"""
        player_level = self.player.level
        
        # Ищем подходящую локацию по уровню игрока
        for rank, config in BOW_FARMING_LOCATIONS.items():
            if config["min_player_level"] <= player_level <= config["max_player_level"]:
                console.print(f"[green]Selected {rank} rank farming location for level {player_level}[/green]")
                logger.info(f"Selected {rank} rank farming location for level {player_level}")
                return config
        
        console.print(f"[yellow]No specific bow farming location for level {player_level}, using default[/yellow]")
        logger.info(f"No specific bow farming location for level {player_level}, using default")
        return None

    def _find_and_move_to_suitable_square(self):
        """Find and move to suitable square for bow farming"""
        try:
            console.print("[blue]Finding suitable square for bow farming...[/blue]")
            logger.info("Finding suitable square for bow farming...")
            
            # Получаем информацию о квадратах
            user_info = self.api_client.get_user_info()
            squares = user_info.get("squares", [])
            
            if not squares:
                console.print("[red]No square information available[/red]")
                logger.error("No square information available")
                return False
            
            # Определяем подходящую локацию для фарма кусков лука
            farming_config = self._get_bow_farming_location()
            
            if farming_config:
                # Ищем квадрат с мобами нужного уровня для фарма кусков лука
                return self._find_bow_farming_square(squares, farming_config)
            else:
                # Используем стандартную логику поиска квадрата
                return self._find_standard_square(squares)
                
        except Exception as e:
            console.print(f"[red]Error finding suitable square: {e}[/red]")
            logger.error(f"Error finding suitable square: {e}")
            return False

    def _find_bow_farming_square(self, squares: list, farming_config: Dict[str, Any]) -> bool:
        """Find square with mobs suitable for bow farming"""
        player_level = self.player.level
        target_mob = farming_config["target_mob"]
        mob_min_level, mob_max_level = farming_config["mob_level_range"]
        
        console.print(f"[blue]Looking for square with mobs level {mob_min_level}-{mob_max_level}[/blue]")
        console.print(f"[blue]Target mob: {target_mob}[/blue]")
        logger.info(f"Looking for square with mobs level {mob_min_level}-{mob_max_level}, target: {target_mob}")
        
        best_square = None
        best_score = float('inf')
        
        for square in squares:
            position = square.get("position")
            lvl_mobs = square.get("lvlMobs")
            
            # Пропускаем квадраты с названием локации (locoName)
            if lvl_mobs and "locoName" in lvl_mobs:
                logger.info(f"Skipping square {position}: has locoName '{lvl_mobs['locoName']}'")
                continue
            
            if lvl_mobs and "mobLvl" in lvl_mobs:
                try:
                    mob_level_str = str(lvl_mobs["mobLvl"]).strip()
                    
                    # Обрабатываем диапазоны типа "26-27" или "20-23"
                    if '-' in mob_level_str:
                        # Берем среднее значение из диапазона
                        level_parts = mob_level_str.split('-')
                        if len(level_parts) == 2:
                            min_level = int(level_parts[0].strip())
                            max_level = int(level_parts[1].strip())
                            mob_level = (min_level + max_level) // 2
                        else:
                            continue
                    else:
                        # Обычное число
                        mob_level = int(mob_level_str)
                    
                    # Проверяем, что уровень мобов в нужном диапазоне
                    if mob_min_level <= mob_level <= mob_max_level:
                        # Вычисляем "идеальность" квадрата
                        # Предпочитаем мобов ближе к середине диапазона
                        target_level = (mob_min_level + mob_max_level) // 2
                        level_diff = abs(mob_level - target_level)
                        
                        # Бонус за безопасность (мобы не слишком высокого уровня)
                        safety_bonus = 0
                        if mob_level <= player_level - 5:
                            safety_bonus = 10
                        
                        score = level_diff - safety_bonus
                        
                        if score < best_score:
                            best_score = score
                            best_square = position
                            logger.info(f"New best square {position}: mobs level {mob_level} (score {score})")
                        
                except (ValueError, TypeError) as e:
                    logger.warning(f"Cannot process mob level in square {position}: {e}")
                    continue
        
        if best_square:
            logger.info(f"Selected best square {best_square} with score {best_score}")
            console.print(f"[yellow]Found suitable square: {best_square} for bow farming[/yellow]")
            logger.info(f"Found suitable square: {best_square} for bow farming")
            
            # Переходим на лучший квадрат
            result = self.api_client.change_square(best_square)
            
            if result.get("status") == "success":
                console.print(f"[green]Successfully moved to square {best_square}[/green]")
                logger.info(f"Successfully moved to square {best_square}")
                self.player.set_square(best_square)
                # Увеличиваем статистику
                self.session_stats['squares_visited'] += 1
                return True
            else:
                console.print(f"[red]Failed to move to square {best_square}: {result.get('message', 'Unknown error')}[/red]")
                logger.error(f"Failed to move to square {best_square}: {result}")
                return False
        else:
            console.print("[yellow]No suitable square found in current direction, searching other directions...[/yellow]")
            logger.info("No suitable square found in current direction, searching other directions...")
            
            # Пробуем найти в других направлениях
            if self._search_target_mob_in_other_directions(farming_config):
                return True
            
            console.print("[red]No suitable square found in any direction[/red]")
            logger.warning("No suitable square found in any direction")
            return False

    def _find_standard_square(self, squares: list) -> bool:
        """Find square using standard logic (original method)"""
        # Ищем подходящий квадрат (мобы максимально близкие к player_level - 9, но не меньше)
        player_level = self.player.level
        target_level = player_level - 9  # Целевой уровень мобов
        min_acceptable_level = target_level  # Минимальный приемлемый уровень
        best_square = None
        best_score = float('inf')  # Минимальная разница с целевым уровнем
        
        logger.info(f"Looking for square with mobs level close to {target_level} (player {player_level})")
        
        for square in squares:
            position = square.get("position")
            lvl_mobs = square.get("lvlMobs")
            
            # Пропускаем квадраты с названием локации (locoName)
            if lvl_mobs and "locoName" in lvl_mobs:
                logger.info(f"Skipping square {position}: has locoName '{lvl_mobs['locoName']}'")
                continue
            
            if lvl_mobs and "mobLvl" in lvl_mobs:
                try:
                    mob_level_str = str(lvl_mobs["mobLvl"]).strip()
                    
                    # Обрабатываем диапазоны типа "26-27" или "20-23"
                    if '-' in mob_level_str:
                        # Берем среднее значение из диапазона
                        level_parts = mob_level_str.split('-')
                        if len(level_parts) == 2:
                            min_level = int(level_parts[0].strip())
                            max_level = int(level_parts[1].strip())
                            mob_level = (min_level + max_level) // 2
                        else:
                            continue
                    else:
                        # Обычное число
                        mob_level = int(mob_level_str)
                    
                    # Проверяем, что уровень мобов не меньше минимального приемлемого
                    if mob_level >= min_acceptable_level:
                        # Вычисляем разницу с целевым уровнем
                        level_diff = abs(mob_level - target_level)
                        
                        # Ищем квадрат с минимальной разницей (максимально близкий к целевому)
                        if level_diff < best_score:
                            best_score = level_diff
                            best_square = position
                            logger.info(f"New best square {position}: mobs level {mob_level} (diff {level_diff} from target {target_level})")
                        
                except (ValueError, TypeError) as e:
                    # Если не удается преобразовать mob_level, пропускаем этот квадрат
                    logger.warning(f"Cannot process mob level in square {position}: {e}")
                    continue
        
        if best_square:
            logger.info(f"Selected best square {best_square} with level difference {best_score}")
            console.print(f"[yellow]Found suitable square: {best_square} (mobs level ~{target_level + best_score})[/yellow]")
            logger.info(f"Found suitable square: {best_square} (mobs level ~{target_level + best_score})")
            
            # Переходим на лучший квадрат
            result = self.api_client.change_square(best_square)
            
            if result.get("status") == "success":
                console.print(f"[green]Successfully moved to square {best_square}[/green]")
                logger.info(f"Successfully moved to square {best_square}")
                self.player.set_square(best_square)
                # Увеличиваем статистику
                self.session_stats['squares_visited'] += 1
                return True
            else:
                console.print(f"[red]Failed to move to square {best_square}: {result.get('message', 'Unknown error')}[/red]")
                logger.error(f"Failed to move to square {best_square}: {result}")
                return False
        else:
            console.print("[red]No suitable square found[/red]")
            logger.warning("No suitable square found")
            return False

    def _search_target_mob_in_other_directions(self, farming_config: Dict[str, Any]) -> bool:
        """Search for target mob in other directions if not found in current direction"""
        try:
            console.print("[blue]Searching for target mob in other directions...[/blue]")
            logger.info("Searching for target mob in other directions...")
            
            location = farming_config["location"]
            target_mob = farming_config["target_mob"]
            mob_min_level, mob_max_level = farming_config["mob_level_range"]
            
            # Проверяем все направления кроме текущего
            current_direction = self.player.current_direction
            directions_to_check = [d for d in DIRECTIONS if d != current_direction]
            
            for direction in directions_to_check:
                console.print(f"[blue]Checking direction: {direction} for {target_mob}[/blue]")
                logger.info(f"Checking direction: {direction} for {target_mob}")
                
                # Переходим в направление
                result = self.api_client.change_geo(location, direction)
                if result.get("status") != "success":
                    console.print(f"[red]Failed to move to {direction}: {result.get('message', 'Unknown error')}[/red]")
                    logger.error(f"Failed to move to {direction}: {result}")
                    continue
                
                time.sleep(20)  # Задержка 20 секунд между переходами направлений
                self.player.set_location(location, direction)
                # Увеличиваем статистику направлений
                self.session_stats['directions_visited'] += 1
                
                # Получаем информацию о квадратах в этом направлении
                user_info = self.api_client.get_user_info()
                squares = user_info.get("squares", [])
                
                # Ищем квадрат с подходящими мобами
                best_square = None
                best_score = float('inf')
                
                for square in squares:
                    position = square.get("position")
                    lvl_mobs = square.get("lvlMobs")
                    
                    # Пропускаем квадраты с названием локации
                    if lvl_mobs and "locoName" in lvl_mobs:
                        continue
                    
                    if lvl_mobs and "mobLvl" in lvl_mobs:
                        try:
                            mob_level_str = str(lvl_mobs["mobLvl"]).strip()
                            
                            # Обрабатываем диапазоны типа "26-27" или "20-23"
                            if '-' in mob_level_str:
                                level_parts = mob_level_str.split('-')
                                if len(level_parts) == 2:
                                    min_level = int(level_parts[0].strip())
                                    max_level = int(level_parts[1].strip())
                                    mob_level = (min_level + max_level) // 2
                                else:
                                    continue
                            else:
                                mob_level = int(mob_level_str)
                            
                            # Проверяем, что уровень мобов в нужном диапазоне
                            if mob_min_level <= mob_level <= mob_max_level:
                                # Вычисляем "идеальность" квадрата
                                target_level = (mob_min_level + mob_max_level) // 2
                                level_diff = abs(mob_level - target_level)
                                
                                # Бонус за безопасность
                                safety_bonus = 0
                                if mob_level <= self.player.level - 5:
                                    safety_bonus = 10
                                
                                score = level_diff - safety_bonus
                                
                                if score < best_score:
                                    best_score = score
                                    best_square = position
                                
                        except (ValueError, TypeError) as e:
                            logger.warning(f"Cannot process mob level in square {position}: {e}")
                            continue
                
                if best_square:
                    console.print(f"[green]Found suitable square {best_square} in direction {direction}[/green]")
                    logger.info(f"Found suitable square {best_square} in direction {direction}")
                    
                    # Переходим на лучший квадрат
                    result = self.api_client.change_square(best_square)
                    if result.get("status") == "success":
                        self.player.set_square(best_square)
                        # Увеличиваем статистику квадратов
                        self.session_stats['squares_visited'] += 1
                        console.print(f"[green]Successfully moved to {direction} square {best_square}[/green]")
                        logger.info(f"Successfully moved to {direction} square {best_square}")
                        return True
                    else:
                        console.print(f"[red]Failed to move to square {best_square}[/red]")
                        logger.error(f"Failed to move to square {best_square}")
            
            console.print("[yellow]Target mob not found in any direction[/yellow]")
            logger.warning("Target mob not found in any direction")
            return False
                
        except Exception as e:
            console.print(f"[red]Error searching for target mob: {e}[/red]")
            logger.error(f"Error searching for target mob: {e}")
            return False
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get current session statistics"""
        return self.session_stats.copy() 

    def _check_direction_rotation(self, killed_mob_name: str) -> bool:
        """Check if we need to rotate to next direction after killing a mob"""
        if not self.current_farming_config:
            return False
            
        target_mob = self.current_farming_config["target_mob"]
        
        # Проверяем, был ли убит целевой моб
        if killed_mob_name == target_mob:
            self.target_mob_found = True
            console.print(f"[green]🎯 Найден целевой моб: {target_mob}! Остаемся в текущем направлении[/green]")
            logger.info(f"Target mob found: {target_mob}, staying in current direction")
            return False
        
        # Увеличиваем счетчик убитых мобов в текущем направлении
        self.mobs_killed_in_current_direction += 1
        
        console.print(f"[blue]Убито мобов в текущем направлении: {self.mobs_killed_in_current_direction}/{MOBS_PER_DIRECTION}[/blue]")
        logger.info(f"Mobs killed in current direction: {self.mobs_killed_in_current_direction}/{MOBS_PER_DIRECTION}")
        
        # Если достигли лимита мобов в текущем направлении
        if self.mobs_killed_in_current_direction >= MOBS_PER_DIRECTION:
            console.print(f"[yellow]Достигнут лимит {MOBS_PER_DIRECTION} мобов в текущем направлении. Переходим к следующему...[/yellow]")
            logger.info(f"Reached limit of {MOBS_PER_DIRECTION} mobs in current direction, rotating to next")
            return True
        
        return False
    
    def _rotate_to_next_direction(self) -> bool:
        """Rotate to next direction and find suitable square"""
        if not self.current_farming_config:
            return False
            
        location = self.current_farming_config["location"]
        
        # Переходим к следующему направлению
        self.current_direction_index = (self.current_direction_index + 1) % len(DIRECTIONS)
        new_direction = DIRECTIONS[self.current_direction_index]
        
        console.print(f"[blue]Переходим к направлению: {new_direction}[/blue]")
        logger.info(f"Rotating to direction: {new_direction}")
        
        # Переходим в новое направление
        result = self.api_client.change_geo(location, new_direction)
        if result.get("status") != "success":
            console.print(f"[red]Failed to move to {new_direction}: {result.get('message', 'Unknown error')}[/red]")
            logger.error(f"Failed to move to {new_direction}: {result}")
            return False
        
        time.sleep(20)  # Задержка 20 секунд между переходами направлений
        self.player.set_location(location, new_direction)
        # Увеличиваем статистику направлений
        self.session_stats['directions_visited'] += 1
        
        # Получаем информацию о квадратах в новом направлении
        user_info = self.api_client.get_user_info()
        if not user_info or user_info.get('status') != 'success':
            console.print("[red]Failed to get user info for new direction[/red]")
            logger.error("Failed to get user info for new direction")
            return False
        
        squares = user_info.get("squares", [])
        
        # Ищем подходящий квадрат в новом направлении
        if self._find_bow_farming_square(squares, self.current_farming_config):
            # Сбрасываем счетчик мобов для нового направления
            self.mobs_killed_in_current_direction = 0
            console.print(f"[green]Успешно перешли в направление {new_direction}[/green]")
            logger.info(f"Successfully rotated to direction {new_direction}")
            return True
        else:
            console.print(f"[red]Не удалось найти подходящий квадрат в направлении {new_direction}[/red]")
            logger.error(f"Failed to find suitable square in direction {new_direction}")
            return False 

    def _move_to_square(self, square: str) -> bool:
        """Переместиться на указанный квадрат в текущей локации и направлении"""
        try:
            result = self.api_client.change_square(square)
            if result and result.get('status') == 'success':
                self.player.set_square(square)
                self.mob_mapper.set_current_position(
                    self.player.current_location,
                    self.player.current_direction,
                    square
                )
                # Увеличиваем статистику
                self.session_stats['squares_visited'] += 1
                time.sleep(2)  # Короткая задержка для стабильности
                return True
            else:
                logger.error(f"Failed to move to square {square}: {result}")
                return False
        except Exception as e:
            logger.error(f"Exception in _move_to_square: {e}")
            return False

    def _move_to_direction(self, direction: str) -> bool:
        """Переместиться на указанное направление в текущей локации"""
        try:
            result = self.api_client.change_geo(
                self.player.current_location,
                direction,
                type_action="change"
            )
            if result and result.get('status') == 'success':
                self.player.current_direction = direction
                
                # Получаем квадраты из API ответа
                squares_data = result.get('squares', [])
                if squares_data:
                    # Обновляем MobMapper с полными данными квадратов
                    self.mob_mapper.update_direction_squares(squares_data)
                    logger.info(f"Updated direction squares data: {squares_data}")
                    
                    # Выбираем первый подходящий квадрат
                    if self.mob_mapper.current_direction_squares:
                        first_square = self.mob_mapper.current_direction_squares[0]
                        self._move_to_square(first_square)
                    else:
                        logger.warning("No suitable squares found in this direction")
                
                self.mob_mapper.set_current_position(
                    self.player.current_location,
                    direction,
                    self.player.current_square
                )
                # Увеличиваем статистику
                self.session_stats['directions_visited'] += 1
                time.sleep(2)
                return True
            else:
                logger.error(f"Failed to move to direction {direction}: {result}")
                return False
        except Exception as e:
            logger.error(f"Exception in _move_to_direction: {e}")
            return False

    def _move_to_location(self, location: str) -> bool:
        """Переместиться на указанную локацию"""
        try:
            result = self.api_client.change_geo(
                location,
                "north",  # Начинаем с северного направления
                type_action="change"
            )
            if result and result.get('status') == 'success':
                self.player.current_location = location
                self.player.current_direction = "north"
                
                # Получаем квадраты из API ответа
                squares_data = result.get('squares', [])
                if squares_data:
                    # Обновляем MobMapper с полными данными квадратов
                    self.mob_mapper.update_direction_squares(squares_data)
                    logger.info(f"Updated location squares data: {squares_data}")
                    
                    # Выбираем первый подходящий квадрат
                    if self.mob_mapper.current_direction_squares:
                        first_square = self.mob_mapper.current_direction_squares[0]
                        self._move_to_square(first_square)
                    else:
                        logger.warning("No suitable squares found in this location")
                
                self.mob_mapper.set_current_position(
                    location,
                    "north",
                    self.player.current_square
                )
                # Увеличиваем статистику
                self.session_stats['locations_visited'] += 1
                time.sleep(2)
                return True
            else:
                logger.error(f"Failed to move to location {location}: {result}")
                return False
        except Exception as e:
            logger.error(f"Exception in _move_to_location: {e}")
            return False 

    def setup_route_based_farming(self):
        # Получаем уровень игрока
        player_info = self.api_client.get_user_info()
        if player_info.get("status") == "success":
            player_data = player_info.get("data", {})
            player_level = player_data.get("level", 20)
            self.player.set_level(player_level)
        else:
            player_level = 20
        self.current_route = self.world_router.build_optimal_route(player_level, self.target_mobs_per_square)
        if not self.current_route:
            logger.error("[ROUTE] Не найдено подходящих квадратов для фарма!")
            return False
        self.current_route_index = 0
        self.mobs_killed_on_current_square = 0
        first_point = self.current_route[0]
        success = self._move_to_route_point(first_point)
        if not success:
            logger.error("[ROUTE] Не удалось перейти к первому квадрату!")
            return False
        return True

    def _move_to_route_point(self, route_point: RoutePoint) -> bool:
        """Переход к точке маршрута (без поиска альтернатив, только логирование)"""
        try:
            # Переходим в локацию и направление
            result = self.api_client.change_geo(route_point.location, route_point.direction)
            logger.info(f"[ROUTE] change_geo: location={route_point.location}, direction={route_point.direction}, result={result}")
            if result.get("status") != "success":
                logger.error(f"[ROUTE] Ошибка перехода в {route_point.location_name} | {route_point.direction_name}: {result}")
                return False
            time.sleep(2)
            self.player.set_location(route_point.location, route_point.direction)
            self.session_stats['directions_visited'] += 1

            # Переходим на квадрат
            logger.info(f"[ROUTE] change_square: square={route_point.square}")
            result = self.api_client.change_square(route_point.square)
            logger.info(f"[ROUTE] change_square response: {result}")
            if result.get("status") != "success":
                logger.error(f"[ROUTE] Ошибка перехода на квадрат {route_point.square}: {result}")
                # Можно добавить отображение ошибки в rich-дисплей, если нужно
                return False
            time.sleep(2)
            self.player.set_square(route_point.square)
            self.session_stats['squares_visited'] += 1
            self.mob_mapper.set_position(route_point.location, route_point.direction, route_point.square)
            self.mob_mapper.set_player_level(self.player.level)
            return True
        except Exception as e:
            logger.error(f"Ошибка перехода к точке маршрута: {e}")
            return False
    
    def _get_numeric_level(self, mob_level) -> int:
        """Преобразует уровень моба в числовое значение для сортировки"""
        if isinstance(mob_level, int):
            return mob_level
        elif isinstance(mob_level, str):
            # Обработка диапазонов типа "86-88"
            if '-' in mob_level:
                try:
                    min_level, max_level = map(int, mob_level.split('-'))
                    return min_level  # Используем минимальный уровень для сортировки
                except:
                    return 999  # Высокое значение для нераспознанных форматов
            else:
                try:
                    return int(mob_level)
                except:
                    return 999
        else:
            return 999

    def _move_to_next_route_point(self):
        """Переход к следующей точке маршрута"""
        max_attempts = len(self.current_route)  # Максимальное количество попыток
        attempts = 0
        
        while attempts < max_attempts:
            self.current_route_index += 1
            
            # Проверяем, не достигли ли конца маршрута
            if self.current_route_index >= len(self.current_route):
                console.print("[bold green]🎉 Маршрут завершен! Начинаем заново...[/bold green]")
                self.current_route_index = 0
                self.mobs_killed_on_current_square = 0
            
            # Переходим к следующей точке
            next_point = self.current_route[self.current_route_index]
            console.print(f"[blue]Переходим к следующему квадрату: {next_point.location_name} | {next_point.direction_name} | {next_point.square}[/blue]")
            
            success = self._move_to_route_point(next_point)
            if success:
                self.mobs_killed_on_current_square = 0
                self.state_manager.change_state(GameState.CITY, "Moved to next route point")
                self.current_mob_group = None
                self.explore_done = False
                return True
            else:
                console.print(f"[yellow]⚠️ Пропускаем недоступный квадрат {next_point.square}[/yellow]")
                attempts += 1
                continue
        
        # Если все квадраты недоступны
        console.print("[red]❌ Все квадраты в маршруте недоступны![/red]")
        return False 