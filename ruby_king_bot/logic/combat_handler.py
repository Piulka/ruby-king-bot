"""
Combat Handler - Manages combat actions, skills, and potion usage
"""

import time
import logging
import re
from typing import Optional, Dict, Any, Literal
from ruby_king_bot.core.mob import Mob, MobGroup
from ruby_king_bot.core.player import Player
from ruby_king_bot.api.client import APIClient
from ruby_king_bot.ui.display import GameDisplay
from ruby_king_bot.config.settings import Settings
from ruby_king_bot.logic.data_extractor import DataExtractor

logger = logging.getLogger(__name__)

class CombatHandler:
    """Handles all combat-related actions and logic"""
    
    def __init__(self, api_client: APIClient, player: Player, display: GameDisplay):
        self.api_client = api_client
        self.player = player
        self.display = display
        self.data_extractor = DataExtractor()
        
        # Combat state
        self.skill_used = False  # Flag to track if skill was used in current round
    
    def handle_combat_round(self, current_target: Mob, current_time: float, mob_group: MobGroup) -> Literal['victory', 'continue', 'failure']:
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
        """
        self.skill_used = False  # Reset flag at start of round
        
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
        
        # 5. Wait for cooldowns
        time.sleep(0.1)
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
            time.sleep(0.1)  # Delay between requests
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
            time.sleep(0.1)  # Delay between requests
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
            self.display.print_message(f"⚡ Используем скилл против {current_target.name}...", "success")
            
            # Update player data from response
            self.player.update_from_api_response(skill_result)
            
            if isinstance(skill_result, dict):
                if skill_result.get('status') == 'fail':
                    return self._handle_combat_failure(skill_result, "skill")
                elif skill_result.get('status') == 'success':
                    return self._handle_combat_success(skill_result, current_target, mob_group, "skill")
            
            time.sleep(0.1)  # Delay between requests
            return 'continue'
            
        except Exception as e:
            self.display.print_message(f"Network error: {e}. Waiting 60 seconds before retry...", "error")
            time.sleep(60)
            return 'failure'
    
    def _use_attack(self, current_target: Mob, current_time: float, mob_group: MobGroup) -> Literal['victory', 'continue', 'failure']:
        """Use regular attack"""
        self.display.print_message(f"⚔️ Атакуем {current_target.name}...", "info")
        
        try:
            attack_result = self.api_client.attack_mob(current_target.farm_id)
            self._log_api_response(attack_result, "attack_mob")
            self.player.record_attack(current_time)
            
            if isinstance(attack_result, dict):
                if attack_result.get('status') == 'fail':
                    return self._handle_combat_failure(attack_result, "attack")
                elif attack_result.get('status') == 'success':
                    return self._handle_combat_success(attack_result, current_target, mob_group, "attack")
            
            time.sleep(0.1)  # Delay between requests
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
        # Update mob HP from response
        if "mob" in result:
            mob_data = result["mob"]
            if current_target and current_target.farm_id == mob_data.get("farmId"):
                old_hp = current_target.hp
                current_target.hp = mob_data.get("hp", current_target.hp)
                current_target.max_hp = mob_data.get("maxHp", current_target.max_hp)
                damage_dealt = old_hp - current_target.hp
                
                # Get damage received from arrLogs
                damage_received = self._extract_damage_received(result)
                
                # Display combat results
                self._display_combat_results(action_type, damage_dealt, damage_received, current_target)
        
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
        
        return 'continue'
    
    def _extract_damage_received(self, result: Dict[str, Any]) -> int:
        """Extract damage received from combat logs"""
        damage_received = 0
        arr_logs = result.get('arrLogs', [])
        for log_entry in arr_logs:
            messages = log_entry.get('messages', [])
            for message in messages:
                if 'наносит' in message and 'урон' in message:
                    damage_match = re.search(r'наносит (\d+) урон', message)
                    if damage_match:
                        damage_received = int(damage_match.group(1))
                        break
        return damage_received
    
    def _display_combat_results(self, action_type: str, damage_dealt: int, damage_received: int, current_target: Mob):
        """Display combat results"""
        action_icon = "⚡" if action_type == "skill" else "⚔️"
        action_name = "Скилл" if action_type == "skill" else "Атака"
        
        if damage_dealt > 0:
            if damage_received > 0:
                self.display.print_message(
                    f"{action_icon} {action_name}: нанес {damage_dealt} урона, получил {damage_received} урона. "
                    f"{current_target.name} HP: {current_target.hp}/{current_target.max_hp}", 
                    "success"
                )
            else:
                self.display.print_message(
                    f"{action_icon} {action_name} нанесла {damage_dealt} урона {current_target.name}! "
                    f"HP: {current_target.hp}/{current_target.max_hp}", 
                    "success"
                )
        else:
            if damage_received > 0:
                self.display.print_message(
                    f"{action_icon} {action_name} по {current_target.name} - промах! "
                    f"Получил {damage_received} урона. HP: {current_target.hp}/{current_target.max_hp}", 
                    "warning"
                )
            else:
                self.display.print_message(
                    f"{action_icon} {action_name} по {current_target.name} - промах! "
                    f"HP: {current_target.hp}/{current_target.max_hp}", 
                    "warning"
                )
    
    def _handle_victory(self, result: Dict[str, Any], mob_group: MobGroup) -> Literal['victory']:
        """Handle combat victory"""
        # Count dead mobs
        dead_mobs_count = 0
        for mob in mob_group.get_all_mobs():
            if mob.hp <= 0:
                dead_mobs_count += 1
                self.display.update_killed_mobs(mob.name)
        
        # Process drops
        drop_data = result.get('dataWin', {}).get('drop', [])
        if drop_data:
            self.display.update_drops(drop_data)
        
        # Calculate rewards
        exp_gained = result.get('dataWin', {}).get('expWin', 0)
        gold_gained = sum(item.get('count', 0) for item in drop_data if item.get('id') == 'm_0_1')
        
        # Update statistics
        self.display.update_stats(
            mobs_killed=dead_mobs_count,
            total_exp=exp_gained,
            session_gold=gold_gained
        )
        
        self.display.print_message(
            f"🎉 Все враги побеждены! Убито мобов: {dead_mobs_count}, "
            f"+{exp_gained} опыта, +{gold_gained} золота", 
            "success"
        )
        
        return 'victory'
    
    def _log_api_response(self, response: Dict[str, Any], context: str = ""):
        """Log API response to file"""
        import json
        with open("logs/api_responses.log", "a", encoding="utf-8") as f:
            f.write(f"\n--- {context} ---\n")
            f.write(json.dumps(response, ensure_ascii=False, indent=2))
            f.write("\n") 