"""
Combat Handler - Manages combat actions, skills, and potion usage
"""

import time
import logging
import re
import os
import json
from typing import Optional, Dict, Any, Literal
from core.mob import Mob, MobGroup
from core.player import Player
from api.client import APIClient
from ui.display import GameDisplay
from config.settings import Settings
from logic.data_extractor import DataExtractor
from logic.low_damage_handler import LowDamageHandler

logger = logging.getLogger(__name__)

class CombatHandler:
    """Handles all combat-related actions and logic"""
    
    def __init__(self, api_client: APIClient, player: Player, display: GameDisplay):
        self.api_client = api_client
        self.player = player
        self.display = display
        self.data_extractor = DataExtractor()
        self.low_damage_handler = LowDamageHandler(api_client, player, display)
        
        # Combat state
        self.skill_used = False  # Flag to track if skill was used in current round
        
        # Low damage tracking
        self.low_damage_count = 0  # Count of consecutive low damage attacks
        self.last_attack_damages = []  # Last 3 attack damages
        self.combat_paused = False  # Flag to pause combat
        self.low_damage_handled = False  # Flag to track if low damage was handled
        self.situation_type = "low_damage"  # Type of situation: "low_damage" or "low_potions"
    
    def handle_combat_round(self, current_target: Mob, current_time: float, mob_group: MobGroup) -> Literal['victory', 'continue', 'failure', 'recover']:
        """
        Handle one round of combat
        
        Args:
            current_target: Current target mob
            current_time: Current timestamp
            mob_group: Current mob group
            
        Returns:
            'victory' if combat ended with victory
            'continue' if combat continues
            'failure' if combat ended with failure
            'recover' if combat ended with recovery
        """
        self.skill_used = False  # Reset flag at start of round
        self.need_recover = False
        
        # Check if combat is paused due to low damage
        if self.combat_paused:
            time.sleep(1)
            return 'continue'
        
        # Check if potions are running low
        if self._check_low_potions():
            self.need_recover = True
        # Check if low damage pattern is detected (by last 3 attacks)
        if hasattr(self, 'last_attack_damages') and len(self.last_attack_damages) == 3:
            average_damage = self.display.get_average_damage()
            if average_damage > 0 and all(damage <= average_damage / 2 for damage in self.last_attack_damages):
                if not self.low_damage_handled:
                    self.need_recover = True
        
        if self.need_recover or self.low_damage_handled:
            self.display.print_message("🚨 Переход к восстановлению!", "warning")
            return 'recover'
        
        # 1. Check and use healing potion
        if self._should_use_heal_potion(current_time):
            heal_result = self._use_healing_potion(current_time)
            if heal_result == 'failure':
                return 'failure'
        
        # 2. Check and use mana potion
        if self._should_use_mana_potion(current_time):
            mana_result = self._use_mana_potion(current_time)
            if mana_result == 'failure':
                return 'failure'
        
        # 3. Use skill if conditions are met
        if self._should_use_skill(current_target, current_time):
            skill_result = self._use_skill(current_target, current_time, mob_group)
            if skill_result == 'victory':
                return 'victory'
            elif skill_result == 'failure':
                return 'failure'
            # If skill was used successfully, continue to next round
            return 'continue'
        
        # 4. Use regular attack
        if self._should_attack(current_time, current_target):
            attack_result = self._use_attack(current_target, current_time, mob_group)
            if attack_result == 'victory':
                return 'victory'
            elif attack_result == 'failure':
                return 'failure'
        
        # 5. Return immediately - no sleep here, main loop handles timing
        return 'continue'
    
    def _should_use_heal_potion(self, current_time: float) -> bool:
        """Check if healing potion should be used"""
        hp_percentage = (self.player.hp / self.player.max_hp * 100) if self.player.max_hp > 0 else 100
        return hp_percentage < Settings.HEAL_THRESHOLD and self.player.can_use_heal_potion(current_time)
    
    def _should_use_mana_potion(self, current_time: float) -> bool:
        """Check if mana potion should be used"""
        mp_percentage = (self.player.mp / self.player.max_mp * 100) if self.player.max_mp > 0 else 100
        return mp_percentage < Settings.MANA_THRESHOLD and self.player.can_use_mana_potion(current_time)
    
    def _should_use_skill(self, current_target: Mob, current_time: float) -> bool:
        """Check if skill should be used"""
        return (current_target and 
                current_target.hp > Settings.SKILL_HP_THRESHOLD and 
                self.player.can_use_skill(current_time))
    
    def _should_attack(self, current_time: float, current_target: Mob) -> bool:
        """Check if regular attack should be used"""
        return (not self.skill_used and 
                self.player.can_attack(current_time) and 
                current_target and 
                current_target.hp > 0)
    
    def _use_healing_potion(self, current_time: float) -> Literal['success', 'failure']:
        """Use healing potion"""
        try:
            heal_result = self.api_client.use_healing_potion()
            self._log_api_response(heal_result, "use_healing_potion")
            self.player.record_heal(current_time)
            
            # Update player data from response
            if "user" in heal_result:
                self.player.update_from_api_response(heal_result)
            
            self.display.print_message("❤️ Использовал зелье лечения!", "success")
            self.display.update_stats(hp_potions_used=1)
            
            return 'success'
            
        except Exception as e:
            self.display.print_message(f"Network error: {e}. Waiting 60 seconds before retry...", "error")
            time.sleep(60)
            return 'failure'
    
    def _use_mana_potion(self, current_time: float) -> Literal['success', 'failure']:
        """Use mana potion"""
        try:
            mana_result = self.api_client.use_mana_potion()
            self._log_api_response(mana_result, "use_mana_potion")
            self.player.record_mana(current_time)
            
            # Update player data from response
            if "user" in mana_result:
                self.player.update_from_api_response(mana_result)
            
            self.display.print_message("🔵 Использовал зелье маны!", "success")
            self.display.update_stats(mp_potions_used=1)
            
            return 'success'
            
        except Exception as e:
            self.display.print_message(f"Network error: {e}. Waiting 60 seconds before retry...", "error")
            time.sleep(60)
            return 'failure'
    
    def _use_skill(self, current_target: Mob, current_time: float, mob_group: MobGroup) -> Literal['victory', 'continue', 'failure']:
        """Use skill attack"""
        self.skill_used = True  # Set flag BEFORE using skill
        
        try:
            skill_result = self.api_client.use_skill(current_target.farm_id)
            self._log_api_response(skill_result, "use_skill")
            self.player.record_skill(current_time)
            
            # Update player data from response
            self.player.update_from_api_response(skill_result)
            
            if isinstance(skill_result, dict):
                # Check if battle is already closed
                if skill_result.get('status') == 'close':
                    # Battle is already finished, treat as victory
                    return self._handle_victory(skill_result, mob_group)
                elif skill_result.get('status') == 'fail':
                    return self._handle_combat_failure(skill_result, "skill")
                elif skill_result.get('status') == 'success':
                    return self._handle_combat_success(skill_result, current_target, mob_group, "skill")
            
            return 'continue'
            
        except Exception as e:
            self.display.print_message(f"Network error: {e}. Waiting 60 seconds before retry...", "error")
            time.sleep(60)
            return 'failure'
    
    def _use_attack(self, current_target: Mob, current_time: float, mob_group: MobGroup) -> Literal['victory', 'continue', 'failure']:
        """Use regular attack"""
        # Не выводим сообщение здесь, оно будет в _display_combat_results
        
        try:
            attack_result = self.api_client.attack_mob(current_target.farm_id)
            self._log_api_response(attack_result, "attack_mob")
            self.player.record_attack(current_time)
            
            if isinstance(attack_result, dict):
                # Check if battle is already closed
                if attack_result.get('status') == 'close':
                    # Battle is already finished, treat as victory
                    return self._handle_victory(attack_result, mob_group)
                elif attack_result.get('status') == 'fail':
                    return self._handle_combat_failure(attack_result, "attack")
                elif attack_result.get('status') == 'success':
                    return self._handle_combat_success(attack_result, current_target, mob_group, "attack")
            
            return 'continue'
            
        except Exception as e:
            self.display.print_message(f"Network error: {e}. Waiting 60 seconds before retry...", "error")
            time.sleep(60)
            return 'failure'
    
    def _handle_combat_failure(self, result: Dict[str, Any], action_type: str) -> Literal['failure']:
        """Handle combat action failure"""
        message = result.get('message', '')
        
        if 'Монстр не найден' in message or 'эта цель уже была мертва' in message:
            self.display.print_message(f"{action_type.title()} failed: mob not found", "info")
            return 'failure'
        else:
            self.display.print_message(f"{action_type.title()} failed: {message}", "error")
            return 'failure'
    
    def _handle_combat_success(self, result: Dict[str, Any], current_target: Mob, mob_group: MobGroup, action_type: str) -> Literal['victory', 'continue']:
        """Handle successful combat action"""
        # Get damage from arrLogs first
        damage_dealt = self._extract_damage_dealt(result)
        damage_received = self._extract_damage_received(result)
        
        # Update player data from response (for accurate HP tracking)
        if "user" in result:
            self.player.update_from_api_response(result)
        
        # Update mob HP from response
        if "mob" in result:
            mob_data = result["mob"]
            if current_target and current_target.farm_id == mob_data.get("farmId"):
                old_hp = current_target.hp
                current_target.hp = mob_data.get("hp", current_target.hp)
                current_target.max_hp = mob_data.get("maxHp", current_target.max_hp)
                
                # If we couldn't get damage from arrLogs, calculate from HP difference
                if damage_dealt == 0 and old_hp > current_target.hp:
                    damage_dealt = old_hp - current_target.hp
                
                # Display combat results
                self._display_combat_results(action_type, damage_dealt, damage_received, current_target)
        else:
            # No mob data, but we still have damage info - display it
            if current_target:
                self._display_combat_results(action_type, damage_dealt, damage_received, current_target)
            else:
                # No current target, but we have damage - display basic info
                self._display_basic_combat_results(action_type, damage_dealt, damage_received)
        
        # Check for victory
        if result.get('statusBattle') == 'win':
            return self._handle_victory(result, mob_group)
        
        # Update mob group from response
        mob_group.update_from_combat_response(result)
        
        # Check if current target died
        if current_target and current_target.hp <= 0:
            self.display.print_message(f"💀 {current_target.name} повержен!", "success")
            
            # Update killed mobs statistics
            self.display.update_killed_mobs(current_target.name)
            
            # Switch to next target
            next_target = mob_group.switch_to_next_alive_target()
            if next_target:
                self.display.print_message(f"🎯 Переключился на: {next_target.name} (HP: {next_target.hp})", "info")
            else:
                # All mobs dead but statusBattle not 'win' - treat as victory
                return self._handle_victory(result, mob_group)
        
        # Сохраняем подробную информацию о мобе (если есть)
        if "mobs" in result:
            for mob in result["mobs"]:
                self.update_mob_database(mob)
        elif "mob" in result:
            self.update_mob_database(result["mob"])
        
        return 'continue'
    
    def _extract_damage_received(self, result: Dict[str, Any]) -> int:
        """Extract damage received from combat logs"""
        damage_received = 0
        
        # First try to get damage from user data (most accurate)
        if "user" in result:
            user_data = result["user"]
            old_hp = self.player.hp
            new_hp = user_data.get("hp", old_hp)
            if old_hp > new_hp:
                damage_received = old_hp - new_hp
        
        # If no damage from user data, try arrLogs
        if damage_received == 0:
            arr_logs = result.get('arrLogs', [])
            for log_entry in arr_logs:
                # Ищем урон, нанесенный мобом игроку (isMob: true, defname: "Piulok")
                if log_entry.get('isMob') == True and log_entry.get('defname') == 'Piulok':
                    damage_received = log_entry.get('damage', 0)
                    break
                # Также проверяем messages на случай если структура другая
                messages = log_entry.get('messages', [])
                for message in messages:
                    # Ищем сообщения типа "моб наносит X урон игроку"
                    if 'наносит' in message and 'урон' in message and 'вам' in message:
                        damage_match = re.search(r'наносит (\d+) урон', message)
                        if damage_match:
                            damage_received = int(damage_match.group(1))
                            break
                    # Альтернативный поиск - урон от моба
                    elif 'наносит' in message and 'урон' in message and not 'вы' in message:
                        damage_match = re.search(r'наносит (\d+) урон', message)
                        if damage_match:
                            damage_received = int(damage_match.group(1))
                            break
        
        return damage_received
    
    def _extract_damage_dealt(self, result: Dict[str, Any]) -> int:
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
    
    def _display_combat_results(self, action_type: str, damage_dealt: int, damage_received: int, current_target: Mob):
        """Display combat results"""
        action_icon = "⚡" if action_type == "skill" else "⚔️"
        action_name = "[yellow]Усиленный удар[/yellow]" if action_type == "skill" else "[cyan]Атака[/cyan]"
        
        # Update damage statistics only for regular attacks
        if action_type == "attack":
            self.display.update_damage_stats(damage_dealt)
            
            # Check for low damage pattern
            self._check_low_damage_pattern(damage_dealt)
        
        # Формируем сообщение с уроном в одной строке
        if damage_dealt > 0:
            if damage_received > 0:
                message = f"{action_icon} {action_name} по [bold cyan]{current_target.name}[/bold cyan]: нанес [bold red]{damage_dealt}[/bold red] урона, получил [bold red]{damage_received}[/bold red] урона."
            else:
                message = f"{action_icon} {action_name} по [bold cyan]{current_target.name}[/bold cyan]: нанес [bold red]{damage_dealt}[/bold red] урона."
        else:
            if damage_received > 0:
                message = f"{action_icon} {action_name} по [bold cyan]{current_target.name}[/bold cyan]: промах! Получил [bold red]{damage_received}[/bold red] урона."
            else:
                message = f"{action_icon} {action_name} по [bold cyan]{current_target.name}[/bold cyan]: промах!"
        
        # Определяем уровень сообщения
        level = "success" if damage_dealt > 0 else "warning"
        self.display.print_message(message, level)
    
    def _check_low_damage_pattern(self, damage_dealt: int):
        """Check if damage is consistently low and handle low damage situation"""
        if damage_dealt > 0:  # Only check actual hits
            self.last_attack_damages.append(damage_dealt)
            
            # Keep only last 3 attacks
            if len(self.last_attack_damages) > 3:
                self.last_attack_damages = self.last_attack_damages[-3:]
            
            # Check if we have 3 consecutive attacks
            if len(self.last_attack_damages) == 3:
                average_damage = self.display.get_average_damage()
                
                # Check if all 3 attacks are less than half of average
                if average_damage > 0 and all(damage <= average_damage / 2 for damage in self.last_attack_damages):
                    if not self.low_damage_handled:
                        self.low_damage_handled = True
                        self.situation_type = "low_damage"
                        self.display.print_message(
                            f"⚠️ Низкий урон! 3 атаки подряд: {self.last_attack_damages}. "
                            f"Средний урон: {average_damage:.1f}. Запуск процедуры восстановления...", 
                            "warning"
                        )
                        # Reset pattern
                        self.last_attack_damages = []
    
    def _check_low_potions(self) -> bool:
        """Check if potions are running low (10 or less)"""
        # Don't check if player data is not initialized yet
        if not hasattr(self.player, 'inventory') or not self.player.inventory:
            return False
            
        hp_potions = self.player.get_heal_potions_count()
        mp_potions = self.player.get_mana_potions_count()
        
        if hp_potions <= 10 or mp_potions <= 10:
            if not self.low_damage_handled:
                self.low_damage_handled = True
                self.situation_type = "low_potions"
                self.display.print_message(
                    f"⚠️ Мало зелий! HP: {hp_potions}, MP: {mp_potions}. "
                    f"Запуск процедуры восстановления...", 
                    "warning"
                )
                return True
        return False
    
    def _reset_low_damage_tracking(self):
        """Reset low damage tracking when combat ends or pattern breaks"""
        self.low_damage_count = 0
        self.last_attack_damages = []
        self.combat_paused = False
        self.low_damage_handled = False
        self.situation_type = "low_damage"
    
    def _handle_victory(self, result: Dict[str, Any], mob_group: MobGroup) -> Literal['victory']:
        """Handle combat victory"""
        # Reset low damage tracking
        self._reset_low_damage_tracking()
        
        # Extract mob information from arrLogs
        arr_logs = result.get('arrLogs', [])
        killed_mobs = {}
        
        for log_entry in arr_logs:
            def_name = log_entry.get('defname', '')
            if def_name and log_entry.get('winAll', False):
                # This mob was killed
                if def_name in killed_mobs:
                    killed_mobs[def_name] += 1
                else:
                    killed_mobs[def_name] = 1
        
        # Update killed mobs statistics
        total_killed = 0
        for mob_name, count in killed_mobs.items():
            self.display.update_killed_mobs(mob_name, count)
            total_killed += count
        
        # Process drops
        drop_data = result.get('dataWin', {}).get('drop', [])
        if drop_data:
            self.display.update_drops(drop_data)
        
        # Calculate rewards
        exp_gained = result.get('dataWin', {}).get('expWin', 0)
        gold_gained = sum(item.get('count', 0) for item in drop_data if item.get('id') == 'm_0_1')
        
        # Update statistics - добавляем каждого убитого моба отдельно
        for mob_name, count in killed_mobs.items():
            for _ in range(count):  # Добавляем каждого моба отдельно
                self.display.update_stats(mobs_killed=1)
        
        # Добавляем опыт и золото
        self.display.update_stats(
            total_exp=exp_gained,
            session_gold=gold_gained
        )
        
        self.display.print_message(
            f"🎉 Все враги побеждены! Убито мобов: {total_killed}, "
            f"[yellow]+{exp_gained}[/yellow] опыта, [yellow]+{gold_gained}[/yellow] золота", 
            "success"
        )
        
        return 'victory'
    
    def _log_api_response(self, response: Dict[str, Any], context: str = ""):
        """Log API response to file"""
        with open("logs/api_responses.log", "a", encoding="utf-8") as f:
            f.write(f"\n--- {context} ---\n")
            f.write(json.dumps(response, ensure_ascii=False, indent=2))
            f.write("\n")
    
    def _update_display_after_action(self, current_target: Mob, mob_group: MobGroup, current_time: float):
        """Update display after any combat action"""
        # Get player data
        player_data = self.player.get_stats_summary()
        
        # Get mob data
        mob_data = None
        mob_group_data = None
        if current_target:
            mob_data = {
                'name': current_target.name,
                'hp': current_target.hp,
                'max_hp': current_target.max_hp,
                'level': current_target.level
            }
        
        if mob_group:
            # Get all mobs for display
            all_mobs = mob_group.get_all_mobs()
            if len(all_mobs) > 1:
                mob_group_data = mob_group.get_all_mobs_with_status()
        
        # Calculate cooldowns
        attack_cooldown = max(0, self.player.GLOBAL_COOLDOWN - (current_time - self.player.last_attack_time))
        skill_cooldown = max(0, self.player.SKILL_COOLDOWN - (current_time - self.player.last_skill_time))
        heal_cooldown = max(0, self.player.HEAL_COOLDOWN - (current_time - self.player.last_heal_time))
        mana_cooldown = max(0, self.player.MANA_COOLDOWN - (current_time - self.player.last_mana_time))
        
        # Update display
        self.display.update_display(
            current_state="combat",
            player_data=player_data,
            mob_data=mob_data,
            mob_group_data=mob_group_data,
            attack_cooldown=attack_cooldown,
            heal_cooldown=heal_cooldown,
            skill_cooldown=skill_cooldown,
            mana_cooldown=mana_cooldown,
            rest_time=None,
            player_name="Piulok",
            last_attack_time=self.player.last_attack_time,
            last_skill_time=self.player.last_skill_time
        )
        
        # Update statistics
        self.display.update_stats(
            current_gold=self.player.get_gold_count(),
            current_skulls=self.player.get_skulls_count()
        )
    
    def _display_basic_combat_results(self, action_type: str, damage_dealt: int, damage_received: int):
        """Display basic combat results when no mob data is available"""
        action_icon = "⚡" if action_type == "skill" else "⚔️"
        action_name = "[yellow]Усиленный удар[/yellow]" if action_type == "skill" else "[cyan]Атака[/cyan]"
        
        # Update damage statistics only for regular attacks
        if action_type == "attack":
            self.display.update_damage_stats(damage_dealt)
        
        # Формируем сообщение с уроном в одной строке
        if damage_dealt > 0:
            if damage_received > 0:
                message = f"{action_icon} {action_name}: нанес [bold red]{damage_dealt}[/bold red] урона, получил [bold red]{damage_received}[/bold red] урона"
            else:
                message = f"{action_icon} {action_name}: нанес [bold red]{damage_dealt}[/bold red] урона"
        else:
            if damage_received > 0:
                message = f"{action_icon} {action_name}: промах! Получил [bold red]{damage_received}[/bold red] урона"
            else:
                message = f"{action_icon} {action_name}: промах!"
        
        # Определяем уровень сообщения
        level = "success" if damage_dealt > 0 else "warning"
        self.display.print_message(message, level)
    
    def update_mob_database(self, mob_data: dict, db_path: str = "mob_database.json"):
        """Сохраняет или обновляет информацию о мобе в базе мобов"""
        if os.path.exists(db_path):
            with open(db_path, "r", encoding="utf-8") as f:
                db = json.load(f)
        else:
            db = {"mobs": []}
        # Защита от повреждённой структуры
        if not isinstance(db.get("mobs"), list):
            db["mobs"] = []
        farm_id = mob_data.get("farmId") or mob_data.get("id")
        found = False
        for mob in db["mobs"]:
            if mob.get("farmId") == farm_id:
                mob.update(mob_data)
                found = True
                break
        if not found:
            db["mobs"].append(mob_data)
        with open(db_path, "w", encoding="utf-8") as f:
            json.dump(db, f, ensure_ascii=False, indent=2) 