"""
Main entry point for Ruby King Bot
"""

import logging
import time
import sys
import os
from rich.console import Console
from rich.live import Live
from rich.layout import Layout
from datetime import datetime, timedelta
import json
from collections import Counter

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ruby_king_bot.api.client import APIClient
from ruby_king_bot.core.game_state import GameState, GameStateManager
from ruby_king_bot.core.player import Player
from ruby_king_bot.core.mob import Mob, MobGroup
from ruby_king_bot.ui.display import GameDisplay

console = Console()

def setup_logging():
    """Setup logging configuration"""
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/bot.log'),
            # Убираем StreamHandler чтобы логи не появлялись в консоли
            # logging.StreamHandler()
        ]
    )

def extract_mob_data(response_data):
    """
    Extract mob data from API response
    
    Args:
        response_data: API response data
        
    Returns:
        List of mob data dictionaries or None
    """
    mobs_found = []
    
    # Try different possible locations for mob data
    if isinstance(response_data, dict):
        # Direct mob data
        if 'mob' in response_data:
            mob_list = response_data['mob']
            if isinstance(mob_list, list) and len(mob_list) > 0:
                print(f"DEBUG: Found {len(mob_list)} mobs in direct mob field")
                mobs_found.extend(mob_list)
            elif isinstance(mob_list, dict):
                mobs_found.append(mob_list)
        
        # Check if response contains farm data
        if 'farm' in response_data and isinstance(response_data['farm'], list):
            for farm_item in response_data['farm']:
                if isinstance(farm_item, dict) and 'mob' in farm_item:
                    mob_data = farm_item['mob']
                    if isinstance(mob_data, list) and len(mob_data) > 0:
                        print(f"DEBUG: Found {len(mob_data)} mobs in farm data")
                        mobs_found.extend(mob_data)
                    elif isinstance(mob_data, dict):
                        mobs_found.append(mob_data)
    
    if mobs_found:
        print(f"DEBUG: Total mobs found: {len(mobs_found)}")
        return mobs_found
    
    return None

def extract_player_data(response_data):
    """
    Extract player data from API response
    
    Args:
        response_data: API response data
        
    Returns:
        Player data dictionary or None
    """
    # Try different possible locations for player data
    if isinstance(response_data, dict):
        # Direct player data
        if 'player' in response_data:
            return response_data['player']
        
        # Check if response contains user data
        if 'user' in response_data:
            return response_data['user']
    
    return None

def format_mmss(seconds: int) -> str:
    m, s = divmod(seconds, 60)
    return f"{m:02}:{s:02}"

def show_rest_timer(time_end: int):
    """Показывает таймер отдыха в формате mm:ss до time_end (timestamp ms)"""
    now = int(time.time() * 1000)  # Текущее время в миллисекундах
    seconds_left = max(0, (time_end - now) // 1000)  # Оставшиеся секунды
    
    print(f"DEBUG: time_end={time_end}, now={now}, seconds_left={seconds_left}")
    
    with Progress(
        TextColumn("[bold blue]Осталось отдыха:[/bold blue]"),
        BarColumn(),
        TextColumn("{task.fields[mmss]}")
    ) as progress:
        task = progress.add_task("rest", total=seconds_left, mmss=format_mmss(seconds_left))
        while seconds_left > 0:
            progress.update(task, completed=progress.tasks[0].total - seconds_left, mmss=format_mmss(seconds_left))
            time.sleep(1)
            seconds_left -= 1
        progress.update(task, completed=progress.tasks[0].total, mmss="00:00")

def show_hp_bars(player_hp, player_max_hp, mob_hp, mob_max_hp, player_name, mob_name):
    """Показывает полоски HP игрока и моба в консоли"""
    with Progress(
        TextColumn(f"[bold green]{player_name} HP:[/bold green]"),
        BarColumn(),
        TextColumn("{task.fields[hp]}/{task.fields[max_hp]}")
    ) as player_progress, Progress(
        TextColumn(f"[bold red]{mob_name} HP:[/bold red]"),
        BarColumn(),
        TextColumn("{task.fields[hp]}/{task.fields[max_hp]}")
    ) as mob_progress:
        player_task = player_progress.add_task("player_hp", total=player_max_hp, hp=player_hp, max_hp=player_max_hp)
        mob_task = mob_progress.add_task("mob_hp", total=mob_max_hp, hp=mob_hp, max_hp=mob_max_hp)
        player_progress.update(player_task, completed=player_hp, hp=player_hp, max_hp=player_max_hp)
        mob_progress.update(mob_task, completed=mob_hp, hp=mob_hp, max_hp=mob_max_hp)
        time.sleep(1)  # Показываем 1 секунду, потом обновим

def log_api_response(response: dict, context: str = ""):
    """Сохраняет структуру ответа API в отдельный лог-файл для анализа"""
    with open("logs/api_responses.log", "a", encoding="utf-8") as f:
        f.write(f"\n--- {context} ---\n")
        f.write(json.dumps(response, ensure_ascii=False, indent=2))
        f.write("\n")

def main():
    """Main bot loop with beautiful UI"""
    console = Console()
    console.print("[bold blue]Starting Ruby King Bot...[/bold blue]")

    # Вызываем setup_logging ПЕРВЫМ, чтобы убедиться, что папка logs существует
    setup_logging()
    logger = logging.getLogger(__name__)  # Инициализируем logger ПОСЛЕ setup_logging
    
    # Initialize components
    api_client = APIClient()
    state_manager = GameStateManager()
    player = Player()
    display = GameDisplay()
    
    # Initialize game state
    current_state = GameState.CITY
    explore_done = False
    current_mob_group = None
    rest_end_time = None
    
    # Variables for accumulating rewards in multi-mob battles
    accumulated_exp = 0
    accumulated_gold = 0
    accumulated_drops = []
    
    console.print("[green]Bot initialized successfully[/green]")
    console.print("[yellow]Continuous mode: Bot will explore territory after each victory[/yellow]")
    
    # Main game loop with live display
    with Live(display.layout, refresh_per_second=4, screen=True) as live:
        while True:
            current_time = time.time()
            current_state = state_manager.get_current_state()
            
            # Update display with current state
            player_data = {
                'hp': player.hp,
                'max_hp': player.max_hp,
                'mp': player.mp,
                'max_mp': player.max_mp,
                'stamina': player.stamina,
                'max_stamina': player.max_stamina,
                'level': player.level,
                'xp': player.xp,
                'xp_next': player.stats.experience_to_next,
                'gold': player.get_gold_count(),
                'heal_potions': player.get_heal_potions_count(),
                'mana_potions': player.get_mana_potions_count(),
                'skulls': player.get_skulls_count(),
                'morale': player.morale
            }
            
            mob_data = None
            mob_group_data = None
            if current_mob_group:
                current_target = current_mob_group.get_current_target()
                if current_target:
                    mob_data = {
                        'name': current_target.name,
                        'hp': current_target.hp,
                        'max_hp': current_target.max_hp,
                        'level': current_target.level
                    }
                
                # Get all mobs for display
                all_mobs = current_mob_group.get_all_mobs()
                if len(all_mobs) > 1:
                    mob_group_data = current_mob_group.get_all_mobs_with_status()
            
            # Calculate cooldowns
            attack_cooldown = max(0, player.attack_cooldown_end - current_time)
            heal_cooldown = max(0, player.heal_cooldown_end - current_time)
            
            # Update display
            display.update_display(
                current_state=current_state.value,
                player_data=player_data,
                mob_data=mob_data,
                mob_group_data=mob_group_data,
                attack_cooldown=attack_cooldown,
                heal_cooldown=heal_cooldown,
                rest_time=rest_end_time,
                player_name="Piulok"  # TODO: Get from API
            )
            
            # Обновляем статистику золота и черепов
            display.update_stats(
                current_gold=player.get_gold_count(),
                current_skulls=player.get_skulls_count()
            )
            
            # Game logic
            if current_state == GameState.CITY:
                if not explore_done:
                    try:
                        result = api_client.explore_territory()
                        log_api_response(result, context="explore_territory")
                        
                        if isinstance(result, dict) and result.get('status') == 'fail':
                            if 'иссяк боевой дух' in result.get('message', ''):
                                display.print_message("😴 Morale depleted, starting rest...", "warning")
                                rest_result = api_client.start_rest()
                                log_api_response(rest_result, context="start_rest")
                                state_manager.change_state(GameState.RESTING, "Starting rest due to low morale")
                                rest_end_time = time.time() + (20 * 60)  # 20 minutes
                                continue
                            elif 'Очень быстро совершаете действия' in result.get('message', ''):
                                display.print_message("⏱️ Actions too fast, waiting 5 seconds...", "warning")
                                time.sleep(5)  # Ждём 5 секунд
                                continue  # Повторяем попытку
                            elif 'Неверное местонахождения' in result.get('message', ''):
                                display.print_message("📍 Location error, waiting 10 seconds...", "warning")
                                time.sleep(10)  # Ждём 10 секунд
                                continue  # Повторяем попытку
                            else:
                                display.print_message(f"Exploration failed: {result.get('message', 'Unknown error')}", "error")
                                break
                        
                        # Check if mob was found
                        mob_data = extract_mob_data(result)
                        if isinstance(mob_data, list):
                            current_mob_group = MobGroup(mob_data)
                            state_manager.change_state(GameState.COMBAT, f"Found {len(mob_data)} mobs")
                            mob_names = [mob['name'] for mob in mob_data]
                            display.print_message(f"🎯 Найдено: {', '.join(mob_names)}", "success")
                            
                            # Update player data from response
                            player_data = extract_player_data(result)
                            if player_data:
                                player.update_from_api_response({'player': player_data})
                        elif mob_data is not None:
                            display.print_message(f"extract_mob_data вернул не список: {type(mob_data)}: {mob_data}", "error")
                            break
                        else:
                            # Нет моба и нет текущего моба - это событие или пустая область
                            display.print_message("🎪 Event found, skipping...", "info")
                            
                            # Логируем событие в отдельный файл
                            with open("logs/events.log", "a", encoding="utf-8") as f:
                                f.write(f"\n--- СОБЫТИЕ НАЙДЕНО {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n")
                                f.write(json.dumps(result, ensure_ascii=False, indent=2))
                                f.write("\n")
                            
                            # Увеличиваем счетчик событий и продолжаем работу
                            display.update_stats(events_found=display.stats['events_found'] + 1)
                        
                        # Устанавливаем explore_done = True только если нашли моба
                        if isinstance(mob_data, list):
                            explore_done = True
                        
                    except Exception as e:
                        display.print_message(f"Network error: {e}. Waiting 60 seconds before retry...", "error")
                        time.sleep(60)
                        continue
                else:
                    # Exploration done, wait for combat to finish
                    time.sleep(1)
                    continue
            
            elif current_state == GameState.COMBAT:
                if not current_mob_group:
                    display.print_message("No mob group in combat state", "error")
                    break
                
                current_target = current_mob_group.get_current_target()
                if not current_target:
                    display.print_message("No current target in mob group", "error")
                    break
                
                # Использовать хилку, если (max_hp - hp) >= 100 и есть хилки
                if (player.max_hp - player.hp) >= 100 and player.get_heal_potions_count() > 0 and player.can_heal(current_time):
                    try:
                        heal_result = api_client.use_healing_potion()
                        log_api_response(heal_result, context="use_healing_potion")
                        player.record_heal(current_time)
                        remaining_heals = player.get_heal_potions_count()
                        display.print_message(f"🔴 Использовал хилку! HP: {player.hp}/{player.max_hp} (осталось {remaining_heals} банок)", "success")
                    except Exception as e:
                        display.print_message(f"Network error: {e}. Waiting 60 seconds before retry...", "error")
                        time.sleep(60)
                        continue
                
                # Использовать банку маны, если (max_mp - mp) >= 60 и есть банки маны
                if (player.max_mp - player.mp) >= 60 and player.get_mana_potions_count() > 0:
                    try:
                        mana_result = api_client.use_mana_potion()
                        log_api_response(mana_result, context="use_mana_potion")
                        remaining_mana = player.get_mana_potions_count()
                        display.print_message(f"🔵 Использовал банку маны! MP: {player.mp}/{player.max_mp} (осталось {remaining_mana} банок)", "success")
                    except Exception as e:
                        display.print_message(f"Network error: {e}. Waiting 60 seconds before retry...", "error")
                        time.sleep(60)
                        continue
                
                # Attack mob
                if player.can_attack(current_time):
                    try:
                        result = api_client.attack_mob(current_target.farm_id)
                        log_api_response(result, context="attack_mob")
                        player.record_attack(current_time)
                        
                        if isinstance(result, dict):
                            if result.get('status') == 'fail':
                                if 'Монстр не найден' in result.get('message', ''):
                                    display.print_message("Моб не найден для атаки, возможно бой уже закончился", "info")
                                else:
                                    display.print_message(f"Attack failed: {result.get('message', 'Unknown error')}", "error")
                            elif result.get('status') == 'success':
                                # Update player data from response
                                player.update_from_api_response(result)
                                
                                # Check for victory status
                                if result.get('statusBattle') == 'win':
                                    # Extract victory data
                                    arr_logs = result.get('arrLogs', [])
                                    killed_names = []
                                    for log_entry in arr_logs:
                                        messages = log_entry.get('messages', [])
                                        for message in messages:
                                            if 'погиб' in message or 'погибла' in message:
                                                killed_names.append(log_entry.get('defname', 'Unknown'))
                                    for mob_name in killed_names:
                                        display.update_killed_mobs(mob_name)
                                    drop_data = result.get('dataWin', {}).get('drop', [])
                                    if drop_data:
                                        display.update_drops(drop_data)
                                    display.update_stats(
                                        mobs_killed=display.stats['mobs_killed'] + len(killed_names),
                                        total_exp=display.stats['total_exp'] + result.get('dataWin', {}).get('expWin', 0),
                                        session_gold=display.stats['session_gold'] + sum(item.get('count', 0) for item in drop_data if item.get('id') == 'm_0_1')
                                    )
                                    exp_gained = result.get('dataWin', {}).get('expWin', 0)
                                    gold_gained = sum(item.get('count', 0) for item in drop_data if item.get('id') == 'm_0_1')
                                    display.print_message(f"🎉 Все враги побеждены! +{exp_gained} опыта, +{gold_gained} золота", "success")
                                    state_manager.change_state(GameState.CITY, "Combat ended - all mobs defeated")
                                    current_mob_group = None
                                    explore_done = False  # Reset exploration flag
                                    time.sleep(2)  # Задержка перед новым исследованием
                                    continue
                                
                                # Update mob data from response
                                current_mob_group.update_from_combat_response(result)
                                
                                # Extract combat log from response and show combined message
                                arr_logs = result.get('arrLogs', [])
                                mob_killed = False
                                
                                if arr_logs:
                                    player_damage = 0
                                    mob_damage = 0
                                    for log_entry in arr_logs:
                                        if not log_entry.get('isMob', False):  # Player attack
                                            player_damage = log_entry.get('damage', 0)
                                        else:  # Mob attack
                                            mob_damage = log_entry.get('damage', 0)
                                        
                                        # Check if mob was killed in this log entry
                                        messages = log_entry.get('messages', [])
                                        for message in messages:
                                            if 'погиб' in message or 'погибла' in message:
                                                mob_killed = True
                                                break
                                    
                                    # Show combined combat result
                                    if player_damage > 0 and mob_damage > 0:
                                        display.print_message(f"⚔️ {current_target.name}: игрок {player_damage} урона, получил {mob_damage} урона", "info")
                                    elif player_damage > 0:
                                        display.print_message(f"⚔️ {current_target.name}: игрок {player_damage} урона", "info")
                                    elif mob_damage > 0:
                                        display.print_message(f"⚔️ {current_target.name}: получил {mob_damage} урона", "info")
                                
                                # Check if current target died (HP = 0 or killed in logs)
                                if current_target.hp <= 0 or mob_killed:
                                    # Extract drop data from response
                                    drop_data = result.get('drop', [])
                                    exp_gained = result.get('expWin', 0)
                                    
                                    # If no expWin in main response, try to get from arrLogs
                                    if exp_gained == 0 and arr_logs:
                                        for log_entry in arr_logs:
                                            if not log_entry.get('isMob', False):  # Player attack
                                                # Try to extract exp from log entry
                                                exp_gained = log_entry.get('exp', 0)
                                                if exp_gained > 0:
                                                    break
                                    
                                    # Calculate gold from drops
                                    gold_gained = 0
                                    if drop_data:
                                        for item in drop_data:
                                            item_id = item.get('id', '')
                                            item_count = item.get('count', 1)
                                            # Gold has ID 'm_0_1'
                                            if item_id == 'm_0_1':
                                                gold_gained += item_count
                                    
                                    # Update killed mobs tracking
                                    arr_logs = result.get('arrLogs', [])
                                    killed_names = []
                                    for log_entry in arr_logs:
                                        messages = log_entry.get('messages', [])
                                        for message in messages:
                                            if 'погиб' in message or 'погибла' in message:
                                                killed_names.append(log_entry.get('defname', 'Unknown'))
                                    for mob_name in killed_names:
                                        display.update_killed_mobs(mob_name)
                                    display.update_stats(
                                        mobs_killed=display.stats['mobs_killed'] + len(killed_names),
                                        total_exp=display.stats['total_exp'] + exp_gained,
                                        session_gold=display.stats['session_gold'] + gold_gained
                                    )
                                    
                                    # Check if there are more mobs to fight
                                    if current_mob_group.has_more_targets():
                                        # Intermediate mob kill - don't show rewards yet
                                        display.print_message(f"💀 {current_target.name} defeated!", "success")
                                        next_target = current_mob_group.switch_to_next_target()
                                        if next_target:
                                            display.print_message(f"🎯 Switching to next target: {next_target.name}", "info")
                                            continue
                                    else:
                                        # All mobs defeated - show accumulated rewards
                                        display.print_message(f"🎉 Все враги побеждены! +{exp_gained} опыта, +{gold_gained} золота", "success")
                                        
                                        # Update drops tracking with accumulated drops
                                        if accumulated_drops:
                                            display.update_drops(accumulated_drops)
                                        
                                        # Update statistics with accumulated rewards
                                        display.update_stats(
                                            total_exp=exp_gained,
                                            session_gold=gold_gained
                                        )
                                        
                                        display.print_message(f"🎉 Все враги побеждены! +{exp_gained} опыта, +{gold_gained} золота", "success")
                                        state_manager.change_state(GameState.CITY, "Combat ended - all mobs defeated")
                                        current_mob_group = None
                                        explore_done = False  # Reset exploration flag
                                        time.sleep(2)  # Задержка перед новым исследованием
                                        continue
                        
                    except Exception as e:
                        display.print_message(f"Network error: {e}. Waiting 60 seconds before retry...", "error")
                        time.sleep(60)
                        continue
                else:
                    # Wait for attack cooldown
                    time.sleep(0.5)
                    continue
            
            elif current_state == GameState.RESTING:
                if rest_end_time and current_time >= rest_end_time:
                    display.print_rest_complete()
                    state_manager.change_state(GameState.CITY, "Rest completed")
                    rest_end_time = None
                    explore_done = False  # Reset exploration flag
                else:
                    # Still resting
                    time.sleep(1)
                    continue
            
            else:
                display.print_message(f"Unknown state: {current_state}", "error")
                break
            
            # Small delay to prevent excessive CPU usage
            time.sleep(0.1)
    
    display.print_message("Bot stopped", "info")

if __name__ == "__main__":
    main() 