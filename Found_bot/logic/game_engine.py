"""
Game Engine - Main game loop and state management
"""

import time
import logging
from typing import Dict, Any
from rich.console import Console

from api.client import APIClient
from core.game_state import GameState, GameStateManager
from core.player import Player
from core.mob import MobGroup
from ui.display import GameDisplay
from config.settings import Settings
from logic.combat_handler import CombatHandler
from logic.exploration_handler import ExplorationHandler
from logic.rest_handler import RestHandler
from logic.data_extractor import DataExtractor
from logic.route_manager import RouteManager

logger = logging.getLogger(__name__)
console = Console()

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
        
        # Route management
        self.route_manager = None
        
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
            'session_start': time.time()
        }
    
    def initialize(self):
        """Initialize the game engine"""
        console.print("[bold blue]Запуск Ruby King Bot...[/bold blue]")
        console.print("[green]Бот успешно инициализирован[/green]")
        console.print("[yellow]Режим фарма по маршруту: бот будет следовать заранее заданному пути[/yellow]")
        
        # Инициализация данных игрока
        console.print("[cyan]Инициализация данных игрока...[/cyan]")
        self._initialize_player_data()
        console.print("[green]Данные игрока успешно инициализированы[/green]")
        
        # Инициализация менеджера маршрута
        console.print(f"[cyan]Инициализация маршрута для уровня игрока {self.player.level}...[/cyan]")
        self._initialize_route_manager()
        if self.route_manager:
            console.print(f"[green]Маршрут инициализирован: {len(self.route_manager.route)} клеток[/green]")
        
        # Настройка среды фарма
        console.print("[cyan]Настройка среды фарма...")
        if not self._setup_farming_environment():
            console.print("[red]Не удалось настроить среду фарма, бот может работать некорректно[/red]")
            logger.error("Не удалось настроить среду фарма")
        else:
            console.print("[green]Среда фарма готова, запуск основного цикла[/green]")
            logger.info("Среда фарма готова")
    
    def run(self):
        """Main game loop"""
        with self.display.get_live_display() as live:
            while True:
                try:
                    current_time = time.time()
                    current_state = self.state_manager.get_current_state()
                    
                    # Update display once per second
                    if current_time - self.last_display_update >= 1.0:
                        self._update_display(current_time, current_state)
                        self.last_display_update = current_time
                    
                    # Handle current state
                    if current_state == GameState.CITY:
                        self._handle_city_state()
                    elif current_state == GameState.COMBAT:
                        self._handle_combat_state(current_time)
                    elif current_state == GameState.RESTING:
                        self._handle_resting_state(current_time)
                    else:
                        logger.error(f"Unknown state: {current_state}")
                        break
                    
                    # Small delay to prevent excessive CPU usage
                    time.sleep(0.1)  # Small delay to prevent CPU overuse
                    
                except KeyboardInterrupt:
                    console.print("\n[yellow]Bot stopped by user[/yellow]")
                    break
                except Exception as e:
                    logger.error(f"Critical error in game loop: {e}")
                    self.display.print_message(f"Critical error: {e}", "error")
                    time.sleep(60)  # Wait before retry
    
    def _update_display(self, current_time: float, current_state: GameState):
        """Update the display with current game state"""
        # Get player data
        player_data = self.player.get_stats_summary()
        
        # Get mob data
        mob_data = None
        mob_group_data = None
        if self.current_mob_group:
            current_target = self.current_mob_group.get_current_target()
            if current_target:
                mob_data = {
                    'name': current_target.name,
                    'hp': current_target.hp,
                    'max_hp': current_target.max_hp,
                    'level': current_target.level
                }
            
            # Get all mobs for display
            all_mobs = self.current_mob_group.get_all_mobs()
            if len(all_mobs) > 1:
                mob_group_data = self.current_mob_group.get_all_mobs_with_status()
        
        # Calculate cooldowns
        attack_cooldown = max(0, self.player.GLOBAL_COOLDOWN - (current_time - self.player.last_attack_time))
        skill_cooldown = max(0, self.player.SKILL_COOLDOWN - (current_time - self.player.last_skill_time))
        heal_cooldown = max(0, self.player.HEAL_COOLDOWN - (current_time - self.player.last_heal_time))
        mana_cooldown = max(0, self.player.MANA_COOLDOWN - (current_time - self.player.last_mana_time))
        
        # Calculate rest time if resting
        rest_time = None
        if current_state == GameState.RESTING and self.rest_end_time:
            rest_time = self.rest_end_time
        
        # Update display
        self.display.update_display(
            current_state=current_state.value,
            player_data=player_data,
            mob_data=mob_data,
            mob_group_data=mob_group_data,
            attack_cooldown=attack_cooldown,
            heal_cooldown=heal_cooldown,
            skill_cooldown=skill_cooldown,
            mana_cooldown=mana_cooldown,
            rest_time=rest_time,
            player_name="Piulok",
            last_attack_time=self.player.last_attack_time,
            last_skill_time=self.player.last_skill_time,
            route_data=self.route_manager.get_route_display_data() if self.route_manager else None
        )
        
        # Update statistics
        self.display.update_stats(
            current_gold=self.player.get_gold_count(),
            current_skulls=self.player.get_skulls_count()
        )
    
    def _handle_city_state(self):
        """Handle city state - exploration and route management"""
        # Сохраняем индекс маршрута перед уходом в город
        if self.route_manager:
            self.route_manager.save_current_index()
        
        # Check if we need to move to next square
        if self.route_manager and self.route_manager.should_move_to_next_square():
            console.print(f"[yellow]Moving to next square in route...[/yellow]")
            logger.info("Moving to next square in route")
            self.route_manager.move_to_next_square(display=self.display)
            self.explore_done = False  # Reset exploration for new square
        
        if not self.explore_done:
            # Try to explore territory
            result = self.exploration_handler.explore_territory()
            
            # --- SPEC_BATS обход ---
            bats_attempts = 0
            while result and result.get('action') == 'SPEC_BATS':
                bats_attempts += 1
                console.print(f"[yellow]Обнаружено событие SPEC_BATS (летучие мыши), попытка {bats_attempts}...[/yellow]")
                logger.info(f"SPEC_BATS detected, attempt {bats_attempts}")
                self.display.update_stats(bats_events=1)
                self.display.show_bats_event_message()
                self.display.update_display(
                    current_state=str(self.state_manager.current_state),
                    player_data=self.player.to_dict() if hasattr(self.player, 'to_dict') else {},
                    mob_data=None,
                    mob_group_data=None
                )
                # Новый обход: ждем 2 секунды, отправляем запрос на /api/user/vesna, затем продолжаем исследование
                logger.info("Жду 2 секунды перед обходом SPEC_BATS...")
                time.sleep(2)
                logger.info("Отправляю запрос на обход летучих мышей (/api/user/vesna)...")
                response = self.api_client.complete_bats_event()
                logger.info(f"SPEC_BATS server response: {response}")
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
                if mob_group_data and isinstance(mob_group_data, list):
                    flat_mobs = []
                    for mob in mob_group_data:
                        if isinstance(mob, list):
                            flat_mobs.extend(mob)
                        else:
                            flat_mobs.append(mob)
                    mob_group_data = flat_mobs
                mob_names = [mob['name'] for mob in mob_group_data if isinstance(mob, dict) and 'name' in mob]
                self.display.print_message(f"🔍 Найдены враги: {', '.join(mob_names)}", "info")
                
                # Check and use skill immediately after exploration if conditions are met
                current_time = time.time()
                if current_target and self._should_use_skill_after_exploration(current_target, current_time):
                    self.display.print_message("⚡ Проверяем возможность использования усиленного удара...", "info")
                    skill_result = self.combat_handler._use_skill(current_target, current_time, self.current_mob_group)
                    if skill_result == 'victory':
                        self._handle_combat_victory()
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
    
    def _handle_combat_state(self, current_time: float):
        """Handle combat state - combat logic and potion management"""
        if not self.current_mob_group:
            self.display.print_message("No mob group in combat state", "error")
            # Если нет группы мобов в состоянии боя, переводим в город
            self.state_manager.change_state(GameState.CITY, "No mob group in combat state")
            self.explore_done = False  # Сбрасываем флаг исследования
            return
        current_target = self.current_mob_group.get_current_target()
        if not current_target:
            self.display.print_message("No current target in mob group", "error")
            return

        # Основной боевой цикл
        combat_result = self.combat_handler.handle_combat_round(current_target, current_time, self.current_mob_group)
        if combat_result == 'victory':
            self._handle_combat_victory()
            return
        elif combat_result == 'failure':
            self._handle_combat_failure()
            return
        elif combat_result == 'recover':
            self.display.print_message("▶️ Запуск процедуры восстановления (LowDamageHandler)...", "warning")
            result = self.combat_handler.low_damage_handler.handle_low_damage_situation(
                current_target,
                self.current_mob_group,
                current_time,
                self.combat_handler.situation_type
            )
            if result:
                self.combat_handler.low_damage_handled = False
                self.combat_handler._reset_low_damage_tracking()
                self.display.print_message("✅ Восстановление завершено, возвращаемся к фарму!", "success")
                # Сбрасываем флаг исследования и переходим в город для запуска исследования
                self.explore_done = False
                self.current_mob_group = None  # Очищаем группу мобов
                self.state_manager.change_state(GameState.CITY, "Восстановление завершено")
            else:
                self.display.print_message("❌ Ошибка восстановления, попробуйте позже", "error")
            return
        # иначе просто продолжаем бой (continue)
    
    def _handle_combat_victory(self):
        """Handle combat victory"""
        if self.current_mob_group:
            current_target = self.current_mob_group.get_current_target()
            
            # Update route manager
            if self.route_manager:
                self.route_manager.increment_mob_kills()
                
                # Check if should move to next square
                if self.route_manager.should_move_to_next_square():
                    console.print(f"[yellow]Killed {self.route_manager.mobs_per_square} mobs on current square, moving to next[/yellow]")
                    logger.info(f"Killed {self.route_manager.mobs_per_square} mobs on current square, moving to next")
                    self.route_manager.move_to_next_square()
                    self.explore_done = False  # Reset exploration for new square
            
            # Clear current mob group and change state to CITY
            self.current_mob_group = None
            self.explore_done = False
            self.state_manager.change_state(GameState.CITY, "Combat ended - victory")
    
    def _handle_combat_failure(self):
        """Handle combat failure"""
        self.state_manager.change_state(GameState.CITY, "Combat ended - failure")
        self.current_mob_group = None
        self.explore_done = False  # Reset exploration flag
        self.display.print_message("🔄 Начинаем новое исследование...", "info")
    
    def _handle_resting_state(self, current_time: float):
        """Handle resting state"""
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
            current_time = time.time()
            self._update_display(current_time, GameState.CITY)
            
            # 2. Проверяем текущую позицию
            geo = user_info.get('geo', 'city')
            console.print(f"[yellow]Current location: {geo}[/yellow]")
            logger.info(f"Current location: {geo}")
            
            if geo == 'city':
                # Игрок в городе - нужно купить зелья и перейти в фарм-зону
                console.print("[blue]Player is in city, preparing for farming...[/blue]")
                logger.info("Player is in city, preparing for farming...")
                
                # Покупаем зелья
                if not self._buy_potions_if_needed():
                    console.print("[red]Failed to buy potions[/red]")
                    return False
                
                # Переходим в фарм-зону
                if not self._go_to_farm_zone():
                    console.print("[red]Failed to go to farm zone[/red]")
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
                
                if not self._move_to_route_point():
                    console.print("[red]Failed to move to route point[/red]")
                    return False
            
            console.print("[green]Farming environment setup completed[/green]")
            logger.info("Farming environment setup completed")
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
    
    def _go_to_location(self):
        """Go to location (loco_3) to load mob information"""
        try:
            console.print("[blue]Going to location...[/blue]")
            logger.info("Going to location...")
            
            # Выбираем локацию в зависимости от уровня игрока
            player_level = self.player.level
            if player_level >= 10:
                location = "loco_3"
                direction = "south"  # Добавляем направление
                console.print(f"[blue]Going to {location} {direction} (level {player_level} >= 10).[/blue]")
                logger.info(f"Going to {location} {direction} (level {player_level} >= 10).")
            else:
                location = "loco_0"
                direction = "north"  # Добавляем направление
                console.print(f"[blue]Going to {location} {direction} (level {player_level} < 10).[/blue]")
                logger.info(f"Going to {location} {direction} (level {player_level} < 10).")
            
            result = self.api_client.change_geo(location, direction)
            
            if result.get("status") == "success":
                console.print(f"[green]Successfully moved to location[/green]")
                logger.info("Successfully moved to location")
                time.sleep(2)  # Пауза 2 секунды
                return True
            else:
                console.print(f"[red]Failed to move to location: {result.get('message', 'Unknown error')}[/red]")
                logger.error(f"Failed to move to location: {result}")
                return False
            
        except Exception as e:
            console.print(f"[red]Error moving to location: {e}[/red]")
            logger.error(f"Error moving to location: {e}")
            return False
    
    def _move_to_route_point(self) -> bool:
        """Move to current route point"""
        try:
            if not self.route_manager or not self.route_manager.route:
                console.print("[red]No route available[/red]")
                logger.error("No route available")
                return False
            
            current_point = self.route_manager.get_current_point()
            if not current_point:
                console.print("[red]No current route point[/red]")
                logger.error("No current route point")
                return False
            
            console.print(f"[blue]Moving to route point: {current_point.location_name}/{current_point.direction_name}/{current_point.square}[/blue]")
            logger.info(f"Moving to route point: {current_point.location_name}/{current_point.direction_name}/{current_point.square}")
            
            # Move to location and direction
            result = self.api_client.change_geo(current_point.location, current_point.direction)
            if result.get("status") != "success":
                console.print(f"[red]Failed to move to {current_point.location_name}/{current_point.direction_name}[/red]")
                logger.error(f"Failed to move to {current_point.location_name}/{current_point.direction_name}")
                return False
            
            time.sleep(2)  # Delay after location change
            
            # Move to square
            result = self.api_client.change_square(current_point.square)
            if result.get("status") != "success":
                console.print(f"[red]Failed to move to square {current_point.square}[/red]")
                logger.error(f"Failed to move to square {current_point.square}")
                return False
            
            time.sleep(1)  # Delay after square change
            
            console.print(f"[green]Successfully moved to {current_point.location_name}/{current_point.direction_name}/{current_point.square}[/green]")
            logger.info(f"Successfully moved to {current_point.location_name}/{current_point.direction_name}/{current_point.square}")
            return True
            
        except Exception as e:
            console.print(f"[red]Error moving to route point: {e}[/red]")
            logger.error(f"Error moving to route point: {e}")
            return False
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get current session statistics"""
        return self.session_stats.copy()

    def _initialize_route_manager(self):
        """Initialize route manager with player level"""
        try:
            logger.info("Starting route manager initialization...")
            player_level = self.player.level
            console.print(f"[blue]Initializing route manager for player level {player_level}...[/blue]")
            logger.info(f"Player level: {player_level}")
            
            self.route_manager = RouteManager(player_level)
            logger.info("RouteManager instance created successfully")
            
            if self.route_manager.route:
                console.print(f"[green]Route initialized with {len(self.route_manager.route)} squares[/green]")
                logger.info(f"Route initialized with {len(self.route_manager.route)} squares")
            else:
                console.print("[red]Failed to build route - no suitable squares found[/red]")
                logger.error("Failed to build route - no suitable squares found")
                
        except Exception as e:
            console.print(f"[red]Error initializing route manager: {e}[/red]")
            logger.error(f"Error initializing route manager: {e}")
            logger.exception("Full traceback:")
            self.route_manager = None 