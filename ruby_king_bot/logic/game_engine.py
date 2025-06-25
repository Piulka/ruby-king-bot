"""
Game Engine - Main game loop and state management
"""

import time
import logging
from typing import Optional, Dict, Any
from rich.console import Console

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

logger = logging.getLogger(__name__)
console = Console()

class GameEngine:
    """Main game engine that manages the game loop and state transitions"""
    
    def __init__(self):
        self.api_client = APIClient()
        self.state_manager = GameStateManager()
        self.player = Player()
        self.display = GameDisplay()
        
        # Game state variables
        self.current_mob_group: Optional[MobGroup] = None
        self.rest_end_time: Optional[float] = None
        self.explore_done = False
        self.total_mobs_killed = 0
        
        # Handlers
        self.combat_handler = CombatHandler(self.api_client, self.player, self.display)
        self.exploration_handler = ExplorationHandler(self.api_client, self.display)
        self.rest_handler = RestHandler(self.api_client, self.display)
        self.data_extractor = DataExtractor()
        
        # Statistics
        self.session_stats = {
            'mobs_killed': 0,
            'total_exp': 0,
            'session_gold': 0,
            'session_start': time.time()
        }
    
    def initialize(self):
        """Initialize the game engine"""
        console.print("[bold blue]Starting Ruby King Bot...[/bold blue]")
        console.print("[green]Bot initialized successfully[/green]")
        console.print("[yellow]Continuous mode: Bot will explore territory after each victory[/yellow]")
        
        # Initialize player data if needed
        # self._initialize_player_data()
    
    def run(self):
        """Main game loop"""
        with self.display.get_live_display() as live:
            while True:
                try:
                    current_time = time.time()
                    current_state = self.state_manager.get_current_state()
                    
                    # Update display
                    self._update_display(current_time, current_state)
                    
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
                    time.sleep(1)
                    
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
            last_skill_time=self.player.last_skill_time
        )
        
        # Update statistics
        self.display.update_stats(
            current_gold=self.player.get_gold_count(),
            current_skulls=self.player.get_skulls_count()
        )
    
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
            return
        
        current_target = self.current_mob_group.get_current_target()
        if not current_target:
            self.display.print_message("No current target in mob group", "error")
            return
        
        # Check if low damage situation was detected
        if self.combat_handler.low_damage_handled:
            # Handle low damage situation
            result = self.combat_handler.low_damage_handler.handle_low_damage_situation(
                current_target, 
                self.current_mob_group, 
                current_time,
                self.combat_handler.situation_type
            )
            
            if result:
                # Low damage handling completed, reset flag and continue normal flow
                self.combat_handler.low_damage_handled = False
                self.combat_handler._reset_low_damage_tracking()
                self.state_manager.change_state(GameState.CITY, "Low damage handling completed")
                self.current_mob_group = None
                self.explore_done = False
                return
        
        # Handle combat actions
        combat_result = self.combat_handler.handle_combat_round(
            current_target, 
            current_time, 
            self.current_mob_group
        )
        
        if combat_result == 'victory':
            # Combat ended with victory
            self._handle_combat_victory()
        elif combat_result == 'continue':
            # Combat continues
            pass
        else:
            # Combat ended with failure
            self._handle_combat_failure()
    
    def _handle_combat_victory(self):
        """Handle combat victory"""
        self.state_manager.change_state(GameState.CITY, "Combat ended - victory")
        self.current_mob_group = None
        self.explore_done = False  # Reset exploration flag
    
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
            player_info = self.api_client.get_user_info()
            if player_info and 'player' in player_info:
                self.player.update_from_api_response(player_info)
                console.print("[green]Player data initialized successfully[/green]")
            else:
                console.print("[yellow]Could not get player data, using defaults[/yellow]")
        except Exception as e:
            console.print(f"[yellow]Failed to get player data: {e}, using defaults[/yellow]")
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get current session statistics"""
        return self.session_stats.copy() 