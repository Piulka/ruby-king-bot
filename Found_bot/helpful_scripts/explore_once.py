import sys
import os
from rich.console import Console
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.client import APIClient
from ui.display import GameDisplay
from logic.exploration_handler import ExplorationHandler

console = Console()

def main():
    api_client = APIClient()
    display = GameDisplay()
    explorer = ExplorationHandler(api_client, display)
    result = explorer.explore_territory()
    console.print("[bold green]Результат исследования:[/bold green]")
    console.print(result)
    # Краткий анализ
    if not result:
        console.print("[red]Исследование не дало результата[/red]")
        return
    found = []
    if 'mob' in result and result['mob']:
        found.append(f"Мобы: {len(result['mob']) if isinstance(result['mob'], list) else 1}")
    if 'event' in result and result['event']:
        found.append(f"События: {result['event']}")
    if 'drop' in result and result['drop']:
        found.append(f"Дроп: {result['drop']}")
    if 'logs' in result and result['logs']:
        found.append(f"Логи: {len(result['logs'])}")
    if found:
        console.print("[bold yellow]Найдено при исследовании:[/bold yellow] " + ", ".join(found))
    else:
        console.print("[yellow]Ничего особенного не найдено[/yellow]")

if __name__ == "__main__":
    main() 