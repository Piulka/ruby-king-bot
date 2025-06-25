#!/usr/bin/env python3
"""
Тест: переход в ферму -> огненный кратер -> лучший квадрат -> исследование
"""

import requests
import json
import time

# Конфигурация
GAME_TOKEN = "1750764015078_145327_6700_95b44b31447fdc4c593251e276531049ed0c51d9f73ae0c50bec"
base_url = "https://ruby-king.ru/api"
player_level = 14  # Уровень персонажа

# Заголовки из curl запроса
headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'ru,en;q=0.9,en-US;q=0.8,de;q=0.7',
    'Connection': 'keep-alive',
    'Content-Type': 'application/json',
    'Origin': 'https://ruby-king.ru',
    'Referer': f'https://ruby-king.ru/city?name={GAME_TOKEN}',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"'
}

print("🧪 Тест: переход в ферму -> огненный кратер -> лучший квадрат -> исследование")
print("=" * 70)
print(f"🔑 Используется токен: {GAME_TOKEN[:20]}...")
print(f"👤 Уровень персонажа: {player_level}")

# Шаг 1: Переход в ферму
print(f"\n🌾 Шаг 1: Переход в ферму")
try:
    start_time = time.time()
    data = {"position": "farm"}
    response = requests.post(
        f"{base_url}/farm/change-main-geo?name={GAME_TOKEN}",
        headers=headers,
        json=data,
        timeout=10
    )
    end_time = time.time()
    request_time = end_time - start_time
    print(f"⏱️  Время запроса: {request_time:.3f} сек")
    print(f"📡 Статус ответа: {response.status_code}")
    if response.status_code == 200:
        try:
            response_data = response.json()
            print(f"📋 Ответ: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
            
            if "status" in response_data:
                if response_data["status"] == "success":
                    print(f"✅ Переход в ферму успешен")
                else:
                    print(f"❌ Переход не удался: {response_data.get('message', 'Неизвестная ошибка')}")
            else:
                print(f"⚠️  Неожиданный формат ответа")
                
        except json.JSONDecodeError:
            print(f"⚠️  Не удалось распарсить JSON ответ")
            print(f"📄 Текст ответа: {response.text}")
    else:
        print(f"❌ HTTP ошибка: {response.status_code}")
        print(f"📄 Текст ответа: {response.text}")
except requests.exceptions.Timeout:
    print(f"⏰ Таймаут запроса (>10 сек)")
except requests.exceptions.RequestException as e:
    print(f"❌ Ошибка запроса: {e}")

# Пауза 5 секунд
print(f"\n⏳ Пауза 5 секунд...")
time.sleep(5)

# Шаг 2: Переход в локацию огненный кратер на юг
print(f"\n🔥 Шаг 2: Переход в локацию огненный кратер на юг")
try:
    start_time = time.time()
    data = {"loco": "loco_3", "direction": "south", "typeAction": "change"}
    response = requests.post(
        f"{base_url}/farm/change-geo?name={GAME_TOKEN}",
        headers=headers,
        json=data,
        timeout=10
    )
    end_time = time.time()
    request_time = end_time - start_time
    print(f"⏱️  Время запроса: {request_time:.3f} сек")
    print(f"📡 Статус ответа: {response.status_code}")
    if response.status_code == 200:
        try:
            response_data = response.json()
            print(f"📋 Ответ: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
            
            if "status" in response_data:
                if response_data["status"] == "success":
                    print(f"✅ Переход в локацию успешен")
                    
                    # Анализируем карту и находим лучший квадрат
                    if "squares" in response_data:
                        squares = response_data["squares"]
                        best_square = None
                        best_score = -1
                        
                        print(f"\n🔍 Анализ карты для уровня {player_level}:")
                        for square in squares:
                            position = square.get("position")
                            lvl_mobs = square.get("lvlMobs")
                            
                            if lvl_mobs and "mobLvl" in lvl_mobs:
                                mob_level = lvl_mobs["mobLvl"]
                                # Вычисляем "идеальность" квадрата (близость к уровню игрока)
                                score = 100 - abs(mob_level - player_level)
                                
                                # Бонус за точное совпадение
                                if mob_level == player_level:
                                    score += 50
                                
                                # Бонус за специальные локации
                                if "locoName" in lvl_mobs:
                                    score += 10
                                    print(f"  {position}: мобы уровня {mob_level} ({lvl_mobs['locoName']}) - оценка: {score}")
                                else:
                                    print(f"  {position}: мобы уровня {mob_level} - оценка: {score}")
                                
                                if score > best_score:
                                    best_score = score
                                    best_square = position
                            else:
                                print(f"  {position}: нет мобов")
                        
                        if best_square:
                            print(f"\n🎯 Лучший квадрат: {best_square} (оценка: {best_score})")
                            
                            # Пауза 5 секунд перед переходом на лучший квадрат
                            print(f"\n⏳ Пауза 5 секунд...")
                            time.sleep(5)
                            
                            # Шаг 3: Переход на лучший квадрат
                            print(f"\n🎯 Шаг 3: Переход на квадрат {best_square}")
                            data_square = {"square": best_square}
                            try:
                                start_time = time.time()
                                response = requests.post(
                                    f"{base_url}/farm/change-square?name={GAME_TOKEN}",
                                    headers=headers,
                                    json=data_square,
                                    timeout=10
                                )
                                end_time = time.time()
                                request_time = end_time - start_time
                                print(f"⏱️  Время запроса: {request_time:.3f} сек")
                                print(f"📡 Статус ответа: {response.status_code}")
                                if response.status_code == 200:
                                    try:
                                        response_data = response.json()
                                        print(f"📋 Ответ: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
                                        
                                        if "status" in response_data:
                                            if response_data["status"] == "success":
                                                print(f"✅ Переход на {best_square} успешен")
                                                
                                                # Пауза 2 секунды перед исследованием
                                                print(f"\n⏳ Пауза 2 секунды...")
                                                time.sleep(2)
                                                
                                                # Шаг 4: Исследование территории
                                                print(f"\n🔍 Шаг 4: Исследование территории")
                                                
                                                # Определяем параметры для исследования
                                                explore_loco = ""
                                                explore_direction = ""
                                                
                                                # Если мы в подлокации, используем её ID
                                                if "innerLoco" in response_data and response_data["innerLoco"]:
                                                    explore_loco = response_data["innerLoco"]
                                                    explore_direction = "south"
                                                    print(f"📍 Исследуем подлокацию: {explore_loco}")
                                                else:
                                                    # Для обычного квадрата используем основную локацию
                                                    explore_loco = "loco_3"
                                                    explore_direction = "south"
                                                    print(f"📍 Исследуем обычный квадрат в локации {explore_loco}")
                                                
                                                try:
                                                    start_time = time.time()
                                                    data_explore = {
                                                        "loco": explore_loco,
                                                        "direction": explore_direction
                                                    }
                                                    response = requests.post(
                                                        f"{base_url}/farm/farm-mob-one?name={GAME_TOKEN}",
                                                        headers=headers,
                                                        json=data_explore,
                                                        timeout=10
                                                    )
                                                    end_time = time.time()
                                                    request_time = end_time - start_time
                                                    print(f"⏱️  Время запроса: {request_time:.3f} сек")
                                                    print(f"📡 Статус ответа: {response.status_code}")
                                                    if response.status_code == 200:
                                                        try:
                                                            response_data = response.json()
                                                            print(f"📋 Ответ: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
                                                            
                                                            if "status" in response_data:
                                                                if response_data["status"] == "success":
                                                                    print(f"✅ Исследование успешно завершено")
                                                                    if "mob" in response_data:
                                                                        print(f"🎯 Найден моб!")
                                                                    elif "message" in response_data:
                                                                        print(f"📝 Сообщение: {response_data['message']}")
                                                                else:
                                                                    print(f"❌ Исследование не удалось: {response_data.get('message', 'Неизвестная ошибка')}")
                                                            else:
                                                                print(f"⚠️  Неожиданный формат ответа")
                                                                
                                                        except json.JSONDecodeError:
                                                            print(f"⚠️  Не удалось распарсить JSON ответ")
                                                            print(f"📄 Текст ответа: {response.text}")
                                                    else:
                                                        print(f"❌ HTTP ошибка: {response.status_code}")
                                                        print(f"📄 Текст ответа: {response.text}")
                                                except requests.exceptions.Timeout:
                                                    print(f"⏰ Таймаут запроса (>10 сек)")
                                                except requests.exceptions.RequestException as e:
                                                    print(f"❌ Ошибка запроса: {e}")
                                                
                                            else:
                                                print(f"❌ Переход не удался: {response_data.get('message', 'Неизвестная ошибка')}")
                                        else:
                                            print(f"⚠️  Неожиданный формат ответа")
                                            
                                    except json.JSONDecodeError:
                                        print(f"⚠️  Не удалось распарсить JSON ответ")
                                        print(f"📄 Текст ответа: {response.text}")
                                else:
                                    print(f"❌ HTTP ошибка: {response.status_code}")
                                    print(f"📄 Текст ответа: {response.text}")
                            except requests.exceptions.Timeout:
                                print(f"⏰ Таймаут запроса (>10 сек)")
                            except requests.exceptions.RequestException as e:
                                print(f"❌ Ошибка запроса: {e}")
                        else:
                            print(f"❌ Не найден подходящий квадрат")
                else:
                    print(f"❌ Переход не удался: {response_data.get('message', 'Неизвестная ошибка')}")
            else:
                print(f"⚠️  Неожиданный формат ответа")
                
        except json.JSONDecodeError:
            print(f"⚠️  Не удалось распарсить JSON ответ")
            print(f"📄 Текст ответа: {response.text}")
    else:
        print(f"❌ HTTP ошибка: {response.status_code}")
        print(f"📄 Текст ответа: {response.text}")
except requests.exceptions.Timeout:
    print(f"⏰ Таймаут запроса (>10 сек)")
except requests.exceptions.RequestException as e:
    print(f"❌ Ошибка запроса: {e}")

print("\n🏁 Тест завершён") 