"""
Game state management for Ruby King
"""

import logging
from enum import Enum
from typing import Optional, Dict, Any
from ruby_king_bot.config.settings import Settings

logger = logging.getLogger(__name__)

class GameState(Enum):
    """Game states enumeration"""
    CITY = "city"           # In city/main menu
    EXPLORING = "exploring" # Exploring territory (temporary)
    COMBAT = "combat"       # In combat with mob (after explore)
    RESTING = "resting"     # Resting at campfire
    HEALING = "healing"     # Using healing potion

class GameStateManager:
    """Manages game state transitions and current state"""
    
    def __init__(self):
        self.current_state = GameState.CITY
        self.previous_state = None
        self.state_history = []
        
    def change_state(self, new_state: GameState, reason: str = ""):
        """
        Change game state with logging
        
        Args:
            new_state: New state to transition to
            reason: Reason for state change
        """
        if new_state != self.current_state:
            self.previous_state = self.current_state
            self.current_state = new_state
            self.state_history.append({
                'from': self.previous_state.value,
                'to': new_state.value,
                'reason': reason
            })
            
            logger.info(f"State change: {self.previous_state.value} → {new_state.value} ({reason})")
    
    def get_current_state(self) -> GameState:
        """Get current game state"""
        return self.current_state
    
    def is_in_combat(self) -> bool:
        """Check if currently in combat state"""
        return self.current_state == GameState.COMBAT
    
    def is_in_city(self) -> bool:
        """Check if currently in city state"""
        return self.current_state == GameState.CITY
    
    def is_resting(self) -> bool:
        """Check if currently resting"""
        return self.current_state == GameState.RESTING
    
    def can_explore(self) -> bool:
        """
        Check if can explore territory
        
        CRITICAL: Can only explore when not in combat
        """
        return self.current_state == GameState.CITY
    
    def can_attack(self) -> bool:
        """Check if can attack (must be in combat)"""
        return self.current_state == GameState.COMBAT
    
    def can_heal(self) -> bool:
        """Check if can use healing potion"""
        return self.current_state in [GameState.CITY, GameState.COMBAT]
    
    def can_rest(self) -> bool:
        """Check if can rest at campfire"""
        return self.current_state == GameState.CITY
    
    def get_state_info(self) -> Dict[str, Any]:
        """Get current state information"""
        return {
            'current_state': self.current_state.value,
            'previous_state': self.previous_state.value if self.previous_state else None,
            'can_explore': self.can_explore(),
            'can_attack': self.can_attack(),
            'can_heal': self.can_heal(),
            'can_rest': self.can_rest(),
            'state_history': self.state_history[-5:]  # Last 5 state changes
        } 