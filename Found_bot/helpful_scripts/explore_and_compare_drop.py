import sys
import os
import json
from typing import List, Dict
from Found_bot.api.client import APIClient
from Found_bot.utils.item_database import get_item_name

# Для парсинга HTML
from bs4 import BeautifulSoup
from rich.console import Console
from rich.table import Table

# --- Настройки ---
# Здесь можно указать путь к тестовому HTML с фронта
HTML_PATH = "test_mob_profile_modal.html"

# --- Функция для парсинга дропа из DOM ---
def parse_mob_drop_from_dom(html: str) -> List[Dict]:
    soup = BeautifulSoup(html, "html.parser")
    drop_block = soup.find("div", class_="mob-profile-modal_Items__fhnt6")
    items = []
    if not drop_block:
        return items
    for cell in drop_block.find_all("div", class_="cell-item-res_Cell__Qw3Oq"):
        img = cell.find("img", class_="cell-item-res_IconOriginal__X9o_Y")
        if not img:
            continue
        src = img["src"]
        # Парсим реальный url картинки из параметра url= (если есть)
        real_url = src
        import urllib.parse
        if "url=" in src:
            url_match = src.split("url=")[-1].split("&")[0]
            real_url = urllib.parse.unquote(url_match)
        # Теперь real_url типа https://i.ibb.co/p0dDzKW/res-25.jpg
        file = real_url.split("/")[-1].split(".")[0]  # res-25, m-0-2, res-a-5
        item_id = file.replace("-", "_")
        name = img.get("alt", item_id)
        items.append({
            "id": item_id,
            "name": name,
            "avatar": real_url
        })
    return items

# --- Функция для получения дропа из API ---
def get_api_drop(api_drop: List[Dict]) -> Dict[str, Dict]:
    result = {}
    for item in api_drop:
        item_id = item.get("id", "")
        result[item_id] = {
            "id": item_id,
            "type": item.get("typeElement", ""),
            "chance": item.get("chance", "?"),
            "count": item.get("count", 1),
            "name": get_item_name(item_id)
        }
    return result

# --- Основной тест ---
def main():
    # 1. Получаем ответ API (эмулируем или делаем реальный запрос)
    api_client = APIClient()
    print("[1] Исследование...")
    api_response = api_client.explore_territory()
    if not api_response or "mob" not in api_response:
        print("Моб не найден в ответе API!")
        return
    mob = api_response["mob"] if isinstance(api_response["mob"], dict) else api_response["mob"][0]
    api_drop = mob.get("drop", [])
    api_drop_map = get_api_drop(api_drop)

    # 2. Читаем HTML с фронта (эмулируем)
    if not os.path.exists(HTML_PATH):
        print(f"HTML файл {HTML_PATH} не найден! Сохраните DOM моба в этот файл.")
        return
    with open(HTML_PATH, "r", encoding="utf-8") as f:
        html = f.read()
    dom_drop = parse_mob_drop_from_dom(html)

    # 3. Сравниваем и выводим таблицу
    console = Console()
    table = Table(title="Сравнение дропа моба (API vs DOM)")
    table.add_column("Аватарка", justify="center")
    table.add_column("Название (DOM)")
    table.add_column("ID")
    table.add_column("Шанс (API)")
    table.add_column("Тип (API)")

    for item in dom_drop:
        item_id = item["id"]
        api_info = api_drop_map.get(item_id, {})
        avatar = item["avatar"]
        name = item["name"]
        chance = str(api_info.get("chance", "?"))
        type_ = api_info.get("type", "?")
        table.add_row(f"[link={avatar}]img[/link]", name, item_id, chance, type_)

    console.print(table)

if __name__ == "__main__":
    main() 