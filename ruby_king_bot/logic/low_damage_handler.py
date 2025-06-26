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
        
    def handle_low_damage_situation(self, current_target, mob_group, current_time: float, situation_type: str = "low_damage") -> bool:
        """
        Обрабатывает ситуацию с низким уроном или малым количеством зелий
        
        Args:
            current_target: Текущая цель
            mob_group: Группа мобов
            current_time: Текущее время
            situation_type: Тип ситуации ("low_damage" или "low_potions")
        
        Returns:
            bool: True если обработка завершена, False если нужно продолжить
        """
        if self.is_handling_low_damage:
            return False
            
        self.is_handling_low_damage = True
        
        if situation_type == "low_potions":
            self.display.print_message("🔄 Запуск процедуры восстановления из-за малого количества зелий...", "warning")
        else:
            self.display.print_message("🔄 Запуск процедуры восстановления после низкого урона...", "warning")
        
        try:
            self.display.print_message("➡️ Этап 1: Завершение боя (пропускаем добивание)", "info")
            # 1. Не добиваем оставшихся мобов, сразу идём дальше
            # self._finish_remaining_mobs(current_target, mob_group, current_time)  # Убираем добивание
            
            self.display.print_message("➡️ Этап 2: Переход на квадрат G4", "info")
            self._move_to_g4()
            time.sleep(2)  # Пауза 2 секунды
            self._force_display_update()  # Принудительное обновление дисплея
            
            self.display.print_message("➡️ Этап 3: Сброс локации", "info")
            self._reset_location()
            time.sleep(2)  # Пауза 2 секунды
            self._force_display_update()  # Принудительное обновление дисплея
            
            self.display.print_message("➡️ Этап 4: Возврат в город", "info")
            self._return_to_city()
            time.sleep(2)  # Пауза 2 секунды
            self._force_display_update()  # Принудительное обновление дисплея
            
            self.display.print_message("➡️ Этап 5: Продажа предметов", "info")
            self._sell_equipment(self.player)
            time.sleep(2)  # Пауза 2 секунды
            self._force_display_update()  # Принудительное обновление дисплея
            
            self.display.print_message("➡️ Этап 6: Покупка зелий", "info")
            self._buy_potions()
            time.sleep(2)  # Пауза 2 секунды
            self._force_display_update()  # Принудительное обновление дисплея
            
            self.display.print_message("➡️ Этап 7: Переход в фарм зону", "info")
            self._go_to_farm_zone()
            time.sleep(2)  # Пауза 2 секунды
            self._force_display_update()  # Принудительное обновление дисплея
            
            self.display.print_message("➡️ Этап 8: Переход на локацию", "info")
            self._go_to_location()
            time.sleep(2)  # Пауза 2 секунды
            self._force_display_update()  # Принудительное обновление дисплея
            
            self.display.print_message("➡️ Этап 9: Переход на подходящий квадрат", "info")
            self._go_to_best_square()
            
            if situation_type == "low_potions":
                self.display.print_message("✅ Процедура восстановления зелий завершена! Возвращаемся к обычному фарму.", "success")
            else:
                self.display.print_message("✅ Процедура восстановления завершена! Возвращаемся к обычному фарму.", "success")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка в обработке ситуации: {e}")
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
    
    def _sell_equipment(self, player: Player) -> bool:
        """Продать все оружие, броню и бижутерию из инвентаря (не надетые)"""
        try:
            user_info = self.api_client.get_user_info()
            if not user_info or 'user' not in user_info or 'inventory' not in user_info['user']:
                logger.error("Не удалось получить информацию о предметах")
                return False
            inventory = user_info['user']['inventory']
            logger.info(f"Получен инвентарь: {len(inventory)} предметов")
            items_to_sell = []
            for item_id, item_data in inventory.items():
                item_type = item_data.get('typeElement', '')
                item_position = item_data.get('position', '')
                # Продаем только вещи из инвентаря, не надетые
                if (item_type in ['weapons', 'armors', 'jewelry'] and 
                    item_position == 'inventory'):
                    unique_id = item_data.get('uniqueId')
                    if unique_id:
                        items_to_sell.append({"id": unique_id, "count": 1})
                        logger.info(f"Добавлен к продаже: {unique_id} ({item_type}) - из инвентаря")
                elif item_type in ['weapons', 'armors', 'jewelry'] and item_position == 'onBody':
                    logger.info(f"Пропускаем надетый предмет: {item_data.get('uniqueId')} ({item_type}) - надет")
            if not items_to_sell:
                logger.info("Нет предметов для продажи в инвентаре")
                return True
            logger.info(f"Продаём {len(items_to_sell)} предметов из инвентаря: {items_to_sell}")
            sell_result = self.api_client.sell_items(items_to_sell)
            logger.info(f"Результат продажи: {sell_result}")
            if sell_result and sell_result.get('status') == 'success':
                gold_earned = sell_result.get('goldEarned', 0)
                self.display.update_stats(gold_earned=gold_earned)
                logger.info(f"Продано {len(items_to_sell)} предметов, заработано {gold_earned} золота")
                return True
            else:
                logger.error(f"Ошибка продажи: {sell_result}")
                return False
        except Exception as e:
            logger.error(f"Ошибка при продаже предметов: {e}")
            return False
    
    def _buy_potions(self):
        """Купить зелья лечения и маны до лимита 300"""
        try:
            user_info = self.api_client.get_user_info()
            if not user_info or 'user' not in user_info or 'inventory' not in user_info['user']:
                logger.error("Не удалось получить информацию о зельях")
                return False
            inventory = user_info['user']['inventory']
            logger.info(f"Получен инвентарь для покупки зелий: {len(inventory)} предметов")
            heal_potions = 0
            mana_potions = 0
            for item_id, item_data in inventory.items():
                item_count = item_data.get('count', 0)
                if item_id == 'm_1':
                    heal_potions = item_count
                    logger.info(f"Найдено зелий лечения: {heal_potions}")
                elif item_id == 'm_3':
                    mana_potions = item_count
                    logger.info(f"Найдено зелий маны: {mana_potions}")
            potions_bought = 0
            if heal_potions < 300:
                to_buy = 300 - heal_potions
                logger.info(f"Покупаем {to_buy} зелий лечения")
                heal_result = self.api_client.buy_items('m_1', 'resources', to_buy)
                logger.info(f"Результат покупки зелий лечения: {heal_result}")
                if heal_result and heal_result.get('status') == 'success':
                    potions_bought += to_buy
                    self.display.update_stats(potions_used=to_buy)
                    logger.info(f"Куплено {to_buy} зелий лечения")
                else:
                    logger.error(f"Ошибка покупки зелий лечения: {heal_result}")
            if mana_potions < 300:
                to_buy = 300 - mana_potions
                logger.info(f"Покупаем {to_buy} зелий маны")
                mana_result = self.api_client.buy_items('m_3', 'resources', to_buy)
                logger.info(f"Результат покупки зелий маны: {mana_result}")
                if mana_result and mana_result.get('status') == 'success':
                    potions_bought += to_buy
                    self.display.update_stats(potions_used=to_buy)
                    logger.info(f"Куплено {to_buy} зелий маны")
                else:
                    logger.error(f"Ошибка покупки зелий маны: {mana_result}")
            if potions_bought > 0:
                logger.info(f"Всего куплено зелий: {potions_bought}")
                return True
            else:
                logger.info("Зелья не покупались (достаточно в инвентаре)")
                return True
        except Exception as e:
            logger.error(f"Ошибка при покупке зелий: {e}")
            return False
    
    def _go_to_best_square(self):
        """Переходим на подходящий квадрат"""
        self.display.print_message("🎯 Ищем подходящий квадрат...", "info")
        
        try:
            # Получаем информацию о квадратах
            user_info = self.api_client.get_user_info()
            squares = user_info.get("squares", [])
            
            if squares:
                best_square = self._find_best_square(squares)
                
                if best_square:
                    self.display.print_message(f"🎯 Найден лучший квадрат: {best_square}", "info")
                    
                    # Переходим на лучший квадрат
                    result = self.api_client.change_square(best_square)
                    
                    if result.get("status") == "success":
                        self.display.print_message(f"✅ Переход на квадрат {best_square} успешен", "success")
                    else:
                        self.display.print_message(f"❌ Ошибка перехода на квадрат {best_square}: {result.get('message', 'Неизвестная ошибка')}", "error")
                else:
                    self.display.print_message("❌ Не найден подходящий квадрат", "error")
            else:
                self.display.print_message("❌ Нет информации о квадратах", "error")
                
        except Exception as e:
            logger.error(f"Ошибка перехода на квадрат: {e}")
            self.display.print_message(f"❌ Ошибка перехода на квадрат: {e}", "error")
    
    def _find_best_square(self, squares: List[Dict[str, Any]]) -> Optional[str]:
        """Находит лучший квадрат для текущего уровня"""
        player_level = self.player.level
        target_level = player_level - 9  # Ищем мобов на 9 уровней ниже
        best_square = None
        best_score = float('inf')  # Минимальная разница в уровнях
        
        logger.info(f"Ищем квадрат с мобами уровня {target_level} (игрок {player_level})")
        
        for square in squares:
            position = square.get("position")
            lvl_mobs = square.get("lvlMobs")
            
            if lvl_mobs and "mobLvl" in lvl_mobs:
                try:
                    mob_level = int(lvl_mobs["mobLvl"])
                    level_diff = abs(mob_level - target_level)
                    
                    # Если мобы на 9 уровней ниже или выше - это идеально
                    if mob_level == target_level:
                        logger.info(f"Найден идеальный квадрат {position}: мобы уровня {mob_level}")
                        return position
                    
                    # Ищем квадрат с минимальной разницей в уровнях
                    if level_diff < best_score:
                        best_score = level_diff
                        best_square = position
                        logger.info(f"Новый лучший квадрат {position}: мобы уровня {mob_level} (разница {level_diff})")
                        
                except (ValueError, TypeError) as e:
                    # Если не удается преобразовать mob_level, пропускаем этот квадрат
                    logger.warning(f"Не удается обработать уровень мобов в квадрате {position}: {e}")
                    continue
        
        if best_square:
            logger.info(f"Выбран лучший квадрат {best_square} с разницей в уровнях {best_score}")
        else:
            logger.warning("Не найден подходящий квадрат")
            
        return best_square
    
    def _force_display_update(self):
        """Принудительное обновление дисплея"""
        try:
            current_time = time.time()
            player_data = self.player.get_stats_summary()
            
            # Обновляем дисплей с текущими данными
            self.display.update_display(
                current_state="city",  # Во время восстановления считаем что в городе
                player_data=player_data,
                mob_data=None,
                mob_group_data=None,
                attack_cooldown=0,
                heal_cooldown=0,
                skill_cooldown=0,
                mana_cooldown=0,
                rest_time=None,
                player_name="Piulok",
                last_attack_time=self.player.last_attack_time,
                last_skill_time=self.player.last_skill_time
            )
            
            # Обновляем статистику
            self.display.update_stats(
                current_gold=self.player.get_gold_count(),
                current_skulls=self.player.get_skulls_count()
            )
        except Exception as e:
            logger.warning(f"Ошибка принудительного обновления дисплея: {e}")
    
    def _reset_location(self):
        """Сбрасываем локацию перед переходом в город"""
        self.display.print_message("🔄 Сбрасываем локацию...", "info")
        
        try:
            result = self.api_client.change_geo("", "", "reset")
            
            if result.get("status") == "success":
                self.display.print_message("✅ Сброс локации успешен", "success")
            else:
                self.display.print_message(f"❌ Ошибка сброса локации: {result.get('message', 'Неизвестная ошибка')}", "error")
                
        except Exception as e:
            logger.error(f"Ошибка сброса локации: {e}")
            self.display.print_message(f"❌ Ошибка сброса локации: {e}", "error")
    
    def _go_to_farm_zone(self):
        """Переходим в фарм зону"""
        self.display.print_message("🌾 Переходим в фарм зону...", "info")
        
        try:
            result = self.api_client.change_main_geo("farm")
            
            if result.get("status") == "success":
                self.display.print_message("✅ Переход в фарм зону успешен", "success")
            else:
                self.display.print_message(f"❌ Ошибка перехода в фарм зону: {result.get('message', 'Неизвестная ошибка')}", "error")
                
        except Exception as e:
            logger.error(f"Ошибка перехода в фарм зону: {e}")
            self.display.print_message(f"❌ Ошибка перехода в фарм зону: {e}", "error")
    
    def _go_to_location(self):
        """Переходим на локацию"""
        self.display.print_message("📍 Переходим на локацию...", "info")
        
        try:
            # Выбираем локацию в зависимости от уровня персонажа
            player_level = self.player.level
            if player_level < 10:
                # Для персонажей ниже 10 уровня используем loco_0
                self.display.print_message(f"📍 Переходим в loco_0 (уровень {player_level} < 10)...", "info")
                result = self.api_client.change_geo("loco_0", "south")
            else:
                # Для персонажей 10+ уровня используем loco_3
                self.display.print_message(f"📍 Переходим в loco_3 (уровень {player_level} >= 10)...", "info")
                result = self.api_client.change_geo("loco_3", "south")
            
            if result.get("status") == "success":
                self.display.print_message("✅ Переход на локацию успешен", "success")
            else:
                self.display.print_message(f"❌ Ошибка перехода на локацию: {result.get('message', 'Неизвестная ошибка')}", "error")
                
        except Exception as e:
            logger.error(f"Ошибка перехода на локацию: {e}")
            self.display.print_message(f"❌ Ошибка перехода на локацию: {e}", "error") 