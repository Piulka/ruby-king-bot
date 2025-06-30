import time
import requests
import json
import sys
from Found_bot.config.token import GAME_TOKEN  # токен хранится в переменной GAME_TOKEN

# --- Константы ---
BASE_URL = 'https://ruby-king.ru/api'
NAME = '1750764015078_145327_6700_95b44b31447fdc4c593251e276531049ed0c51d9f73ae0c50bec'
HEADERS = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'ru,en;q=0.9,en-US;q=0.8,de;q=0.7',
    'Connection': 'keep-alive',
    'Content-Type': 'application/json',
    'Origin': 'https://ruby-king.ru',
    'Referer': f'https://ruby-king.ru/city?name={NAME}&timeEnd=1751300208114',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
    'Authorization': f'Bearer {GAME_TOKEN}'
}

# --- Запросы ---
def main():
    session = requests.Session()
    session.headers.update(HEADERS)

    # 1. change-main-geo
    print('1. change-main-geo...')
    resp1 = session.post(f'{BASE_URL}/farm/change-main-geo?name={NAME}', json={"position": "farm"})
    print(f'Ответ: {resp1.status_code}')
    time.sleep(2)

    # 2. change-geo
    print('2. change-geo...')
    resp2 = session.post(f'{BASE_URL}/farm/change-geo?name={NAME}', json={"loco": "loco_2", "direction": "north", "typeAction": "change"})
    print(f'Ответ: {resp2.status_code}')
    time.sleep(2)

    # 3. farm-mob-one
    print('3. farm-mob-one...')
    resp3 = session.post(f'{BASE_URL}/farm/farm-mob-one?name={NAME}', json={"loco": "loco_2", "direction": "north"})
    print(f'Ответ: {resp3.status_code}')

    # --- Вывод результата ---
    try:
        data = resp3.json()
        print('\nКого нашёл:')
        print(json.dumps(data, ensure_ascii=False, indent=2))
    except Exception as e:
        print('Ошибка при разборе ответа:', e)
        print(resp3.text)

if __name__ == '__main__':
    main() 