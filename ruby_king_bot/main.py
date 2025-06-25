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
from ruby_king_bot.config.settings import Settings

console = Console()

def setup_logging():
    """Setup logging configuration"""
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    logging.basicConfig(
        level=logging.DEBUG,
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
    logger = logging.getLogger(__name__)
    
    logger.debug(f"🔍 DEBUG: extract_mob_data called with response keys: {list(response_data.keys()) if isinstance(response_data, dict) else 'Not a dict'}")
    
    mobs_found = []
    
    # Try different possible locations for mob data
    if isinstance(response_data, dict):
        # Direct mob data
        if 'mob' in response_data:
            mob_list = response_data['mob']
            logger.debug(f"🔍 DEBUG: Found 'mob' field: {type(mob_list)}")
            if isinstance(mob_list, list) and len(mob_list) > 0:
                logger.debug(f"🔍 DEBUG: mob_list is list with {len(mob_list)} items")
                mobs_found.extend(mob_list)
            elif isinstance(mob_list, dict):
                logger.debug("🔍 DEBUG: mob_list is dict")
                mobs_found.append(mob_list)
        
        # Check if response contains farm data
        if 'farm' in response_data and isinstance(response_data['farm'], list):
            logger.debug("🔍 DEBUG: Found 'farm' field")
            for farm_item in response_data['farm']:
                if isinstance(farm_item, dict) and 'mob' in farm_item:
                    mob_data = farm_item['mob']
                    if isinstance(mob_data, list) and len(mob_data) > 0:
                        mobs_found.extend(mob_data)
                    elif isinstance(mob_data, dict):
                        mobs_found.append(mob_data)
    
    logger.debug(f"🔍 DEBUG: extract_mob_data returning {len(mobs_found)} mobs: {mobs_found}")
    
    if mobs_found:
        return mobs_found
    
    return None

def extract_mob_group_data(response_data):
    """
    Extract mob group data from API response for display
    
    Args:
        response_data: API response data
        
    Returns:
        List of mob data dictionaries formatted for display or None
    """
    logger = logging.getLogger(__name__)
    
    mobs_found = extract_mob_data(response_data)
    
    if not mobs_found:
        return None
    
    # Format mobs for display
    formatted_mobs = []
    for i, mob in enumerate(mobs_found):
        if isinstance(mob, dict):
            formatted_mob = {
                'name': mob.get('name', 'Неизвестно'),
                'hp': f"{mob.get('hp', 0)}/{mob.get('maxHp', 1)}",
                'level': mob.get('level', 1),
                'is_current_target': i == 0,  # First mob is current target
                'is_dead': mob.get('hp', 1) <= 0
            }
            formatted_mobs.append(formatted_mob)
    
    logger.debug(f"🔍 DEBUG: extract_mob_group_data returning {len(formatted_mobs)} formatted mobs")
    return formatted_mobs

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
    
    # Total mobs killed counter
    total_mobs_killed = 0
    
    console.print("[green]Bot initialized successfully[/green]")
    console.print("[yellow]Continuous mode: Bot will explore territory after each victory[/yellow]")
    
    # Initialize player data from API
    # try:
    #     console.print("[blue]Initializing player data...[/blue]")
    #     player_info = api_client.get_user_info()
    #     if player_info and 'player' in player_info:
    #         player.update_from_api_response(player_info)
    #         console.print("[green]Player data initialized successfully[/green]")
    #     else:
    #         console.print("[yellow]Could not get player data, using defaults[/yellow]")
    # except Exception as e:
    #     console.print(f"[yellow]Failed to get player data: {e}, using defaults[/yellow]")
    
    # Main game loop with live display
    with Live(display.layout, refresh_per_second=4, screen=True) as live:
        while True:
            current_time = time.time()
            skill_used = False  # Сброс флага в начале каждой итерации
            current_state = state_manager.get_current_state()
            
            # Update display with current state
            player_data = player.get_stats_summary()
            
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
            attack_cooldown = max(0, player.GLOBAL_COOLDOWN - (current_time - player.last_attack_time))
            skill_cooldown = max(0, player.SKILL_COOLDOWN - (current_time - player.last_skill_time))
            heal_cooldown = max(0, player.HEAL_COOLDOWN - (current_time - player.last_heal_time))
            mana_cooldown = max(0, player.MANA_COOLDOWN - (current_time - player.last_mana_time))
            
            # Calculate rest time if resting
            rest_time = None
            if current_state == GameState.RESTING and rest_end_time:
                rest_time = rest_end_time
            
            # Update display
            display.update_display(
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
                last_attack_time=player.last_attack_time,
                last_skill_time=player.last_skill_time
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
                        
                        # Extract mob data from response
                        mob_data = extract_mob_data(result)
                        mob_group_data = extract_mob_group_data(result)
                        
                        if mob_data and mob_group_data:
                            # Создаем MobGroup из сырых данных mob_data
                            current_mob_group = MobGroup(mob_data)
                            current_target = current_mob_group.get_current_target()
                            
                            # Обновляем данные для дисплея из созданной группы
                            if current_target:
                                mob_data = {
                                    'name': current_target.name,
                                    'hp': current_target.hp,
                                    'max_hp': current_target.max_hp,
                                    'level': current_target.level
                                }
                                mob_group_data = current_mob_group.get_all_mobs_with_status()
                            
                            # Сообщение о найденных мобах
                            mob_names = [mob['name'] for mob in mob_group_data]
                            display.print_message(f"🔍 Найдены враги: {', '.join(mob_names)}", "info")
                            
                            state_manager.change_state(GameState.COMBAT, "Mobs found")
                            explore_done = True
                        else:
                            display.print_message("🔍 Исследуем территорию...", "info")
                        
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
                
                # 1. Исследование (уже выполнено, переходим к обновлению дисплея)
                
                # 2. Проверка и использование зелий
                if (player.hp / player.max_hp * 100) < Settings.HEAL_THRESHOLD and player.can_use_heal_potion(current_time):
                    try:
                        heal_result = api_client.use_healing_potion()
                        log_api_response(heal_result, context="use_healing_potion")
                        player.record_heal(current_time)
                        
                        # Обновить данные игрока из ответа
                        if "user" in heal_result:
                            player.update_from_api_response(heal_result)
                        
                        # Обновление дисплея
                        display.update_display(
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
                            last_attack_time=player.last_attack_time,
                            last_skill_time=player.last_skill_time
                        )
                        
                        time.sleep(0.1)  # Задержка между запросами
                        
                    except Exception as e:
                        display.print_message(f"Network error: {e}. Waiting 60 seconds before retry...", "error")
                        time.sleep(60)
                        continue
                
                if (player.mp / player.max_mp * 100) < Settings.MANA_THRESHOLD and player.can_use_mana_potion(current_time):
                    try:
                        mana_result = api_client.use_mana_potion()
                        log_api_response(mana_result, context="use_mana_potion")
                        player.record_mana(current_time)
                        display.print_message("🔵 Использовал зелье маны!", "success")
                        
                        # Обновить данные игрока из ответа
                        if "user" in mana_result:
                            player.update_from_api_response(mana_result)
                        
                        # Обновление дисплея
                        display.update_display(
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
                            last_attack_time=player.last_attack_time,
                            last_skill_time=player.last_skill_time
                        )
                        
                        time.sleep(0.1)  # Задержка между запросами
                        
                    except Exception as e:
                        display.print_message(f"Network error: {e}. Waiting 60 seconds before retry...", "error")
                        time.sleep(60)
                        continue
                
                # 3. Если моб подходит под условие удара скилом, то удар скилом
                if current_target and current_target.hp > Settings.SKILL_HP_THRESHOLD and player.can_use_skill(current_time):
                    # Отладочная информация
                    last_combat_time = max(player.last_attack_time, player.last_skill_time)
                    time_since_combat = current_time - last_combat_time
                    
                    skill_used = True  # Устанавливаем флаг ДО использования скилла
                    
                    try:
                        skill_result = api_client.use_skill(current_target.farm_id)
                        log_api_response(skill_result, context="use_skill")
                        player.record_skill(current_time)
                        display.print_message(f"⚡ Используем скилл против {current_target.name}...", "success")
                        
                        # Обновить данные игрока из ответа
                        player.update_from_api_response(skill_result)
                        
                        if isinstance(skill_result, dict):
                            if skill_result.get('status') == 'fail':
                                if 'Монстр не найден' in skill_result.get('message', '') or 'эта цель уже была мертва' in skill_result.get('message', ''):
                                    display.print_message(f"Скилл не сработал: {skill_result.get('message', 'Unknown error')}", "error")
                                    # Бой закончился, переходим к новому исследованию
                                    state_manager.change_state(GameState.CITY, "Combat ended - mob not found")
                                    current_mob_group = None
                                    explore_done = False  # Reset exploration flag
                                    display.print_message("🔄 Начинаем новое исследование...", "info")
                                    time.sleep(2)  # Задержка перед новым исследованием
                                    continue
                                else:
                                    display.print_message(f"Скилл не сработал: {skill_result.get('message', 'Unknown error')}", "error")
                            elif skill_result.get('status') == 'success':
                                # Обновить HP текущего моба из ответа скилла
                                if "mob" in skill_result:
                                    mob_data = skill_result["mob"]
                                    if current_target and current_target.farm_id == mob_data.get("farmId"):
                                        old_hp = current_target.hp
                                        current_target.hp = mob_data.get("hp", current_target.hp)
                                        current_target.max_hp = mob_data.get("maxHp", current_target.max_hp)
                                        damage_dealt = old_hp - current_target.hp
                                        
                                        # Получаем информацию о полученном уроне из arrLogs
                                        damage_received = 0
                                        arr_logs = skill_result.get('arrLogs', [])
                                        for log_entry in arr_logs:
                                            messages = log_entry.get('messages', [])
                                            for message in messages:
                                                if 'наносит' in message and 'урон' in message:
                                                    # Пытаемся извлечь урон из сообщения
                                                    import re
                                                    damage_match = re.search(r'наносит (\d+) урон', message)
                                                    if damage_match:
                                                        damage_received = int(damage_match.group(1))
                                                        break
                                        
                                        if damage_dealt > 0:
                                            if damage_received > 0:
                                                display.print_message(f"⚡ Скилл: нанес {damage_dealt} урона, получил {damage_received} урона. {current_target.name} HP: {current_target.hp}/{current_target.max_hp}", "success")
                                            else:
                                                display.print_message(f"⚡ Скилл нанес {damage_dealt} урона {current_target.name}! HP: {current_target.hp}/{current_target.max_hp}", "success")
                                        else:
                                            if damage_received > 0:
                                                display.print_message(f"⚡ Скилл по {current_target.name} - промах! Получил {damage_received} урона. HP: {current_target.hp}/{current_target.max_hp}", "warning")
                                            else:
                                                display.print_message(f"⚡ Скилл по {current_target.name} - промах! HP: {current_target.hp}/{current_target.max_hp}", "warning")
                                
                                # Check for victory status
                                if skill_result.get('statusBattle') == 'win':
                                    # Extract victory data
                                    arr_logs = skill_result.get('arrLogs', [])
                                    killed_names = []
                                    for log_entry in arr_logs:
                                        messages = log_entry.get('messages', [])
                                        for message in messages:
                                            if 'погиб' in message or 'погибла' in message:
                                                killed_names.append(log_entry.get('defname', 'Unknown'))
                                    
                                    # Подсчитываем всех мертвых мобов в группе
                                    dead_mobs_count = 0
                                    for mob in current_mob_group.get_all_mobs():
                                        if mob.hp <= 0:
                                            dead_mobs_count += 1
                                            display.update_killed_mobs(mob.name)
                                    
                                    # Всегда используем подсчитанное количество мертвых мобов
                                    final_killed_count = dead_mobs_count
                                    
                                    # Обрабатываем дроп если есть
                                    drop_data = skill_result.get('dataWin', {}).get('drop', [])
                                    if drop_data:
                                        display.update_drops(drop_data)
                                    
                                    # Обновляем общий счетчик убитых мобов
                                    total_mobs_killed += final_killed_count
                                    
                                    display.update_stats(
                                        mobs_killed=total_mobs_killed,
                                        total_exp=display.stats['total_exp'] + skill_result.get('dataWin', {}).get('expWin', 0),
                                        session_gold=display.stats['session_gold'] + sum(item.get('count', 0) for item in drop_data if item.get('id') == 'm_0_1')
                                    )
                                    exp_gained = skill_result.get('dataWin', {}).get('expWin', 0)
                                    gold_gained = sum(item.get('count', 0) for item in drop_data if item.get('id') == 'm_0_1')
                                    display.print_message(f"🎉 Все враги побеждены! Убито мобов: {final_killed_count}, +{exp_gained} опыта, +{gold_gained} золота", "success")
                                    state_manager.change_state(GameState.CITY, "Combat ended - all mobs defeated")
                                    current_mob_group = None
                                    explore_done = False  # Reset exploration flag
                                    time.sleep(2)  # Задержка перед новым исследованием
                                    continue
                                
                                # Update mob data from response
                                current_mob_group.update_from_combat_response(skill_result)
                                
                                # Обновляем дисплей после атаки
                                display.update_display(
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
                                    last_attack_time=player.last_attack_time,
                                    last_skill_time=player.last_skill_time
                                )
                                
                                # Проверить, не умер ли моб после атаки
                                if current_target and current_target.hp <= 0:
                                    display.print_message(f"💀 {current_target.name} повержен!", "success")
                                    
                                    # Обновляем статистику убитого моба
                                    display.update_killed_mobs(current_target.name)
                                    total_mobs_killed += 1
                                    display.update_stats(mobs_killed=total_mobs_killed)
                                    
                                    next_target = current_mob_group.switch_to_next_alive_target()
                                    if next_target:
                                        current_target = next_target
                                        display.print_message(f"🎯 Переключился на: {current_target.name} (HP: {current_target.hp})", "info")
                                    else:
                                        # Все мобы мертвы, но statusBattle не 'win' - обрабатываем как победу
                                        arr_logs = skill_result.get('arrLogs', [])
                                        killed_names = []
                                        for log_entry in arr_logs:
                                            messages = log_entry.get('messages', [])
                                            for message in messages:
                                                if 'погиб' in message or 'погибла' in message:
                                                    killed_names.append(log_entry.get('defname', 'Unknown'))
                                        
                                        # Подсчитываем всех мертвых мобов в группе
                                        dead_mobs_count = 0
                                        for mob in current_mob_group.get_all_mobs():
                                            if mob.hp <= 0:
                                                dead_mobs_count += 1
                                                display.update_killed_mobs(mob.name)
                                        
                                        # Всегда используем подсчитанное количество мертвых мобов
                                        final_killed_count = dead_mobs_count
                                        
                                        # Обрабатываем дроп если есть
                                        drop_data = skill_result.get('dataWin', {}).get('drop', [])
                                        if drop_data:
                                            display.update_drops(drop_data)
                                        
                                        # Обновляем общий счетчик убитых мобов
                                        total_mobs_killed += final_killed_count
                                        
                                        display.update_stats(
                                            mobs_killed=total_mobs_killed,
                                            total_exp=display.stats['total_exp'] + skill_result.get('dataWin', {}).get('expWin', 0),
                                            session_gold=display.stats['session_gold'] + sum(item.get('count', 0) for item in drop_data if item.get('id') == 'm_0_1')
                                        )
                                        exp_gained = skill_result.get('dataWin', {}).get('expWin', 0)
                                        gold_gained = sum(item.get('count', 0) for item in drop_data if item.get('id') == 'm_0_1')
                                        display.print_message(f"🎉 Все враги побеждены! Убито мобов: {final_killed_count}, +{exp_gained} опыта, +{gold_gained} золота", "success")
                                        state_manager.change_state(GameState.CITY, "Combat ended - all mobs defeated")
                                        current_mob_group = None
                                        explore_done = False  # Reset exploration flag
                                        time.sleep(2)  # Задержка перед новым исследованием
                                        continue
                        
                        time.sleep(0.1)  # Задержка между запросами
                        current_time = time.time()  # Обновляем время после sleep
                        
                    except Exception as e:
                        display.print_message(f"Network error: {e}. Waiting 60 seconds before retry...", "error")
                        time.sleep(60)
                    
                    # ВАЖНО: continue находится ЗА пределами try-except
                    continue  # <--- Гарантированный переход к следующей итерации
                
                # 6. Обновление дисплея
                display.update_display(
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
                    last_attack_time=player.last_attack_time,
                    last_skill_time=player.last_skill_time
                )
                
                # 7. Удар атакой (только если скилл не был использован в этом цикле)
                if not skill_used and player.can_attack(current_time) and current_target and current_target.hp > 0:
                    display.print_message(f"⚔️ Атакуем {current_target.name}...", "info")
                    
                    try:
                        attack_result = api_client.attack_mob(current_target.farm_id)
                        log_api_response(attack_result, context="attack_mob")
                        player.record_attack(current_time)
                        
                        if isinstance(attack_result, dict):
                            if attack_result.get('status') == 'fail':
                                if 'Монстр не найден' in attack_result.get('message', '') or 'эта цель уже была мертва' in attack_result.get('message', ''):
                                    display.print_message("Моб не найден для атаки, возможно бой уже закончился", "info")
                                    # Бой закончился, переходим к новому исследованию
                                    state_manager.change_state(GameState.CITY, "Combat ended - mob not found")
                                    current_mob_group = None
                                    explore_done = False  # Reset exploration flag
                                    display.print_message("🔄 Начинаем новое исследование...", "info")
                                    time.sleep(2)  # Задержка перед новым исследованием
                                    continue
                                else:
                                    display.print_message(f"Атака не удалась: {attack_result.get('message', 'Unknown error')}", "error")
                            elif attack_result.get('status') == 'success':
                                # Update player data from response
                                player.update_from_api_response(attack_result)
                                
                                # Обновить HP текущего моба из ответа атаки
                                if "mob" in attack_result:
                                    mob_data = attack_result["mob"]
                                    if current_target and current_target.farm_id == mob_data.get("farmId"):
                                        old_hp = current_target.hp
                                        current_target.hp = mob_data.get("hp", current_target.hp)
                                        current_target.max_hp = mob_data.get("maxHp", current_target.max_hp)
                                        damage_dealt = old_hp - current_target.hp
                                        
                                        # Получаем информацию о полученном уроне из arrLogs
                                        damage_received = 0
                                        arr_logs = attack_result.get('arrLogs', [])
                                        for log_entry in arr_logs:
                                            messages = log_entry.get('messages', [])
                                            for message in messages:
                                                if 'наносит' in message and 'урон' in message:
                                                    # Пытаемся извлечь урон из сообщения
                                                    import re
                                                    damage_match = re.search(r'наносит (\d+) урон', message)
                                                    if damage_match:
                                                        damage_received = int(damage_match.group(1))
                                                        break
                                        
                                        if damage_dealt > 0:
                                            if damage_received > 0:
                                                display.print_message(f"⚔️ Атака: нанес {damage_dealt} урона, получил {damage_received} урона. {current_target.name} HP: {current_target.hp}/{current_target.max_hp}", "success")
                                            else:
                                                display.print_message(f"⚔️ Атака нанесла {damage_dealt} урона {current_target.name}! HP: {current_target.hp}/{current_target.max_hp}", "success")
                                        else:
                                            if damage_received > 0:
                                                display.print_message(f"⚔️ Атака по {current_target.name} - промах! Получил {damage_received} урона. HP: {current_target.hp}/{current_target.max_hp}", "warning")
                                            else:
                                                display.print_message(f"⚔️ Атака по {current_target.name} - промах! HP: {current_target.hp}/{current_target.max_hp}", "warning")
                                
                                # Check for victory status
                                if attack_result.get('statusBattle') == 'win':
                                    # Extract victory data
                                    arr_logs = attack_result.get('arrLogs', [])
                                    killed_names = []
                                    for log_entry in arr_logs:
                                        messages = log_entry.get('messages', [])
                                        for message in messages:
                                            if 'погиб' in message or 'погибла' in message:
                                                killed_names.append(log_entry.get('defname', 'Unknown'))
                                    
                                    # Подсчитываем всех мертвых мобов в группе
                                    dead_mobs_count = 0
                                    for mob in current_mob_group.get_all_mobs():
                                        if mob.hp <= 0:
                                            dead_mobs_count += 1
                                            display.update_killed_mobs(mob.name)
                                    
                                    # Всегда используем подсчитанное количество мертвых мобов
                                    final_killed_count = dead_mobs_count
                                    
                                    # Обрабатываем дроп если есть
                                    drop_data = attack_result.get('dataWin', {}).get('drop', [])
                                    if drop_data:
                                        display.update_drops(drop_data)
                                    
                                    # Обновляем общий счетчик убитых мобов
                                    total_mobs_killed += final_killed_count
                                    
                                    display.update_stats(
                                        mobs_killed=total_mobs_killed,
                                        total_exp=display.stats['total_exp'] + attack_result.get('dataWin', {}).get('expWin', 0),
                                        session_gold=display.stats['session_gold'] + sum(item.get('count', 0) for item in drop_data if item.get('id') == 'm_0_1')
                                    )
                                    exp_gained = attack_result.get('dataWin', {}).get('expWin', 0)
                                    gold_gained = sum(item.get('count', 0) for item in drop_data if item.get('id') == 'm_0_1')
                                    display.print_message(f"🎉 Все враги побеждены! Убито мобов: {final_killed_count}, +{exp_gained} опыта, +{gold_gained} золота", "success")
                                    state_manager.change_state(GameState.CITY, "Combat ended - all mobs defeated")
                                    current_mob_group = None
                                    explore_done = False  # Reset exploration flag
                                    time.sleep(2)  # Задержка перед новым исследованием
                                    continue
                                
                                # Update mob data from response
                                current_mob_group.update_from_combat_response(attack_result)
                                
                                # Обновляем дисплей после атаки
                                display.update_display(
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
                                    last_attack_time=player.last_attack_time,
                                    last_skill_time=player.last_skill_time
                                )
                                
                                # Проверить, не умер ли моб после атаки
                                if current_target and current_target.hp <= 0:
                                    display.print_message(f"💀 {current_target.name} повержен!", "success")
                                    
                                    # Обновляем статистику убитого моба
                                    display.update_killed_mobs(current_target.name)
                                    total_mobs_killed += 1
                                    display.update_stats(mobs_killed=total_mobs_killed)
                                    
                                    next_target = current_mob_group.switch_to_next_alive_target()
                                    if next_target:
                                        current_target = next_target
                                        display.print_message(f"🎯 Переключился на: {current_target.name} (HP: {current_target.hp})", "info")
                                    else:
                                        # Все мобы мертвы, но statusBattle не 'win' - обрабатываем как победу
                                        arr_logs = attack_result.get('arrLogs', [])
                                        killed_names = []
                                        for log_entry in arr_logs:
                                            messages = log_entry.get('messages', [])
                                            for message in messages:
                                                if 'погиб' in message or 'погибла' in message:
                                                    killed_names.append(log_entry.get('defname', 'Unknown'))
                                        
                                        # Подсчитываем всех мертвых мобов в группе
                                        dead_mobs_count = 0
                                        for mob in current_mob_group.get_all_mobs():
                                            if mob.hp <= 0:
                                                dead_mobs_count += 1
                                                display.update_killed_mobs(mob.name)
                                        
                                        # Всегда используем подсчитанное количество мертвых мобов
                                        final_killed_count = dead_mobs_count
                                        
                                        # Обрабатываем дроп если есть
                                        drop_data = attack_result.get('dataWin', {}).get('drop', [])
                                        if drop_data:
                                            display.update_drops(drop_data)
                                        
                                        # Обновляем общий счетчик убитых мобов
                                        total_mobs_killed += final_killed_count
                                        
                                        display.update_stats(
                                            mobs_killed=total_mobs_killed,
                                            total_exp=display.stats['total_exp'] + attack_result.get('dataWin', {}).get('expWin', 0),
                                            session_gold=display.stats['session_gold'] + sum(item.get('count', 0) for item in drop_data if item.get('id') == 'm_0_1')
                                        )
                                        exp_gained = attack_result.get('dataWin', {}).get('expWin', 0)
                                        gold_gained = sum(item.get('count', 0) for item in drop_data if item.get('id') == 'm_0_1')
                                        display.print_message(f"🎉 Все враги побеждены! Убито мобов: {final_killed_count}, +{exp_gained} опыта, +{gold_gained} золота", "success")
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
                    time.sleep(0.1)
                    current_time = time.time()  # Обновляем время после sleep
                    continue
            
            elif current_state == GameState.RESTING:
                if rest_end_time and current_time >= rest_end_time:
                    display.print_rest_complete()
                    state_manager.change_state(GameState.CITY, "Rest completed")
                    rest_end_time = None
                    explore_done = False  # Reset exploration flag
                elif not rest_end_time:
                    # No rest time set, go back to city
                    display.print_message("No rest time set, returning to city", "warning")
                    state_manager.change_state(GameState.CITY, "No rest time set")
                    explore_done = False  # Reset exploration flag
                else:
                    # Still resting
                    time.sleep(0.1)
                    current_time = time.time()  # Обновляем время после sleep
                    continue
            
            else:
                display.print_message(f"Unknown state: {current_state}", "error")
                break
            
            # Small delay to prevent excessive CPU usage
            time.sleep(0.1)
    
    display.print_message("Bot stopped", "info")

if __name__ == "__main__":
    main() 