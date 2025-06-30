#!/usr/bin/env python3
"""
Скрипт для возврата в город
Использование: python3 return_to_city.py
"""

import sys
import os
import time

# Добавляем путь к модулям бота
sys.path.append(os.path.join(os.path.dirname(__file__), 'ruby_king_bot'))

from api.client import APIClient
from config.token import GAME_TOKEN

def return_to_city():
    """Возврат в город"""
    print("🏙️ Возвращаемся в город...")
    
    try:
        # Инициализируем API клиент
        api_client = APIClient()
        
        # Получаем информацию о текущем состоянии
        print("📊 Получаем информацию о текущем состоянии...")
        user_info = api_client.get_user_info()
        
        if user_info and 'user' in user_info:
            current_geo = user_info['user']['second'].get('geo', 'unknown')
            current_square = user_info['user']['second'].get('mySquare', 'unknown')
            print(f"📍 Текущая локация: {current_geo}, квадрат: {current_square}")
        
        # Переходим в город
        print("🏙️ Переходим в город...")
        result = api_client.change_main_geo("city")
        
        if result and result.get('status') == 'success':
            print("✅ Успешно вернулись в город!")
            
            # Получаем обновленную информацию
            time.sleep(1)
            user_info = api_client.get_user_info()
            if user_info and 'user' in user_info:
                new_geo = user_info['user']['second'].get('geo', 'unknown')
                new_square = user_info['user']['second'].get('mySquare', 'unknown')
                print(f"📍 Новая локация: {new_geo}, квадрат: {new_square}")
        else:
            print(f"❌ Ошибка возврата в город: {result}")
            return False
            
        print("✅ Скрипт завершен успешно!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Запуск скрипта возврата в город...")
    success = return_to_city()
    
    if success:
        print("🎉 Возврат в город выполнен успешно!")
    else:
        print("💥 Произошла ошибка при возврате в город!")
        sys.exit(1) 