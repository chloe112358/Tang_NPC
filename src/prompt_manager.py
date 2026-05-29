"""Prompt management for Tang Dynasty Dialogue System"""

import json
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class PromptManagerError(Exception):
    """Base exception for PromptManager-related errors"""
    pass


class PromptManager:
    """
    Manages system prompts and prompt-related configuration.
    
    The PromptManager is responsible for:
    - Loading prompts from configuration file (config/prompts.json)
    - Providing turn-specific system prompts
    - Providing convergence targets for each turn
    - Providing transition phrases for guiding conversations
    - Providing list of prohibited modern technology terms
    
    Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 8.2, 8.3, 8.4, 8.5
    """
    
    def __init__(self, prompts_config_path: str):
        """
        Initialize PromptManager by loading prompts from configuration file.
        
        Args:
            prompts_config_path: Path to the prompts.json configuration file
            
        Raises:
            PromptManagerError: If configuration file is missing or invalid
        """
        self.prompts_config_path = prompts_config_path
        self._config: Optional[Dict[str, Any]] = None
        self._load_config()
    
    def _load_config(self) -> None:
        """
        Load prompts configuration from JSON file.
        
        Handles missing configuration file gracefully by logging an error
        and initializing with empty configuration.
        
        Raises:
            PromptManagerError: If configuration file exists but is invalid JSON
        """
        config_path = Path(self.prompts_config_path)
        
        # Handle missing configuration file gracefully
        if not config_path.exists():
            logger.error(f"Prompts configuration file not found: {self.prompts_config_path}")
            logger.warning("Initializing with empty configuration. System may not function correctly.")
            self._config = self._get_default_config()
            return
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self._config = json.load(f)
                logger.info(f"Loaded prompts configuration from {self.prompts_config_path}")
                
                # Validate configuration structure
                self._validate_config()
                
        except json.JSONDecodeError as e:
            raise PromptManagerError(f"Invalid JSON in prompts configuration file: {e}")
        except OSError as e:
            raise PromptManagerError(f"Error reading prompts configuration file: {e}")
        except Exception as e:
            raise PromptManagerError(f"Unexpected error loading prompts configuration: {e}")
    
    def _validate_config(self) -> None:
        """
        Validate that the configuration has the expected structure.
        
        Raises:
            PromptManagerError: If configuration is missing required fields
        """
        if not isinstance(self._config, dict):
            raise PromptManagerError("Configuration must be a dictionary")
        
        # Check for required top-level keys
        required_keys = ['persona', 'prohibited_terms', 'transition_phrases', 'turns']
        missing_keys = [key for key in required_keys if key not in self._config]
        
        if missing_keys:
            raise PromptManagerError(f"Configuration missing required keys: {missing_keys}")
        
        # Validate turns structure
        turns = self._config.get('turns', {})
        if not isinstance(turns, dict):
            raise PromptManagerError("'turns' must be a dictionary")
        
        # Check that turns 1, 2, 3 exist
        for turn_num in ['1', '2', '3']:
            if turn_num not in turns:
                raise PromptManagerError(f"Configuration missing turn {turn_num}")
            
            turn_data = turns[turn_num]
            if 'system_prompt' not in turn_data:
                raise PromptManagerError(f"Turn {turn_num} missing 'system_prompt'")
            if 'convergence_target' not in turn_data:
                raise PromptManagerError(f"Turn {turn_num} missing 'convergence_target'")
        
        logger.debug("Configuration validation passed")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """
        Return a minimal default configuration.
        
        This is used as a fallback when the configuration file is missing.
        
        Returns:
            Dictionary with minimal default configuration
        """
        return {
            'persona': {
                'name': '安掌櫃',
                'identity': '長安西市的粟特人女老闆',
                'personality': ['熱情好客', '精明幹練'],
                'language_style': '唐朝半白話文',
                'knowledge_constraints': '完全不知道任何現代科技'
            },
            'prohibited_terms': [
                '微波爐', '冰箱', '拉鍊', '塑膠', '手機', '電腦',
                '冷藏', '加熱', '魔鬼氈', '尼龍', '聚酯纖維'
            ],
            'transition_phrases': [
                '哎呀！郎君這是說什麼傻話？',
                '您這外鄉人，不懂咱們長安的規矩...',
                '說起這個，咱們大唐人可有妙法...'
            ],
            'turns': {
                '1': {
                    'system_prompt': '你是安掌櫃，長安西市的粟特人女老闆。',
                    'convergence_target': {
                        'point_1': '胡餅現烤現吃',
                        'point_2': '香料醃製臘肉'
                    }
                },
                '2': {
                    'system_prompt': '你是安掌櫃，長安西市的粟特人女老闆。',
                    'convergence_target': {
                        'point_1': '絲綢材質優勢',
                        'point_2': '繫帶與蹀躞帶固定方式'
                    }
                },
                '3': {
                    'system_prompt': '你是安掌櫃，長安西市的粟特人女老闆。',
                    'convergence_target': {
                        'point_1': '品色服制度',
                        'point_2': '禁色警告'
                    }
                }
            }
        }
    
    def get_system_prompt(self, turn: int) -> str:
        """
        Return system prompt for specified turn.
        
        Args:
            turn: Turn number (1, 2, or 3)
            
        Returns:
            System prompt string for the specified turn
            
        Raises:
            PromptManagerError: If turn number is invalid
            
        Requirements: 8.2, 8.3
        """
        if turn not in [1, 2, 3]:
            raise PromptManagerError(f"Invalid turn number: {turn}. Must be 1, 2, or 3.")
        
        turn_key = str(turn)
        turns = self._config.get('turns', {})
        
        if turn_key not in turns:
            raise PromptManagerError(f"No configuration found for turn {turn}")
        
        turn_data = turns[turn_key]
        system_prompt = turn_data.get('system_prompt', '')
        
        if not system_prompt:
            logger.warning(f"Empty system prompt for turn {turn}")
        
        return system_prompt
    
    def get_convergence_target(self, turn: int) -> Dict[str, str]:
        """
        Return target convergence answer for turn.
        
        Args:
            turn: Turn number (1, 2, or 3)
            
        Returns:
            Dictionary containing convergence target points (e.g., {'point_1': '...', 'point_2': '...'})
            
        Raises:
            PromptManagerError: If turn number is invalid
            
        Requirements: 3.1, 3.2, 3.3
        """
        if turn not in [1, 2, 3]:
            raise PromptManagerError(f"Invalid turn number: {turn}. Must be 1, 2, or 3.")
        
        turn_key = str(turn)
        turns = self._config.get('turns', {})
        
        if turn_key not in turns:
            raise PromptManagerError(f"No configuration found for turn {turn}")
        
        turn_data = turns[turn_key]
        convergence_target = turn_data.get('convergence_target', {})
        
        if not convergence_target:
            logger.warning(f"Empty convergence target for turn {turn}")
        
        return convergence_target
    
    def get_transition_phrases(self) -> List[str]:
        """
        Return example phrases for guiding to convergence.
        
        Returns:
            List of transition phrase strings
            
        Requirements: 3.4, 3.5, 8.4
        """
        transition_phrases = self._config.get('transition_phrases', [])
        
        if not transition_phrases:
            logger.warning("No transition phrases found in configuration")
            return []
        
        return transition_phrases.copy()
    
    def get_prohibited_terms(self) -> List[str]:
        """
        Return list of modern terms to avoid.
        
        Returns:
            List of prohibited term strings (modern technology vocabulary)
            
        Requirements: 2.3, 8.5
        """
        prohibited_terms = self._config.get('prohibited_terms', [])
        
        if not prohibited_terms:
            logger.warning("No prohibited terms found in configuration")
            return []
        
        return prohibited_terms.copy()
    
    def get_persona(self) -> Dict[str, Any]:
        """
        Return persona configuration for An Shopkeeper.
        
        Returns:
            Dictionary containing persona details (name, identity, personality, etc.)
            
        Requirements: 2.1, 2.2
        """
        persona = self._config.get('persona', {})
        
        if not persona:
            logger.warning("No persona configuration found")
        
        return persona.copy()
    
    def get_fallback_response(self, turn: int) -> str:
        """
        Return pre-written fallback response for specified turn.
        
        This is used when the LLM API is unavailable.
        
        Args:
            turn: Turn number (1, 2, or 3)
            
        Returns:
            Fallback response string for the specified turn
            
        Raises:
            PromptManagerError: If turn number is invalid
            
        Requirements: 8.6, 11.2
        """
        if turn not in [1, 2, 3]:
            raise PromptManagerError(f"Invalid turn number: {turn}. Must be 1, 2, or 3.")
        
        turn_key = str(turn)
        turns = self._config.get('turns', {})
        
        if turn_key not in turns:
            raise PromptManagerError(f"No configuration found for turn {turn}")
        
        turn_data = turns[turn_key]
        fallback_response = turn_data.get('fallback_response', '')
        
        if not fallback_response:
            logger.warning(f"No fallback response configured for turn {turn}")
            # Return a generic fallback
            return "安掌櫃正忙著招呼其他客人，請稍候片刻..."
        
        return fallback_response
    
    def get_preset_options(self, turn: int) -> Dict[str, str]:
        """
        Return preset options (A and B) for specified turn.
        
        Args:
            turn: Turn number (1, 2, or 3)
            
        Returns:
            Dictionary with keys 'A' and 'B' containing preset option texts
            
        Raises:
            PromptManagerError: If turn number is invalid
            
        Requirements: 4.1, 4.2
        """
        if turn not in [1, 2, 3]:
            raise PromptManagerError(f"Invalid turn number: {turn}. Must be 1, 2, or 3.")
        
        turn_key = str(turn)
        turns = self._config.get('turns', {})
        
        if turn_key not in turns:
            raise PromptManagerError(f"No configuration found for turn {turn}")
        
        turn_data = turns[turn_key]
        preset_options = turn_data.get('preset_options', {})
        
        if not preset_options:
            logger.warning(f"No preset options configured for turn {turn}")
            return {}
        
        return preset_options.copy()
