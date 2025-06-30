"""
Data Extractor - Extracts and formats data from API responses
"""

import logging
from typing import Optional, List, Dict, Any
import json
import os
# Новые утилиты
from logic.mob_utils import normalize_mob_name
from logic.drop_utils import flatten_drop

logger = logging.getLogger(__name__)

class DataExtractor:
    """Extracts and formats data from API responses"""
    
    def extract_mob_data(self, response_data: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
        """
        Extract mob data from API response
        
        Args:
            response_data: API response data
            
        Returns:
            List of mob data dictionaries or None
        """
        logger.debug(f"🔍 DEBUG: extract_mob_data called with response keys: {list(response_data.keys()) if isinstance(response_data, dict) else 'Not a dict'}")
        
        mobs_found = []
        
        # Try different possible locations for mob data
        if isinstance(response_data, dict):
            # Direct mob data
            if 'mob' in response_data:
                mob_list = response_data['mob']
                logger.debug(f"🔍 DEBUG: Found 'mob' field: {type(mob_list)}")
                if isinstance(mob_list, list) and len(mob_list) > 0:
                    logger.debug(f"🔍 DEBUG: mob_list is list with {len(mob_list)} items")
                    mobs_found.extend(mob_list)
                elif isinstance(mob_list, dict):
                    logger.debug("🔍 DEBUG: mob_list is dict")
                    mobs_found.append(mob_list)
            
            # Check if response contains farm data
            if 'farm' in response_data and isinstance(response_data['farm'], list):
                logger.debug("🔍 DEBUG: Found 'farm' field")
                for farm_item in response_data['farm']:
                    if isinstance(farm_item, dict) and 'mob' in farm_item:
                        mob_data = farm_item['mob']
                        if isinstance(mob_data, list) and len(mob_data) > 0:
                            mobs_found.extend(mob_data)
                        elif isinstance(mob_data, dict):
                            mobs_found.append(mob_data)
        
        logger.debug(f"🔍 DEBUG: extract_mob_data returning {len(mobs_found)} mobs: {mobs_found}")
        
        if mobs_found:
            return mobs_found
        
        return None
    
    def extract_mob_group_data(self, response_data: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
        """
        Extract mob group data from API response for display
        
        Args:
            response_data: API response data
            
        Returns:
            List of mob data dictionaries formatted for display or None
        """
        logger = logging.getLogger(__name__)
        
        mobs_found = self.extract_mob_data(response_data)
        
        if not mobs_found:
            return None
        
        # Format mobs for display
        formatted_mobs = []
        for i, mob in enumerate(mobs_found):
            if isinstance(mob, dict):
                formatted_mob = {
                    'name': mob.get('name', 'Неизвестно'),
                    'hp': f"{mob.get('hp', 0)}/{mob.get('maxHp', 1)}",
                    'level': mob.get('level', 1),
                    'is_current_target': i == 0,  # First mob is current target
                    'is_dead': mob.get('hp', 1) <= 0
                }
                formatted_mobs.append(formatted_mob)
        
        logger.debug(f"🔍 DEBUG: extract_mob_group_data returning {len(formatted_mobs)} formatted mobs")
        return formatted_mobs
    
    def extract_player_data(self, response_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Extract player data from API response
        
        Args:
            response_data: API response data
            
        Returns:
            Player data dictionary or None
        """
        # Try different possible locations for player data
        if isinstance(response_data, dict):
            # Direct player data
            if 'player' in response_data:
                return response_data['player']
            
            # Check if response contains user data
            if 'user' in response_data:
                return response_data['user']
        
        return None
    
    def extract_combat_results(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract combat results from API response
        
        Args:
            response_data: API response data
            
        Returns:
            Dictionary with combat results
        """
        results = {
            'damage_dealt': 0,
            'damage_received': 0,
            'exp_gained': 0,
            'gold_gained': 0,
            'drops': [],
            'killed_mobs': []
        }
        
        if not isinstance(response_data, dict):
            return results
        
        # Extract experience and gold from victory data
        if 'dataWin' in response_data:
            win_data = response_data['dataWin']
            results['exp_gained'] = win_data.get('expWin', 0)
            
            # Extract gold from drops
            drop_data = win_data.get('drop', [])
            results['drops'] = drop_data
            results['gold_gained'] = sum(
                item.get('count', 0) for item in drop_data 
                if item.get('id') == 'm_0_1'
            )
        
        # Extract killed mobs from logs
        if 'arrLogs' in response_data:
            arr_logs = response_data['arrLogs']
            for log_entry in arr_logs:
                messages = log_entry.get('messages', [])
                for message in messages:
                    if 'погиб' in message or 'погибла' in message:
                        mob_name = log_entry.get('defname', 'Unknown')
                        if mob_name not in results['killed_mobs']:
                            results['killed_mobs'].append(mob_name)
        
        return results

    def update_mob_database(self, mob_data: dict, player_level: int, db_path: str = "world_map_viewer/data/mobs-database.json", loco_id: str = None, side_key: str = None) -> bool:
        """
        Новая логика: Записывает моба только в world_map_viewer/data/mobs-database.json по структуре:
        id, name, photo, desc, farmId, location, side, drop (id, typeElement, count, chance, minLvlDrop)
        location и side вычислять через world map, side переводить на русский
        Все поля брать из ответа атаки (или исследования), minLvlDrop писать только если ещё не было
        """
        import json, os
        logger = logging.getLogger(__name__)
        # Загружаем текущую базу
        if not os.path.exists(db_path):
            db = []
        else:
            with open(db_path, 'r', encoding='utf-8') as f:
                try:
                    db = json.load(f)
                except Exception:
                    db = []
        # Получаем карту мира
        world_map_path = "world_map_viewer/data/complete_world_map.json"
        with open(world_map_path, 'r', encoding='utf-8') as f:
            world_map_data = json.load(f)
        world_map = world_map_data.get('world_map', {})
        side_ru = {'north': 'Север', 'south': 'Юг', 'west': 'Запад', 'east': 'Восток', 'center': 'Центр'}
        # Определяем location и side
        location_name = "unknown"
        side_name = "unknown"
        if loco_id and loco_id in world_map:
            location_name = world_map[loco_id].get('name', 'unknown')
            if side_key:
                side_name = side_ru.get(side_key, side_key)
        # Собираем структуру моба
        mob_entry = {
            'id': mob_data.get('id', ''),
            'name': mob_data.get('name', ''),
            'photo': mob_data.get('photo', None),
            'desc': mob_data.get('desc', None),
            'farmId': mob_data.get('farmId', ''),
            'location': location_name,
            'side': side_name,
            'drop': []
        }
        # Обрабатываем drop
        for item in mob_data.get('drop', []):
            if not isinstance(item, dict):
                logger.warning(f"[DROP DEBUG] Unexpected drop item type in update_mob_database: {type(item)}, value: {item}")
                continue
            drop_item = {
                'id': item.get('id', ''),
                'typeElement': item.get('typeElement', ''),
                'count': item.get('count', 1),
                'chance': item.get('chance', None)
            }
            # minLvlDrop: если уже есть для этого id+typeElement, не обновлять, иначе писать текущий уровень
            found = False
            for old_mob in db:
                for old_drop in old_mob.get('drop', []):
                    if old_drop.get('id') == drop_item['id'] and old_drop.get('typeElement') == drop_item['typeElement']:
                        if 'minLvlDrop' in old_drop:
                            drop_item['minLvlDrop'] = old_drop['minLvlDrop']
                            found = True
                        break
                if found:
                    break
            if not found:
                drop_item['minLvlDrop'] = player_level
            mob_entry['drop'].append(drop_item)
        # Проверяем на дубликаты по id и farmId
        exists = False
        for i, m in enumerate(db):
            if m.get('id') == mob_entry['id'] and m.get('farmId') == mob_entry['farmId']:
                db[i] = mob_entry
                exists = True
                break
        if not exists:
            db.append(mob_entry)
        # Строгая валидация обязательных полей
        required_fields = ['id', 'name', 'photo', 'desc', 'farmId', 'location', 'side']
        missing_fields = [field for field in required_fields if not mob_entry.get(field)]
        if missing_fields:
            logger.error(f"[MOB DB] Не записываю моба {mob_entry.get('name', '')}: отсутствуют обязательные поля: {missing_fields}")
            return False
        # Сохраняем
        with open(db_path, 'w', encoding='utf-8') as f:
            json.dump(db, f, ensure_ascii=False, indent=2)
        logger.debug(f"[MOB DB] Итоговая запись mob_entry: {mob_entry}")
        return True

    def extract_drop(self, drop_data) -> List[Dict[str, Any]]:
        return flatten_drop(drop_data) 