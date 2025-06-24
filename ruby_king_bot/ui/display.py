"""
UI Display Module for Ruby King Bot
Provides beautiful console interface with real-time status updates
"""

import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
from rich.columns import Columns
from rich.align import Align

class GameDisplay:
    """Beautiful console UI for Ruby King Bot"""
    
    def __init__(self):
        self.console = Console()
        self.layout = Layout()
        self.stats = {
            'mobs_killed': 0,
            'total_exp': 0,
            'session_start': time.time(),
            'current_gold': 0,
            'current_skulls': 0,
            'events_found': 0
        }
        
        # Message history for UI
        self.message_history = []
        self.max_messages = 10
        
        # Create layout
        self.layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main", ratio=1),
            Layout(name="messages", size=12)  # Увеличиваем размер messages
        )
        
        self.layout["main"].split_row(
            Layout(name="left", ratio=1),
            Layout(name="right", ratio=1)
        )
        
        self.layout["left"].split_column(
            Layout(name="status"),
            Layout(name="combat", size=8),
            Layout(name="timers", size=6)
        )
        
        self.layout["right"].split_column(
            Layout(name="stats")
        )
    
    def update_stats(self, **kwargs):
        """Update statistics"""
        for key, value in kwargs.items():
            if key in self.stats:
                if key in ['total_exp']:
                    self.stats[key] += value
                else:
                    self.stats[key] = value
            elif key == 'current_gold':
                self.stats['current_gold'] = value
            elif key == 'current_skulls':
                self.stats['current_skulls'] = value
            elif key == 'events_found':
                self.stats['events_found'] = value
    
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
        
        title = f"[bold blue]{level_xp_text}[/bold blue] - [bold green]{player_name}[/bold green]"
        status_text = f"State: [bold yellow]{current_state.upper()}[/bold yellow]"
        time_text = f"Session: {self.format_time(int(time.time() - self.stats['session_start']))}"
        
        content = f"{title}\n{status_text} | {time_text}"
        return Panel(content, title="[bold]Game Status[/bold]", border_style="blue")
    
    def create_player_status(self, player_data: Dict[str, Any]) -> Panel:
        """Create player status panel with HP/MP/Stamina bars"""
        hp_percent = (player_data.get('hp', 0) / max(player_data.get('max_hp', 1), 1)) * 100
        mp_percent = (player_data.get('mp', 0) / max(player_data.get('max_mp', 1), 1)) * 100
        
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
        
        content = f"""
[bold]Player Status[/bold]
HP:   {hp_bar} {player_data.get('hp', 0)}/{player_data.get('max_hp', 0)} ({hp_percent:.1f}%)
MP:   {mp_bar} {player_data.get('mp', 0)}/{player_data.get('max_mp', 0)} ({mp_percent:.1f}%)
MR:   {stamina_bar} {stamina_value}/{max_stamina_value} ({stamina_percent:.1f}%)
Gold: {player_data.get('gold', 0)} | Skulls: {player_data.get('skulls', 0)}
Healing Potions: {player_data.get('heal_potions', 0)}
        """.strip()
        
        return Panel(content, title="[bold]Player[/bold]", border_style="green")
    
    def create_combat_status(self, mob_data: Optional[Dict[str, Any]] = None) -> Panel:
        """Create combat status panel"""
        if not mob_data:
            content = "[dim]No active combat[/dim]"
        else:
            mob_hp_percent = (mob_data.get('hp', 0) / max(mob_data.get('max_hp', 1), 1)) * 100
            mob_hp_color = "green" if mob_hp_percent > 50 else "yellow" if mob_hp_percent > 25 else "red"
            mob_hp_bar = f"[{mob_hp_color}]█[/{mob_hp_color}]" * int(mob_hp_percent / 10) + "░" * (10 - int(mob_hp_percent / 10))
            
            content = f"""
[bold]Combat[/bold]
Target: [bold red]{mob_data.get('name', 'Unknown')}[/bold red] Lv.{mob_data.get('level', 1)}
HP: {mob_hp_bar} {mob_data.get('hp', 0)}/{mob_data.get('max_hp', 0)} ({mob_hp_percent:.1f}%)
            """.strip()
        
        return Panel(content, title="[bold]Combat[/bold]", border_style="red")
    
    def create_stats_table(self) -> Panel:
        """Create statistics table"""
        table = Table(title="[bold]Session Statistics[/bold]", show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        session_time = int(time.time() - self.stats['session_start'])
        mobs_per_hour = (self.stats['mobs_killed'] / max(session_time / 3600, 0.1))
        
        table.add_row("Mobs Killed", str(self.stats['mobs_killed']))
        table.add_row("Total XP", str(self.stats['total_exp']))
        table.add_row("Session Time", self.format_time(session_time))
        table.add_row("Mobs/Hour", f"{mobs_per_hour:.1f}")
        table.add_row("Events Found", str(self.stats.get('events_found', 0)))
        table.add_row("Current Gold", str(self.stats.get('current_gold', 0)))
        table.add_row("Current Skulls", str(self.stats.get('current_skulls', 0)))
        
        return Panel(table, title="[bold]Statistics[/bold]", border_style="magenta")
    
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
        
        return Panel(content, title="[bold]Messages[/bold]", border_style="cyan")
    
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
    
    def update_display(self, 
                      current_state: str,
                      player_data: Dict[str, Any],
                      mob_data: Optional[Dict[str, Any]] = None,
                      attack_cooldown: float = 0,
                      heal_cooldown: float = 0,
                      rest_time: Optional[float] = None,
                      player_name: str = "Unknown"):
        """Update the entire display"""
        # Update layout components
        self.layout["header"].update(self.create_header(current_state, player_name, player_data))
        self.layout["left"]["status"].update(self.create_player_status(player_data))
        self.layout["left"]["combat"].update(self.create_combat_status(mob_data))
        self.layout["left"]["timers"].update(self.create_timers(attack_cooldown, heal_cooldown, rest_time))
        self.layout["right"]["stats"].update(self.create_stats_table())
        self.layout["messages"].update(self.create_messages_panel())
    
    def print_message(self, message: str, level: str = "info"):
        """Print a message with appropriate styling"""
        # Add to UI message history instead of printing to console
        self.add_message(message, level)
    
    def print_combat_log(self, attacker: str, target: str, damage: int, text: str = ""):
        """Print combat log entry"""
        if damage > 0:
            self.add_message(f"{attacker} → {target}: {damage} damage {text}", "info")
        else:
            self.add_message(f"{attacker} → {target}: Miss! {text}", "warning")
    
    def print_victory(self, mob_name: str, exp_gained: int, items: list):
        """Print victory message"""
        self.add_message(f"🎉 VICTORY! {mob_name} defeated!", "success")
        self.add_message(f"Experience gained: {exp_gained}", "success")
        if items:
            self.add_message(f"Items: {', '.join(items)}", "success")
    
    def print_healing(self, old_hp: int, new_hp: int, max_hp: int):
        """Print healing message"""
        self.add_message(f"💚 Healing potion used: {old_hp}/{max_hp} → {new_hp}/{max_hp}", "success")
    
    def print_rest_start(self, duration_minutes: int = 20):
        """Print rest start message"""
        self.add_message(f"🔥 Starting rest for {duration_minutes} minutes...", "warning")
    
    def print_rest_complete(self):
        """Print rest complete message"""
        self.add_message(f"✅ Rest complete! Stamina restored.", "success") 