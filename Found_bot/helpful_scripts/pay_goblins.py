import time
import requests
from Found_bot.config.token import GAME_TOKEN

BASE_URL = 'https://ruby-king.ru/api/resources/open-action'
REFERER = f'https://ruby-king.ru/city?name={GAME_TOKEN}&timeEnd=1751297651421'
HEADERS = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'ru,en;q=0.9,en-US;q=0.8,de;q=0.7',
    'Connection': 'keep-alive',
    'Content-Type': 'application/json',
    'Origin': 'https://ruby-king.ru',
    'Referer': REFERER,
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
}

def pay_goblins():
    for i in range(1, 15):
        action_id = f'action_{i}'
        data = {"actionId": action_id}
        params = {"name": GAME_TOKEN}
        response = requests.post(BASE_URL, headers=HEADERS, params=params, json=data)
        print(f"[action_{i}] Status: {response.status_code}, Response: {response.text}")
        time.sleep(2)

if __name__ == "__main__":
    pay_goblins() 