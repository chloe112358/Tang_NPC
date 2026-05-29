"""Knowledge Window Provider for Tang Dynasty Dialogue System

This module provides educational content for each dialogue turn.
"""

import json
from pathlib import Path
from typing import Dict, Any

from src.models import KnowledgeWindow


class KnowledgeWindowProvider:
    """Provides pre-written educational content for each turn
    
    Responsibilities:
    - Load knowledge window content from configuration file
    - Return KnowledgeWindow dataclass for specified turn
    - Handle missing or invalid configuration gracefully
    """
    
    def __init__(self, content_config_path: str):
        """Initialize with path to knowledge windows configuration file
        
        Args:
            content_config_path: Path to knowledge_windows.json file
            
        Raises:
            FileNotFoundError: If configuration file does not exist
            ValueError: If configuration file is invalid JSON
        """
        self.content_config_path = Path(content_config_path)
        self._content: Dict[str, Dict[str, str]] = {}
        self._load_content()
    
    def _load_content(self) -> None:
        """Load knowledge window content from configuration file
        
        Raises:
            FileNotFoundError: If configuration file does not exist
            ValueError: If configuration file is invalid JSON or missing required fields
        """
        if not self.content_config_path.exists():
            raise FileNotFoundError(
                f"Knowledge windows configuration file not found: {self.content_config_path}"
            )
        
        try:
            with open(self.content_config_path, 'r', encoding='utf-8') as f:
                self._content = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Invalid JSON in knowledge windows configuration file: {e}"
            )
        
        # Validate that all required turns are present
        required_turns = ['turn_1', 'turn_2', 'turn_3']
        for turn_key in required_turns:
            if turn_key not in self._content:
                raise ValueError(
                    f"Missing required turn '{turn_key}' in knowledge windows configuration"
                )
            
            # Validate required fields for each turn
            required_fields = ['title', 'body', 'image_description']
            for field in required_fields:
                if field not in self._content[turn_key]:
                    raise ValueError(
                        f"Missing required field '{field}' in {turn_key} configuration"
                    )
    
    def get_knowledge_window(self, turn: int) -> KnowledgeWindow:
        """Return knowledge window content for specified turn
        
        Args:
            turn: Turn number (1, 2, or 3)
            
        Returns:
            KnowledgeWindow dataclass with title, body, and image_description
            
        Raises:
            ValueError: If turn number is not 1, 2, or 3
        """
        if turn not in [1, 2, 3]:
            raise ValueError(f"Invalid turn number: {turn}. Must be 1, 2, or 3.")
        
        turn_key = f"turn_{turn}"
        turn_data = self._content[turn_key]
        
        return KnowledgeWindow(
            title=turn_data['title'],
            body=turn_data['body'],
            image_description=turn_data['image_description']
        )
