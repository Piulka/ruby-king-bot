#!/usr/bin/env python3
"""
Low Damage Handler - обрабатывает ситуации с низким уроном
"""

import time
import logging
from typing import Dict, Any, List, Optional
from ..api.client import APIClient
from ..core.player import Player
from ..ui.display import GameDisplay

logger = logging.getLogger(__name__)

class LowDamageHandler:
    """Обработчик ситуаций с низким уроном"""
    
    def __init__(self, api_client: APIClient, player: Player, display: GameDisplay):
        self.api_client = api_client
        self.player = player
        self.display = display
        self.is_handling_low_damage = False
        
    def handle_low_damage_situation(self, current_target, mob_group, current_time: float) -> bool:
        """
        Обрабатывает ситуацию с низким уроном
        
        Returns:
            bool: True если обработка завершена, False если нужно продолжить
        """
        if self.is_handling_low_damage:
            return False
            
        self.is_handling_low_damage = True
        self.display.print_message("🔄 Запуск процедуры восстановления после низкого урона...", "warning")
        
        try:
            # 1. Добиваем оставшихся мобов
            self._finish_remaining_mobs(current_target, mob_group, current_time)
            
            # 2. Переходим на квадрат G4
            self._move_to_g4()
            
            # 3. Выходим в город
            self._return_to_city()
            
            # 4. Продаем все оружие, броню и украшения
            self._sell_equipment()
            
            # 5. Покупаем зелья до 300 каждого типа
            self._buy_potions()
            
            # 6. Возвращаемся на фарм и идем на лучший квадрат
            self._return_to_farm_and_move_to_best_square()
            
            self.display.print_message("✅ Процедура восстановления завершена! Возвращаемся к обычному фарму.", "success")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка в обработке низкого урона: {e}")
            self.display.print_message(f"❌ Ошибка в процедуре восстановления: {e}", "error")
            return False
        finally:
            self.is_handling_low_damage = False
    
    def _finish_remaining_mobs(self, current_target, mob_group, current_time: float):
        """Добиваем оставшихся мобов"""
        self.display.print_message("⚔️ Добиваем оставшихся мобов...", "info")
        
        # Продолжаем бой до победы
        while mob_group and not mob_group.is_empty():
            # Проверяем здоровье игрока
            if self.player.hp < 50 and self.player.can_use_heal_potion(current_time):
                # Используем API клиент напрямую для лечения
                try:
                    heal_result = self.api_client.use_healing_potion()
                    self.player.record_heal(current_time)
                    if "user" in heal_result:
                        self.player.update_from_api_response(heal_result)
                    self.display.print_message("❤️ Использовал зелье лечения!", "success")
                except Exception as e:
                    self.display.print_message(f"❌ Ошибка лечения: {e}", "error")
                time.sleep(1.1)
                continue
                
            # Атакуем мобов
            for mob in mob_group.get_all_mobs():
                if mob.hp > 0:
                    try:
                        attack_result = self.api_client.attack_mob(mob.farm_id)
                        self.player.record_attack(current_time)
                        
                        # Обновляем данные игрока
                        if "user" in attack_result:
                            self.player.update_from_api_response(attack_result)
                        
                        if isinstance(attack_result, dict):
                            if attack_result.get('status') == 'success':
                                # Обновляем данные моба
                                if 'mob' in attack_result:
                                    mob.update_from_api_response(attack_result['mob'])
                                
                                # Проверяем победу
                                if attack_result.get('dataWin'):
                                    self.display.print_message("🎉 Победа!", "success")
                                    break
                            elif attack_result.get('status') == 'fail':
                                self.display.print_message(f"❌ Атака провалена: {attack_result.get('message', '')}", "error")
                    except Exception as e:
                        self.display.print_message(f"❌ Ошибка атаки: {e}", "error")
                    time.sleep(1.1)
            
            # Обновляем время
            current_time = time.time()
        
        self.display.print_message("✅ Все мобы добиты!", "success")
    
    def _move_to_g4(self):
        """Переходим на квадрат G4"""
        self.display.print_message("📍 Переходим на квадрат G4...", "info")
        
        try:
            result = self.api_client.change_square("G4")
            
            if result.get("status") == "success":
                self.display.print_message("✅ Переход на G4 успешен", "success")
            else:
                self.display.print_message(f"❌ Ошибка перехода на G4: {result.get('message', 'Неизвестная ошибка')}", "error")
                
        except Exception as e:
            logger.error(f"Ошибка перехода на G4: {e}")
            self.display.print_message(f"❌ Ошибка перехода на G4: {e}", "error")
        
        time.sleep(2)
    
    def _return_to_city(self):
        """Возвращаемся в город"""
        self.display.print_message("🏙️ Возвращаемся в город...", "info")
        
        try:
            result = self.api_client.change_main_geo("city")
            
            if result.get("status") == "success":
                self.display.print_message("✅ Возврат в город успешен", "success")
                self.display.update_stats(city_visits=1)
            else:
                self.display.print_message(f"❌ Ошибка возврата в город: {result.get('message', 'Неизвестная ошибка')}", "error")
                
        except Exception as e:
            logger.error(f"Ошибка возврата в город: {e}")
            self.display.print_message(f"❌ Ошибка возврата в город: {e}", "error")
        
        time.sleep(2)
    
    def _sell_equipment(self):
        """Продаем все оружие, броню и украшения"""
        self.display.print_message("💰 Продаем оружие, броню и украшения...", "info")
        
        try:
            # Получаем информацию о предметах
            user_info = self.api_client.get_user_info()
            inventory = user_info.get("inventory", [])
            
            # Фильтруем предметы для продажи
            items_to_sell = []
            for item in inventory:
                item_id = item.get("id", "")
                item_type = item.get("typeElement", "")
                
                # Продаем оружие, броню и украшения
                if (item_type in ["weapon", "armor", "jewelry"] or 
                    "weapon" in item_id or "armor" in item_id or "jewelry" in item_id):
                    items_to_sell.append(item_id)
            
            if items_to_sell:
                # Продаем предметы
                result = self.api_client.sell_items(items_to_sell)
                gold_earned = 0
                if result.get("status") == "success":
                    # Суммируем золото с продажи (обычно id == 'm_0_1')
                    for item in result.get('drop', []):
                        if item.get('id') == 'm_0_1':
                            gold_earned += item.get('count', 0)
                    self.display.print_message(f"✅ Продано {len(items_to_sell)} предметов", "success")
                    self.display.update_stats(items_sold=len(items_to_sell), gold_from_sales=gold_earned)
                else:
                    self.display.print_message(f"❌ Ошибка продажи: {result.get('message', 'Неизвестная ошибка')}", "error")
            else:
                self.display.print_message("ℹ️ Нет предметов для продажи", "info")
                
        except Exception as e:
            logger.error(f"Ошибка продажи предметов: {e}")
            self.display.print_message(f"❌ Ошибка продажи предметов: {e}", "error")
        
        time.sleep(2)
    
    def _buy_potions(self):
        """Покупаем зелья до 300 каждого типа"""
        self.display.print_message("🧪 Проверяем и покупаем зелья...", "info")
        
        try:
            # Получаем информацию о предметах
            user_info = self.api_client.get_user_info()
            inventory = user_info.get("inventory", [])
            
            # Считаем текущие зелья
            hp_potions = 0
            mana_potions = 0
            
            for item in inventory:
                item_id = item.get("id", "")
                count = item.get("count", 0)
                
                if item_id == "m_1":  # Зелье здоровья
                    hp_potions = count
                elif item_id == "m_3":  # Зелье маны
                    mana_potions = count
            
            # Покупаем зелья здоровья
            if hp_potions < 300:
                hp_to_buy = 300 - hp_potions
                result = self.api_client.buy_items("m_1", hp_to_buy)
                
                if result.get("status") == "success":
                    self.display.print_message(f"✅ Куплено {hp_to_buy} зелий здоровья", "success")
                else:
                    self.display.print_message(f"❌ Ошибка покупки зелий здоровья: {result.get('message', 'Неизвестная ошибка')}", "error")
            else:
                self.display.print_message(f"ℹ️ Зелий здоровья достаточно: {hp_potions}", "info")
            
            # Покупаем зелья маны
            if mana_potions < 300:
                mana_to_buy = 300 - mana_potions
                result = self.api_client.buy_items("m_3", mana_to_buy)
                
                if result.get("status") == "success":
                    self.display.print_message(f"✅ Куплено {mana_to_buy} зелий маны", "success")
                else:
                    self.display.print_message(f"❌ Ошибка покупки зелий маны: {result.get('message', 'Неизвестная ошибка')}", "error")
            else:
                self.display.print_message(f"ℹ️ Зелий маны достаточно: {mana_potions}", "info")
                
        except Exception as e:
            logger.error(f"Ошибка покупки зелий: {e}")
            self.display.print_message(f"❌ Ошибка покупки зелий: {e}", "error")
        
        time.sleep(2)
    
    def _return_to_farm_and_move_to_best_square(self):
        """Возвращаемся на фарм и идем на лучший квадрат"""
        self.display.print_message("🌾 Возвращаемся на фарм...", "info")
        
        try:
            # Переходим в ферму
            result = self.api_client.change_main_geo("farm")
            
            if result.get("status") != "success":
                self.display.print_message(f"❌ Ошибка перехода в ферму: {result.get('message', 'Неизвестная ошибка')}", "error")
                return
            
            time.sleep(2)
            
            # Переходим в локацию loco_3 на юг
            result = self.api_client.change_geo("loco_3", "south")
            
            if result.get("status") != "success":
                self.display.print_message(f"❌ Ошибка перехода в локацию: {result.get('message', 'Неизвестная ошибка')}", "error")
                return
            
            # Анализируем карту и находим лучший квадрат
            squares = result.get("squares", [])
            best_square = self._find_best_square(squares)
            
            if best_square:
                time.sleep(2)
                
                # Переходим на лучший квадрат
                result = self.api_client.change_square(best_square)
                
                if result.get("status") == "success":
                    self.display.print_message(f"✅ Переход на лучший квадрат {best_square} успешен", "success")
                else:
                    self.display.print_message(f"❌ Ошибка перехода на квадрат {best_square}: {result.get('message', 'Неизвестная ошибка')}", "error")
            else:
                self.display.print_message("❌ Не найден подходящий квадрат", "error")
                
        except Exception as e:
            logger.error(f"Ошибка возврата на фарм: {e}")
            self.display.print_message(f"❌ Ошибка возврата на фарм: {e}", "error")
    
    def _find_best_square(self, squares: List[Dict[str, Any]]) -> Optional[str]:
        """Находит лучший квадрат для текущего уровня"""
        player_level = self.player.level
        best_square = None
        best_score = -1
        
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
                
                if score > best_score:
                    best_score = score
                    best_square = position
        
        return best_square 