#!/usr/bin/env python3
import time
import json
import sys
import os
from datetime import datetime

# Добавляем путь к модулям бота
sys.path.append('ruby_king_bot')

from api.client import APIClient
from config.token import GAME_TOKEN
# from ui.display import Display  # Не нужен для теста

class HPotionCooldownTester:
    def __init__(self):
        self.api_client = APIClient()
        # self.display = Display()  # Не нужен для теста
        self.potion_timestamps = []
        self.successful_potions = 0
        self.failed_potions = 0
    
    def log_potion_attempt(self, timestamp, success, response):
        status = "SUCCESS" if success else "FAILED"
        print(f"[{datetime.fromtimestamp(timestamp/1000).strftime('%H:%M:%S.%f')[:-3]}] "
              f"HP_POTION {status}: {response.get('message', 'Unknown')}")
        if success:
            self.potion_timestamps.append(timestamp)
            self.successful_potions += 1
            print(f"✅ Successful potions: {self.successful_potions}")
        else:
            self.failed_potions += 1
            print(f"❌ Failed potions: {self.failed_potions}")
    
    def test_hp_potion_cooldown(self, max_potions=5):
        print(f"🔴 Starting HP potion cooldown test (target: {max_potions} successful potions)")
        print("=" * 60)
        
        last_potion_time = None
        
        while self.successful_potions < max_potions:
            try:
                # Пытаемся использовать банку HP
                result = self.api_client.use_healing_potion()
                current_time = int(time.time() * 1000)
                
                # Определяем успешность использования банки
                success = (result.get('status') == 'success' and 
                          'message' in result and 'успешно' in result['message'])
                
                # Логируем попытку
                self.log_potion_attempt(current_time, success, result)
                
                # Если банка успешна, считаем время от предыдущей
                if success and last_potion_time:
                    cooldown = (current_time - last_potion_time) / 1000
                    print(f"⏱️  Cooldown from last potion: {cooldown:.2f} seconds")
                
                if success:
                    last_potion_time = current_time
                
                # Пауза между попытками
                time.sleep(1)
                
            except Exception as e:
                print(f"❌ Potion attempt failed: {e}")
                time.sleep(1)
        
        self.print_cooldown_analysis()
    
    def print_cooldown_analysis(self):
        print("\n" + "=" * 60)
        print("📊 HP POTION COOLDOWN ANALYSIS")
        print("=" * 60)
        
        if len(self.potion_timestamps) < 2:
            print("❌ Not enough data for analysis")
            return
        
        # Вычисляем разницы между банками
        cooldowns = []
        for i in range(1, len(self.potion_timestamps)):
            cooldown = (self.potion_timestamps[i] - self.potion_timestamps[i-1]) / 1000
            cooldowns.append(cooldown)
        
        print(f"🎯 Total successful potions: {self.successful_potions}")
        print(f"❌ Total failed potions: {self.failed_potions}")
        print(f"📈 Cooldown analysis:")
        print(f"   Min: {min(cooldowns):.2f} seconds")
        print(f"   Max: {max(cooldowns):.2f} seconds")
        print(f"   Avg: {sum(cooldowns)/len(cooldowns):.2f} seconds")
        
        print(f"\n📋 Detailed cooldowns:")
        for i, cooldown in enumerate(cooldowns, 1):
            print(f"   Potion {i} → {i+1}: {cooldown:.2f}s")
        
        # Рекомендуемый КД
        recommended_cd = max(cooldowns) + 0.1  # Добавляем небольшой запас
        print(f"\n💡 Recommended cooldown: {recommended_cd:.2f} seconds")

def main():
    print("🚀 HP Potion Cooldown Tester")
    print("This script will test the exact cooldown for HP potions")
    print("=" * 60)
    tester = HPotionCooldownTester()
    tester.test_hp_potion_cooldown(max_potions=5)

if __name__ == "__main__":
    main() 