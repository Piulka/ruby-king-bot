"""
Data Extractor - Extracts and formats data from API responses
"""

import logging
from typing import Optional, List, Dict, Any

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