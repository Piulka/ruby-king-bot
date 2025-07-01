"""
UI Display Module for Ruby King Bot
Provides beautiful console interface with real-time status updates
"""

import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn
from rich.live import Live
from rich.text import Text
from rich.columns import Columns
from rich.align import Align
from rich.table import Table
from rich import box
import logging

# Import item database
from ..utils.item_database import format_item_display_with_emoji, get_item_emoji, get_item_name
from ..config.constants import LOCATION_NAMES, DIRECTION_NAMES

class GameDisplay:
    """Beautiful console UI for Ruby King Bot"""
    
    def __init__(self):
        """Initialize the display"""
        self.console = Console()
        self.layout = Layout()
        
        # Initialize tracking data
        self.stats = {
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
        
        # Message history
        self.message_history = []
        self.max_messages = 10
        
        # Drop items tracking
        self.drop_items = {}
        
        # Killed mobs tracking
        self.killed_mobs = {}
        
        # Cooldown tracking for GCD calculation
        self.last_attack_time = 0
        self.last_skill_time = 0
        
        # Setup layout
        self.layout.split_column(
            Layout(name="top", size=3),
            Layout(name="main"),
            Layout(name="bottom", size=12)  # Фиксированный размер для сообщений
        )
        
        self.layout["main"].split_row(
            Layout(name="left"),
            Layout(name="right")
        )
        
        self.layout["left"].split_column(
            Layout(name="player", size=9),  # Фиксированный размер
            Layout(name="combat", size=11),  # Увеличиваем с 9 до 11
            Layout(name="route", size=8),  # Новый блок для маршрута
            Layout(name="killed_mobs", ratio=1)  # Растягивается до блока сообщений
        )
        
        self.layout["right"].split_column(
            Layout(name="stats", size=9),  # Фиксированный размер
            Layout(name="cooldowns", size=11),  # Увеличиваем с 9 до 11
            Layout(name="drops", ratio=1)  # Растягивается до блока сообщений
        )
    
    def get_live_display(self, refresh_per_second: int = 1, screen: bool = True) -> Live:
        """
        Get live display context manager for the game engine
        
        Args:
            refresh_per_second: Refresh rate for the display (default 1 per second)
            screen: Whether to use screen clearing
            
        Returns:
            Live display context manager
        """
        return Live(self.layout, refresh_per_second=refresh_per_second, screen=screen)
    
    def auto_refresh_display(self):
        """Force display refresh - called every second"""
        # This method can be called to force a display refresh
        # The Live display will automatically refresh based on refresh_per_second
        pass
    
    def update_stats(self, **kwargs):
        """Update statistics"""
        for key, value in kwargs.items():
            if key in self.stats:
                # Для новых полей — всегда инкрементируем
                if key in ['city_visits', 'items_sold', 'gold_from_sales', 'hp_potions_used', 'mp_potions_used', 'total_exp', 'session_gold']:
                    self.stats[key] += value
                else:
                    self.stats[key] = value
            elif key == 'current_gold':
                self.stats['current_gold'] = value
            elif key == 'current_skulls':
                self.stats['current_skulls'] = value
            elif key == 'events_found':
                self.stats['events_found'] = value
            elif key in ['squares_visited', 'directions_visited', 'locations_visited']:
                self.stats[key] = value
    
    def format_time(self, seconds: int) -> str:
        """Format seconds to mm:ss"""
        if seconds < 0:
            return "00:00"
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes:02d}:{secs:02d}"
    
    def create_header(self, current_state: str, player_name: str = "Unknown", player_data: Dict[str, Any] = None) -> Panel:
        """Create header panel with game status"""
        # Добавляем уровень и XP шкалу слева от ника
        level_xp_text = ""
        if player_data:
            level = player_data.get('level', 1)
            xp = player_data.get('xp', 0)
            xp_next = player_data.get('xp_next', 1)
            
            # Создаем XP шкалу
            if xp_next > 0:
                xp_percent = (xp / xp_next) * 100
                xp_filled = int(xp_percent / 10)
                xp_bar = f"{'█' * xp_filled}{'░' * (10 - xp_filled)}"
                level_xp_text = f"Lv.{level} XP:{xp_bar} {xp}/{xp_next}"
        
        session_time = self.format_time(int(time.time() - self.stats['session_start']))
        title = f"[bold blue]{level_xp_text}[/bold blue] - [bold green]{player_name}[/bold green] - [bold cyan]⏱️ {session_time}[/bold cyan]"
        status_text = f"Состояние: [bold yellow]{current_state.upper()}[/bold yellow]"
        
        content = f"{title}\n{status_text}"
        return Panel(content, title="[bold]Статус игры[/bold]", border_style="blue")
    
    def create_player_status(self, player_data: Dict[str, Any]) -> Panel:
        """Create player status panel with HP/MP/Stamina bars"""
        hp_percent = (player_data.get('hp', 0) / max(player_data.get('max_hp', 1), 1)) * 100
        mp_percent = (player_data.get('mana', 0) / max(player_data.get('max_mana', 1), 1)) * 100
        
        # Используем мораль как стамину
        stamina_value = player_data.get('morale', 0)
        max_stamina_value = 100  # Максимум морали 100
        stamina_percent = (stamina_value / max(max_stamina_value, 1)) * 100
        
        # HP Bar
        hp_color = "green" if hp_percent > 50 else "yellow" if hp_percent > 25 else "red"
        hp_bar = f"[{hp_color}]█[/{hp_color}]" * int(hp_percent / 10) + "░" * (10 - int(hp_percent / 10))
        
        # MP Bar
        mp_bar = f"[blue]█[/blue]" * int(mp_percent / 10) + "░" * (10 - int(mp_percent / 10))
        
        # Stamina/Morale Bar
        stamina_bar = f"[cyan]█[/cyan]" * int(stamina_percent / 10) + "░" * (10 - int(stamina_percent / 10))
        
        gold = player_data.get('gold', 0)
        skulls = player_data.get('skulls', 0)
        heal_potions = player_data.get('heal_potions', 0)
        mana_potions = player_data.get('mana_potions', 0)
        inventory_weight = player_data.get('inventory_weight', 0)
        max_inventory_weight = player_data.get('max_inventory_weight', 10000)
        
        content = f"""
[bold]Статус игрока[/bold]
HP:   {hp_bar} {player_data.get('hp', 0)}/{player_data.get('max_hp', 0)} ({hp_percent:.1f}%)
MP:   {mp_bar} {player_data.get('mana', 0)}/{player_data.get('max_mana', 0)} ({mp_percent:.1f}%)
MR:   {stamina_bar} {stamina_value}/{max_stamina_value} ({stamina_percent:.1f}%)
[bold yellow]💰 Золото:[/bold yellow] [yellow]{gold}[/yellow]   [bold red]💀 Черепа:[/bold red] [red]{skulls}[/red]
[bold red]🔴 Хилки:[/bold red] [red]{heal_potions}[/red]   [bold blue]🔵 Мана:[/bold blue] [blue]{mana_potions}[/blue]
        """.strip()
        
        return Panel(content, title="[bold]Игрок[/bold]", border_style="green", height=9)
    
    def create_combat_status(self, mob_data: Optional[Dict[str, Any]], mob_group_data: Optional[List[Dict[str, Any]]], 
                           location: str = "", direction: str = "", square: str = "") -> Panel:
        """Create combat status panel"""
        content_lines = []
        
        # Показываем информацию о локации
        if location and direction and square:
            # Переводим ID локации в название и направление на русский
            location_name = LOCATION_NAMES.get(location, location)
            direction_name = DIRECTION_NAMES.get(direction, direction)
            content_lines.append(f"Локация: {location_name} | {direction_name} | {square}")
        elif location:
            location_name = LOCATION_NAMES.get(location, location)
            content_lines.append(f"Локация: {location_name}")
        
        content_lines.append("")  # Пустая строка
        
        if mob_group_data and len(mob_group_data) > 0:
            # Multi-mob display
            content_lines.append(f"Найдено врагов: {len(mob_group_data)}")
            
            for i, mob_info in enumerate(mob_group_data):
                mob_name = mob_info.get('name', 'Неизвестно')
                mob_level = mob_info.get('level', 1)
                mob_hp_str = mob_info.get('hp', '0/0')
                is_current_target = mob_info.get('is_current_target', False)
                is_dead = mob_info.get('is_dead', False)
                
                # Parse HP string like "123/134" or "-6/144"
                if '/' in mob_hp_str:
                    current_hp_str, max_hp_str = mob_hp_str.split('/')
                    try:
                        current_hp = int(current_hp_str)
                        max_hp = int(max_hp_str)
                        mob_hp_percent = (current_hp / max_hp) * 100 if max_hp > 0 else 0
                    except ValueError:
                        current_hp = 0
                        max_hp = 1
                        mob_hp_percent = 0
                else:
                    current_hp = 0
                    max_hp = 1
                    mob_hp_percent = 0
                
                # Color based on HP percentage
                if is_dead or current_hp <= 0:
                    mob_hp_color = "dim"
                elif mob_hp_percent > 50:
                    mob_hp_color = "green"
                elif mob_hp_percent > 25:
                    mob_hp_color = "yellow"
                else:
                    mob_hp_color = "red"
                
                # Create HP bar
                bar_length = 10
                filled_bars = int(mob_hp_percent / 10)
                mob_hp_bar = f"[{mob_hp_color}]█[/{mob_hp_color}]" * filled_bars + "░" * (bar_length - filled_bars)
                
                # Target indicator
                if is_current_target:
                    target_indicator = "🎯 "  # Target for current mob
                else:
                    target_indicator = "   "  # Empty for other mobs
                
                content_lines.append(f"{target_indicator}[bold red]{mob_name}[/bold red] ур.{mob_level}")
                content_lines.append(f"    HP: {mob_hp_bar} {mob_hp_str} ({mob_hp_percent:.1f}%)")
        else:
            # Single mob display (backward compatibility)
            if mob_data is None:
                content_lines.append("[dim]Нет активного боя[/dim]")
            else:
                mob_hp_percent = (mob_data.get('hp', 0) / max(mob_data.get('max_hp', 1), 1)) * 100
                mob_hp_color = "green" if mob_hp_percent > 50 else "yellow" if mob_hp_percent > 25 else "red"
                mob_hp_bar = f"[{mob_hp_color}]█[/{mob_hp_color}]" * int(mob_hp_percent / 10) + "░" * (10 - int(mob_hp_percent / 10))
                content_lines.append(f"Цель: [bold red]{mob_data.get('name', 'Неизвестно')}[/bold red] ур.{mob_data.get('level', 1)}")
                content_lines.append(f"HP: {mob_hp_bar} {mob_data.get('hp', 0)}/{mob_data.get('max_hp', 0)} ({mob_hp_percent:.1f}%)")
        
        content = "\n".join(content_lines)
        return Panel(content, title="[bold]Бой[/bold]", border_style="magenta", height=11)
    
    def create_stats_table(self) -> Panel:
        """Create statistics panel"""
        stats = self.stats
        avg_damage = self.get_average_damage()
        
        # Подсчитываем общее количество убитых врагов из killed_mobs
        total_killed_mobs = sum(self.killed_mobs.values()) if self.killed_mobs else 0
        
        # Создаем таблицу
        table = Table.grid(padding=(0, 2))  # Увеличиваем отступы между столбцами
        table.add_column(justify="left")
        table.add_column(justify="right")
        table.add_column(justify="left")
        table.add_column(justify="right")
        
        # Левый столбец (6 строк)
        table.add_row("[bold yellow]Опыт:[/bold yellow]", f"[yellow]│{stats['total_exp']}│[/yellow]", 
                     "[bold magenta]В город:[/bold magenta]", f"[magenta]│{stats.get('city_visits', 0)}│[/magenta]")
        table.add_row("[bold yellow]Золото:[/bold yellow]", f"[yellow]│{stats['session_gold']}│[/yellow]", 
                     "[bold green]Продано:[/bold green]", f"[green]│{stats.get('items_sold', 0)}│[/green]")
        table.add_row("[bold cyan]События:[/bold cyan]", f"[cyan]│{stats.get('events_found', 0)}│[/cyan]", 
                     "[bold red]Хилки:[/bold red]", f"[red]│{stats.get('hp_potions_used', 0)}│[/red]")
        table.add_row("[bold]Ср. урон:[/bold]", f"[yellow]│{avg_damage:.1f}│[/yellow]", 
                     "[bold blue]Мана:[/bold blue]", f"[blue]│{stats.get('mp_potions_used', 0)}│[/blue]")
        table.add_row("[bold]Убито мобов:[/bold]", f"[green]│{total_killed_mobs}│[/green]", 
                     "[bold green]Золото с продаж:[/bold green]", f"[yellow]│{stats.get('gold_from_sales', 0)}│[/yellow]")
        table.add_row("[bold]Квадраты:[/bold]", f"[cyan]│{stats.get('squares_visited', 0)}│[/cyan]", 
                     "[bold]Локации:[/bold]", f"[blue]│{stats.get('locations_visited', 0)}│[/blue]")
        
        return Panel(table, title="[bold]Статистика[/bold]", border_style="cyan", height=9)
    
    def create_timers(self, attack_cooldown: float = 0, heal_cooldown: float = 0, rest_time: Optional[float] = None) -> Panel:
        """Create timers panel"""
        content = "[bold]Timers[/bold]\n"
        
        # Attack cooldown
        if attack_cooldown > 0:
            content += f"Attack CD: [red]{self.format_time(int(attack_cooldown))}[/red]\n"
        else:
            content += "Attack CD: [green]Ready[/green]\n"
        
        # Heal cooldown
        if heal_cooldown > 0:
            content += f"Heal CD: [red]{self.format_time(int(heal_cooldown))}[/red]\n"
        else:
            content += "Heal CD: [green]Ready[/green]\n"
        
        # Rest timer
        if rest_time:
            remaining = max(0, rest_time - time.time())
            if remaining > 0:
                content += f"Rest: [yellow]{self.format_time(int(remaining))}[/yellow]\n"
            else:
                content += "Rest: [green]Complete[/green]\n"
        else:
            content += "Rest: [dim]None[/dim]\n"
        
        return Panel(content, title="[bold]Cooldowns[/bold]", border_style="yellow")
    
    def create_messages_panel(self) -> Panel:
        """Create messages panel"""
        if not self.message_history:
            content = "[dim]No messages[/dim]"
        else:
            # Show last messages
            recent_messages = self.message_history[-self.max_messages:]
            content = "\n".join(recent_messages)
        
        return Panel(content, title="[bold]Сообщения[/bold]", border_style="cyan", height=12)
    
    def add_message(self, message: str, level: str = "info"):
        """Add message to history"""
        colors = {
            "info": "blue",
            "success": "green", 
            "warning": "yellow",
            "error": "red"
        }
        color = colors.get(level, "white")
        timestamp = time.strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] [{color}]{message}[/{color}]"
        
        self.message_history.append(formatted_message)
        
        # Keep only last max_messages
        if len(self.message_history) > self.max_messages:
            self.message_history = self.message_history[-self.max_messages:]
    
    def update_display(self, current_state: str, player_data: dict, mob_data: dict = None, 
                      mob_group_data: list = None, attack_cooldown: float = 0, 
                      heal_cooldown: float = 0, skill_cooldown: float = 0, 
                      mana_cooldown: float = 0, rest_time: float = None, player_name: str = "Player",
                      last_attack_time: float = 0, last_skill_time: float = 0,
                      location: str = "", direction: str = "", square: str = "",
                      current_route: List = None, current_route_index: int = 0, mobs_killed_on_current_square: int = 0):
        """Update the display with current game information"""
        try:
            # Update cooldown tracking
            self.last_attack_time = last_attack_time
            self.last_skill_time = last_skill_time
            
            # Create header
            header = self.create_header(current_state, player_name, player_data)
            self.layout["top"].update(header)
            
            # Create player status
            player_panel = self.create_player_status(player_data)
            self.layout["left"]["player"].update(player_panel)
            
            # Create combat status
            combat_panel = self.create_combat_status(mob_data, mob_group_data, location, direction, square)
            self.layout["left"]["combat"].update(combat_panel)
            
            # Create route panel
            route_panel = self.create_route_panel(current_route, current_route_index, mobs_killed_on_current_square)
            self.layout["left"]["route"].update(route_panel)
            
            # Create killed mobs panel
            killed_mobs_panel = self.create_killed_mobs_panel()
            self.layout["left"]["killed_mobs"].update(killed_mobs_panel)
            
            # Create stats table
            stats_panel = self.create_stats_table()
            self.layout["right"]["stats"].update(stats_panel)
            
            # Create cooldowns panel
            cooldowns_panel = self.create_cooldowns_panel(attack_cooldown, heal_cooldown, skill_cooldown, mana_cooldown, rest_time)
            self.layout["right"]["cooldowns"].update(cooldowns_panel)
            
            # Create drops panel
            drops_panel = self.create_drops_panel()
            self.layout["right"]["drops"].update(drops_panel)
            
            # Create messages panel
            messages_panel = self.create_messages_panel()
            self.layout["bottom"].update(messages_panel)
            
        except Exception as e:
            logging.error(f"Error updating display: {e}")
            # Fallback to simple display
            self.layout["top"].update(Panel(f"Error: {e}", title="Error"))
    
    def print_message(self, message: str, level: str = "info"):
        """Print a message with appropriate styling"""
        # Add to UI message history instead of printing to console
        self.add_message(message, level)
    
    def print_combat_log(self, attacker: str, target: str, damage: int, text: str = ""):
        """Print combat log entry"""
        if damage > 0:
            self.add_message(f"{attacker} → {target}: {damage} урона {text}", "info")
        else:
            self.add_message(f"{attacker} → {target}: Промах! {text}", "warning")
    
    def print_victory(self, mob_name: str, exp_gained: int, items: list):
        """Print victory message"""
        self.add_message(f"🎉 ПОБЕДА! {mob_name} повержен!", "success")
        self.add_message(f"Получено опыта: {exp_gained}", "success")
        if items:
            self.add_message(f"Добыча: {', '.join(items)}", "success")
    
    def print_healing(self, old_hp: int, new_hp: int, max_hp: int):
        """Print healing message"""
        self.add_message(f"🔴 Использовано зелье лечения: {old_hp}/{max_hp} → {new_hp}/{max_hp}", "success")
    
    def print_rest_start(self, duration_minutes: int = 20):
        """Print rest start message"""
        self.add_message(f"🔥 Отдых у костра {duration_minutes} минут...", "warning")
    
    def print_rest_complete(self):
        """Print rest complete message"""
        self.add_message(f"✅ Отдых завершён! Мораль восстановлена.", "success")
    
    def update_drops(self, items: list):
        """Update drop items tracking"""
        for item in items:
            item_id = item.get('id', 'Unknown')
            if item_id != 'm_0_1':  # Исключаем золото
                if item_id in self.drop_items:
                    self.drop_items[item_id] += 1
                else:
                    self.drop_items[item_id] = 1
    
    def update_killed_mobs(self, mob_name: str, count: int = 1):
        """Update killed mobs tracking"""
        if mob_name in self.killed_mobs:
            self.killed_mobs[mob_name] += count
        else:
            self.killed_mobs[mob_name] = count
    
    def create_drops_panel(self) -> Panel:
        """Create drops panel in statistics style"""
        if not self.drop_items:
            content = "[dim]No drops yet[/dim]"
        else:
            table = Table.grid(padding=(0,1))
            table.add_column(justify="left", width=22)  # Фиксированная ширина для эмодзи+название
            table.add_column(justify="right")
            sorted_drops = sorted(self.drop_items.items(), key=lambda x: x[1], reverse=True)
            for item_id, count in sorted_drops:
                item_name = get_item_name(item_id)
                emoji = get_item_emoji(item_id)
                # Обрезаем/дополняем название до 16 символов
                display_name = item_name[:16] if len(item_name) > 16 else item_name.ljust(16)
                table.add_row(f"{emoji} {display_name}", f"[green]{count}")
            content = table
        return Panel(content, title="[bold]Дроп[/bold]", border_style="yellow")
    
    def create_killed_mobs_panel(self) -> Panel:
        """Create killed mobs panel in statistics style"""
        if not self.killed_mobs:
            content = "[dim]No mobs killed yet[/dim]"
        else:
            table = Table.grid(padding=(0,1))
            table.add_column(justify="left")
            table.add_column(justify="right")
            sorted_mobs = sorted(self.killed_mobs.items(), key=lambda x: x[1], reverse=True)
            for mob_name, count in sorted_mobs:
                table.add_row(f"{mob_name}", f"[green]{count}")
            content = table
        return Panel(content, title="[bold]Убитые враги[/bold]", border_style="red")
    
    def create_cooldowns_panel(self, attack_cooldown: float, heal_cooldown: float, skill_cooldown: float, mana_cooldown: float, rest_time: float = None) -> Panel:
        """Create cooldowns panel"""
        from rich.text import Text
        
        # Create table for aligned display
        table = Table.grid(padding=(0, 1))
        table.add_column(justify="left", width=6)   # Icon column - делаем уже
        table.add_column(justify="left", width=16)  # Name column - делаем шире
        table.add_column(justify="right", width=8)  # Status column
        
        # Attack cooldown
        attack_status = "Готов" if attack_cooldown <= 0 else f"{int(attack_cooldown)}s"
        attack_style = "green" if attack_cooldown <= 0 else "red"
        # Индикатор использованного навыка - подсветка на 5 секунд
        attack_icon = "⚔️🔥" if 0 < attack_cooldown <= 5 else "⚔️"
        table.add_row(attack_icon, "Атака", f"[{attack_style}]{attack_status}[/{attack_style}]")
        
        # Skill cooldown
        skill_status = "Готов" if skill_cooldown <= 0 else f"{int(skill_cooldown)}s"
        skill_style = "green" if skill_cooldown <= 0 else "red"
        # Индикатор использованного навыка - подсветка на 5 секунд
        skill_icon = "⚡🔥" if 0 < skill_cooldown <= 5 else "⚡"
        table.add_row(skill_icon, "Усиленный удар", f"[{skill_style}]{skill_status}[/{skill_style}]")
        
        # Heal cooldown
        heal_status = "Готов" if heal_cooldown <= 0 else f"{int(heal_cooldown)}s"
        heal_style = "green" if heal_cooldown <= 0 else "red"
        # Индикатор использованного навыка - подсветка на 5 секунд
        heal_icon = "❤️🔥" if 0 < heal_cooldown <= 5 else "❤️"
        table.add_row(heal_icon, "Лечение", f"[{heal_style}]{heal_status}[/{heal_style}]")
        
        # Mana cooldown
        mana_status = "Готов" if mana_cooldown <= 0 else f"{int(mana_cooldown)}s"
        mana_style = "green" if mana_cooldown <= 0 else "red"
        # Индикатор использованного навыка - подсветка на 5 секунд
        mana_icon = "🔵🔥" if 0 < mana_cooldown <= 5 else "🔵"
        table.add_row(mana_icon, "Мана", f"[{mana_style}]{mana_status}[/{mana_style}]")
        
        return Panel(table, title="⏱️ КД", border_style="blue", height=11)
    
    def update_damage_stats(self, damage_dealt: int):
        """Update damage statistics"""
        if damage_dealt > 0:
            self.stats['total_damage_dealt'] += damage_dealt
            self.stats['total_attacks'] += 1
    
    def get_average_damage(self) -> float:
        """Get average damage per attack"""
        if self.stats['total_attacks'] > 0:
            return self.stats['total_damage_dealt'] / self.stats['total_attacks']
        return 0.0 
    
    def update_route_progress(self, route_progress: str):
        """Обновить информацию о прогрессе маршрута"""
        self.add_message(route_progress, "info")
    
    def update_combat_status(self, combat_status: str, location: str, direction: str, square: str):
        """Обновить статус боя"""
        self.add_message(combat_status, "combat")
    
    def update_exp_gained(self, exp_gained: int):
        """Обновить полученный опыт"""
        if exp_gained > 0:
            self.add_message(f"🎉 +{exp_gained} опыта", "success")
    
    def update_gold_gained(self, gold_gained: int):
        """Обновить полученное золото"""
        if gold_gained > 0:
            self.add_message(f"💰 +{gold_gained} золота", "success")
    
    def update_mobs_killed(self, mobs_killed: int):
        """Обновить количество убитых мобов"""
        if mobs_killed > 0:
            self.add_message(f"⚔️ Убито мобов: {mobs_killed}", "combat")
    
    def create_route_panel(self, current_route: List = None, current_route_index: int = 0, mobs_killed_on_current_square: int = 0) -> Panel:
        """Create route panel with interactive route display"""
        if not current_route:
            content = "[dim]Маршрут не настроен[/dim]"
            return Panel(content, title="[bold]Маршрут[/bold]", border_style="cyan", height=8)
        
        content_lines = []
        content_lines.append(f"[bold cyan]Маршрут: {current_route_index + 1}/{len(current_route)}[/bold cyan]")
        
        # Показываем текущую точку и несколько следующих
        start_idx = max(0, current_route_index - 1)
        end_idx = min(len(current_route), current_route_index + 4)
        
        for i in range(start_idx, end_idx):
            point = current_route[i]
            if i == current_route_index:
                # Текущая точка - выделяем
                mobs_text = f" [red]💀{mobs_killed_on_current_square}[/red]" if mobs_killed_on_current_square > 0 else ""
                content_lines.append(f"[bold yellow]▶ {point.location_name} | {point.direction_name} | {point.square}{mobs_text}[/bold yellow]")
            else:
                content_lines.append(f"[dim]  {point.location_name} | {point.direction_name} | {point.square}[/dim]")
        
        if end_idx < len(current_route):
            content_lines.append(f"[dim]  ... и еще {len(current_route) - end_idx} точек[/dim]")
        
        content = "\n".join(content_lines)
        return Panel(content, title="[bold]Маршрут[/bold]", border_style="cyan", height=8) 