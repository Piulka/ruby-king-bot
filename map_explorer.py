#!/usr/bin/env python3
"""
Скрипт для полного картографирования всех локаций, направлений и квадратов
Записывает расположение всех мобов на всех квадратах в файл
"""

import json
import time
import logging
from typing import Dict, List, Optional, Tuple
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

# Импорты из нашего бота
from ruby_king_bot.api.client import APIClient
from ruby_king_bot.config.token import GAME_TOKEN
from ruby_king_bot.config.constants import LOCATION_NAMES, DIRECTION_NAMES

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('map_exploration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

console = Console()

class MapExplorer:
    def __init__(self):
        self.api_client = APIClient()
        self.token = GAME_TOKEN
        
        # Все локации и направления
        self.locations = [
            "loco_0", "loco_1", "loco_2", "loco_3", "loco_4", 
            "loco_5", "loco_6", "loco_7", "loco_8", "loco_9"
        ]
        self.directions = ["north", "south", "east", "west"]
        
        # Структура для хранения данных
        self.world_map = {}
        
        # Статистика
        self.stats = {
            'locations_visited': 0,
            'directions_visited': 0,
            'squares_visited': 0,
            'mobs_found': 0,
            'errors': 0
        }
    
    def explore_world(self):
        """Полное исследование мира"""
        console.print("[bold blue]🌍 Начинаем полное картографирование мира...[/bold blue]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            total_locations = len(self.locations)
            total_directions = len(self.directions)
            total_tasks = total_locations * total_directions
            
            main_task = progress.add_task(
                f"Исследуем {total_locations} локаций × {total_directions} направлений = {total_tasks} задач",
                total=total_tasks
            )
            
            for location in self.locations:
                location_name = LOCATION_NAMES.get(location, location)
                console.print(f"\n[bold green]📍 Исследуем локацию: {location_name} ({location})[/bold green]")
                
                self.world_map[location] = {
                    'name': location_name,
                    'directions': {}
                }
                
                for direction in self.directions:
                    direction_name = DIRECTION_NAMES.get(direction, direction)
                    console.print(f"  [yellow]🧭 Направление: {direction_name} ({direction})[/yellow]")
                    
                    try:
                        # Переходим в локацию и направление
                        change_geo_result = self._move_to_location_and_direction(location, direction)
                        
                        # Получаем данные о квадратах
                        squares_data = self._get_squares_data(change_geo_result)
                        
                        if squares_data:
                            self.world_map[location]['directions'][direction] = {
                                'name': direction_name,
                                'squares': self._process_squares_data(squares_data)
                            }
                            
                            self.stats['directions_visited'] += 1
                            self.stats['squares_visited'] += len(squares_data)
                            
                            console.print(f"    [green]✅ Найдено {len(squares_data)} квадратов[/green]")
                        else:
                            self.world_map[location]['directions'][direction] = {
                                'name': direction_name,
                                'squares': {},
                                'error': 'Нет данных о квадратах'
                            }
                            console.print(f"    [red]❌ Нет данных о квадратах[/red]")
                            self.stats['errors'] += 1
                    
                    except Exception as e:
                        logger.error(f"Ошибка при исследовании {location}/{direction}: {e}")
                        self.world_map[location]['directions'][direction] = {
                            'name': direction_name,
                            'squares': {},
                            'error': str(e)
                        }
                        self.stats['errors'] += 1
                        console.print(f"    [red]❌ Ошибка: {e}[/red]")
                    
                    progress.advance(main_task)
                    
                    # Задержка между направлениями
                    time.sleep(2)
                
                self.stats['locations_visited'] += 1
                
                # Сохраняем промежуточные результаты
                self._save_map_data()
                
                # Задержка между локациями
                time.sleep(5)
    
    def _move_to_location_and_direction(self, location: str, direction: str) -> dict:
        """Переход в локацию и направление и возвращает ответ change_geo"""
        result = self.api_client.change_geo(location, direction)
        if result.get("status") != "success":
            raise Exception(f"Не удалось перейти в {location}/{direction}: {result.get('message', 'Unknown error')}")
        time.sleep(3)
        return result

    def _get_squares_data(self, change_geo_result: dict) -> Optional[List[Dict]]:
        """Получение данных о квадратах из ответа change_geo"""
        return change_geo_result.get("squares", [])
    
    def _process_squares_data(self, squares_data: List[Dict]) -> Dict:
        """Обработка данных о квадратах"""
        processed_squares = {}
        
        for square_info in squares_data:
            position = square_info.get('position', '')
            lvl_mobs = square_info.get('lvlMobs', {})
            
            if position and lvl_mobs:
                processed_squares[position] = {
                    'mob_level': lvl_mobs.get('mobLvl', 'unknown'),
                    'mob_name': lvl_mobs.get('mobName', 'unknown'),
                    'mob_hp': lvl_mobs.get('mobHp', 0),
                    'mob_max_hp': lvl_mobs.get('mobMaxHp', 0),
                    'raw_data': lvl_mobs
                }
                
                self.stats['mobs_found'] += 1
        
        return processed_squares
    
    def _save_map_data(self):
        """Сохранение данных карты в файл"""
        output_file = 'world_map_data.json'
        
        data_to_save = {
            'metadata': {
                'created_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                'total_locations': len(self.locations),
                'total_directions': len(self.directions),
                'stats': self.stats
            },
            'world_map': self.world_map
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=2)
        
        console.print(f"[green]💾 Данные сохранены в {output_file}[/green]")
    
    def print_summary(self):
        """Вывод итоговой статистики"""
        console.print("\n[bold blue]📊 ИТОГОВАЯ СТАТИСТИКА КАРТИРОВАНИЯ[/bold blue]")
        
        table = Table(title="Результаты исследования")
        table.add_column("Метрика", style="cyan")
        table.add_column("Значение", style="magenta")
        
        table.add_row("Локаций исследовано", str(self.stats['locations_visited']))
        table.add_row("Направлений исследовано", str(self.stats['directions_visited']))
        table.add_row("Квадратов найдено", str(self.stats['squares_visited']))
        table.add_row("Мобов обнаружено", str(self.stats['mobs_found']))
        table.add_row("Ошибок", str(self.stats['errors']))
        
        console.print(table)
        
        # Подробная статистика по локациям
        console.print("\n[bold green]📍 ДЕТАЛЬНАЯ СТАТИСТИКА ПО ЛОКАЦИЯМ[/bold green]")
        
        for location, location_data in self.world_map.items():
            location_name = location_data['name']
            directions_count = len(location_data['directions'])
            total_squares = sum(len(direction_data.get('squares', {})) 
                              for direction_data in location_data['directions'].values())
            
            console.print(f"  {location_name} ({location}): {directions_count} направлений, {total_squares} квадратов")
    
    def create_readable_report(self):
        """Создание читаемого отчета"""
        report_file = 'world_map_report.md'
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# 🌍 КАРТА МИРА RUBY KING\n\n")
            f.write(f"*Создано: {time.strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
            
            f.write("## 📊 Статистика\n\n")
            f.write(f"- **Локаций исследовано:** {self.stats['locations_visited']}\n")
            f.write(f"- **Направлений исследовано:** {self.stats['directions_visited']}\n")
            f.write(f"- **Квадратов найдено:** {self.stats['squares_visited']}\n")
            f.write(f"- **Мобов обнаружено:** {self.stats['mobs_found']}\n")
            f.write(f"- **Ошибок:** {self.stats['errors']}\n\n")
            
            f.write("## 🗺️ Детальная карта\n\n")
            
            for location, location_data in self.world_map.items():
                location_name = location_data['name']
                f.write(f"### 📍 {location_name} ({location})\n\n")
                
                for direction, direction_data in location_data['directions'].items():
                    direction_name = direction_data['name']
                    squares = direction_data.get('squares', {})
                    
                    f.write(f"#### 🧭 {direction_name} ({direction})\n\n")
                    
                    if squares:
                        f.write("| Квадрат | Моб | Уровень | HP | Макс HP |\n")
                        f.write("|---------|-----|---------|----|---------|\n")
                        
                        for square, square_data in squares.items():
                            mob_name = square_data.get('mob_name', 'unknown')
                            mob_level = square_data.get('mob_level', 'unknown')
                            mob_hp = square_data.get('mob_hp', 0)
                            mob_max_hp = square_data.get('mob_max_hp', 0)
                            
                            f.write(f"| {square} | {mob_name} | {mob_level} | {mob_hp} | {mob_max_hp} |\n")
                    else:
                        error = direction_data.get('error', 'Нет данных')
                        f.write(f"*{error}*\n")
                    
                    f.write("\n")
                
                f.write("---\n\n")
        
        console.print(f"[green]📄 Читаемый отчет создан: {report_file}[/green]")


def main():
    """Главная функция"""
    console.print("[bold red]⚠️  ВНИМАНИЕ: Этот скрипт исследует ВСЕ локации и направления![/bold red]")
    console.print("[yellow]Это может занять значительное время и создать много API запросов.[/yellow]")
    
    response = input("\nПродолжить? (y/N): ").strip().lower()
    if response != 'y':
        console.print("[red]Операция отменена.[/red]")
        return
    
    try:
        explorer = MapExplorer()
        explorer.explore_world()
        explorer.print_summary()
        explorer.create_readable_report()
        
        console.print("\n[bold green]🎉 Картографирование завершено![/bold green]")
        console.print("[green]Файлы созданы:[/green]")
        console.print("  - world_map_data.json (структурированные данные)")
        console.print("  - world_map_report.md (читаемый отчет)")
        console.print("  - map_exploration.log (логи)")
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Операция прервана пользователем.[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Критическая ошибка: {e}[/red]")
        logger.error(f"Критическая ошибка: {e}")


if __name__ == "__main__":
    main() 