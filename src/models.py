"""Core data models for Tang Dynasty Dialogue System"""

from dataclasses import dataclass, field
from typing import List, Tuple, Optional
from enum import Enum
from datetime import datetime
import json


class TurnNumber(Enum):
    """Enumeration of dialogue turns"""
    TURN_1 = 1  # Food cooking and preservation
    TURN_2 = 2  # Clothing materials and fastening
    TURN_3 = 3  # Clothing colors and social hierarchy


@dataclass
class KnowledgeWindow:
    """Educational content displayed after convergence"""
    title: str
    body: str
    image_description: str
    
    def to_dict(self) -> dict:
        """Serialize to dictionary"""
        return {
            'title': self.title,
            'body': self.body,
            'image_description': self.image_description
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'KnowledgeWindow':
        """Deserialize from dictionary"""
        return cls(
            title=data['title'],
            body=data['body'],
            image_description=data['image_description']
        )
    
    def to_json(self) -> str:
        """Serialize to JSON string"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


@dataclass
class DialogueResponse:
    """Response returned to frontend"""
    npc_response: str
    turn: int
    knowledge_window: KnowledgeWindow
    is_complete: bool
    
    def to_dict(self) -> dict:
        """Serialize to dictionary"""
        return {
            'npc_response': self.npc_response,
            'turn': self.turn,
            'knowledge_window': self.knowledge_window.to_dict(),
            'is_complete': self.is_complete
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'DialogueResponse':
        """Deserialize from dictionary"""
        return cls(
            npc_response=data['npc_response'],
            turn=data['turn'],
            knowledge_window=KnowledgeWindow.from_dict(data['knowledge_window']),
            is_complete=data['is_complete']
        )
    
    def to_json(self) -> str:
        """Serialize to JSON string"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


@dataclass
class ConversationState:
    """Complete state of the dialogue system"""
    current_turn: TurnNumber
    is_complete: bool
    conversation_history: List[Tuple[str, str]] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> dict:
        """Serialize to dictionary for storage"""
        return {
            'current_turn': self.current_turn.value,
            'is_complete': self.is_complete,
            'conversation_history': self.conversation_history,
            'timestamp': self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ConversationState':
        """Deserialize from dictionary"""
        return cls(
            current_turn=TurnNumber(data['current_turn']),
            is_complete=data['is_complete'],
            conversation_history=data.get('conversation_history', []),
            timestamp=data.get('timestamp', datetime.now().isoformat())
        )
    
    def to_json(self) -> str:
        """Serialize to JSON string"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


@dataclass
class SystemConfig:
    """System configuration loaded from environment"""
    api_key: str
    model_name: str = "gemini-3.1-flash-lite"
    max_input_length: int = 500
    storage_backend: str = "file"  # file, memory, or database
    state_file_path: str = "./conversation_state.json"
    prompts_config_path: str = "./config/prompts.json"
    knowledge_config_path: str = "./config/knowledge_windows.json"
    temperature: float = 0.7
    max_tokens: int = 500
    
    def to_dict(self) -> dict:
        """Serialize to dictionary"""
        return {
            'api_key': self.api_key,
            'model_name': self.model_name,
            'max_input_length': self.max_input_length,
            'storage_backend': self.storage_backend,
            'state_file_path': self.state_file_path,
            'prompts_config_path': self.prompts_config_path,
            'knowledge_config_path': self.knowledge_config_path,
            'temperature': self.temperature,
            'max_tokens': self.max_tokens
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'SystemConfig':
        """Deserialize from dictionary"""
        return cls(
            api_key=data['api_key'],
            model_name=data.get('model_name', 'gemini-3.1-flash-lite'),
            max_input_length=data.get('max_input_length', 500),
            storage_backend=data.get('storage_backend', 'file'),
            state_file_path=data.get('state_file_path', './conversation_state.json'),
            prompts_config_path=data.get('prompts_config_path', './config/prompts.json'),
            knowledge_config_path=data.get('knowledge_config_path', './config/knowledge_windows.json'),
            temperature=data.get('temperature', 0.7),
            max_tokens=data.get('max_tokens', 500)
        )
    
    def to_json(self) -> str:
        """Serialize to JSON string (excluding sensitive data like api_key)"""
        data = self.to_dict()
        data['api_key'] = '***REDACTED***'
        return json.dumps(data, ensure_ascii=False, indent=2)
    
    @classmethod
    def from_env(cls) -> 'SystemConfig':
        """Load configuration from environment variables"""
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        return cls(
            api_key=api_key,
            model_name=os.getenv('MODEL_NAME', 'gemini-3.1-flash-lite'),
            max_input_length=int(os.getenv('MAX_INPUT_LENGTH', '500')),
            storage_backend=os.getenv('STORAGE_BACKEND', 'file'),
            state_file_path=os.getenv('STATE_FILE_PATH', './conversation_state.json'),
            prompts_config_path=os.getenv('PROMPTS_CONFIG_PATH', './config/prompts.json'),
            knowledge_config_path=os.getenv('KNOWLEDGE_CONFIG_PATH', './config/knowledge_windows.json'),
            temperature=float(os.getenv('TEMPERATURE', '0.7')),
            max_tokens=int(os.getenv('MAX_TOKENS', '500'))
        )
