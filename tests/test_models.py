"""Tests for core data models"""

import pytest
import json
from datetime import datetime
from src.models import (
    TurnNumber,
    KnowledgeWindow,
    DialogueResponse,
    ConversationState,
    SystemConfig
)


class TestKnowledgeWindow:
    """Test KnowledgeWindow serialization"""
    
    def test_to_dict(self):
        kw = KnowledgeWindow(
            title="Test Title",
            body="Test Body",
            image_description="Test Image"
        )
        data = kw.to_dict()
        
        assert data['title'] == "Test Title"
        assert data['body'] == "Test Body"
        assert data['image_description'] == "Test Image"
    
    def test_from_dict(self):
        data = {
            'title': "Test Title",
            'body': "Test Body",
            'image_description': "Test Image"
        }
        kw = KnowledgeWindow.from_dict(data)
        
        assert kw.title == "Test Title"
        assert kw.body == "Test Body"
        assert kw.image_description == "Test Image"
    
    def test_to_json(self):
        kw = KnowledgeWindow(
            title="唐代的鮮與存",
            body="唐代沒有冰箱",
            image_description="胡餅爐"
        )
        json_str = kw.to_json()
        data = json.loads(json_str)
        
        assert data['title'] == "唐代的鮮與存"
        assert data['body'] == "唐代沒有冰箱"
        assert data['image_description'] == "胡餅爐"


class TestDialogueResponse:
    """Test DialogueResponse serialization"""
    
    def test_to_dict(self):
        kw = KnowledgeWindow("Title", "Body", "Image")
        response = DialogueResponse(
            npc_response="Test response",
            turn=1,
            knowledge_window=kw,
            is_complete=False
        )
        data = response.to_dict()
        
        assert data['npc_response'] == "Test response"
        assert data['turn'] == 1
        assert data['is_complete'] is False
        assert 'knowledge_window' in data
    
    def test_from_dict(self):
        data = {
            'npc_response': "Test response",
            'turn': 2,
            'knowledge_window': {
                'title': "Title",
                'body': "Body",
                'image_description': "Image"
            },
            'is_complete': True
        }
        response = DialogueResponse.from_dict(data)
        
        assert response.npc_response == "Test response"
        assert response.turn == 2
        assert response.is_complete is True
        assert response.knowledge_window.title == "Title"
    
    def test_to_json(self):
        kw = KnowledgeWindow("Title", "Body", "Image")
        response = DialogueResponse(
            npc_response="Test",
            turn=3,
            knowledge_window=kw,
            is_complete=True
        )
        json_str = response.to_json()
        data = json.loads(json_str)
        
        assert 'npc_response' in data
        assert 'turn' in data
        assert 'knowledge_window' in data
        assert 'is_complete' in data


class TestConversationState:
    """Test ConversationState serialization"""
    
    def test_to_dict(self):
        state = ConversationState(
            current_turn=TurnNumber.TURN_1,
            is_complete=False,
            conversation_history=[("input1", "response1")],
            timestamp="2024-01-01T00:00:00"
        )
        data = state.to_dict()
        
        assert data['current_turn'] == 1
        assert data['is_complete'] is False
        assert len(data['conversation_history']) == 1
        assert data['timestamp'] == "2024-01-01T00:00:00"
    
    def test_from_dict(self):
        data = {
            'current_turn': 2,
            'is_complete': False,
            'conversation_history': [("input1", "response1"), ("input2", "response2")],
            'timestamp': "2024-01-01T00:00:00"
        }
        state = ConversationState.from_dict(data)
        
        assert state.current_turn == TurnNumber.TURN_2
        assert state.is_complete is False
        assert len(state.conversation_history) == 2
        assert state.timestamp == "2024-01-01T00:00:00"
    
    def test_to_json(self):
        state = ConversationState(
            current_turn=TurnNumber.TURN_3,
            is_complete=True,
            conversation_history=[],
            timestamp="2024-01-01T00:00:00"
        )
        json_str = state.to_json()
        data = json.loads(json_str)
        
        assert data['current_turn'] == 3
        assert data['is_complete'] is True


class TestSystemConfig:
    """Test SystemConfig serialization"""
    
    def test_to_dict(self):
        config = SystemConfig(api_key="test_key")
        data = config.to_dict()
        
        assert data['api_key'] == "test_key"
        assert data['model_name'] == "gemini-3.1-flash-lite"
        assert data['max_input_length'] == 500
    
    def test_from_dict(self):
        data = {
            'api_key': "test_key",
            'model_name': "custom-model",
            'max_input_length': 1000
        }
        config = SystemConfig.from_dict(data)
        
        assert config.api_key == "test_key"
        assert config.model_name == "custom-model"
        assert config.max_input_length == 1000
    
    def test_to_json_redacts_api_key(self):
        config = SystemConfig(api_key="secret_key")
        json_str = config.to_json()
        data = json.loads(json_str)
        
        assert data['api_key'] == "***REDACTED***"
        assert 'secret_key' not in json_str
    
    def test_from_env_with_all_variables(self, monkeypatch):
        """Test from_env() loads all environment variables correctly"""
        # Set all environment variables
        monkeypatch.setenv('GEMINI_API_KEY', 'test_api_key_123')
        monkeypatch.setenv('MODEL_NAME', 'custom-model')
        monkeypatch.setenv('MAX_INPUT_LENGTH', '1000')
        monkeypatch.setenv('STORAGE_BACKEND', 'memory')
        monkeypatch.setenv('STATE_FILE_PATH', './custom_state.json')
        monkeypatch.setenv('PROMPTS_CONFIG_PATH', './custom_prompts.json')
        monkeypatch.setenv('KNOWLEDGE_CONFIG_PATH', './custom_knowledge.json')
        monkeypatch.setenv('TEMPERATURE', '0.9')
        monkeypatch.setenv('MAX_TOKENS', '1000')
        
        config = SystemConfig.from_env()
        
        assert config.api_key == 'test_api_key_123'
        assert config.model_name == 'custom-model'
        assert config.max_input_length == 1000
        assert config.storage_backend == 'memory'
        assert config.state_file_path == './custom_state.json'
        assert config.prompts_config_path == './custom_prompts.json'
        assert config.knowledge_config_path == './custom_knowledge.json'
        assert config.temperature == 0.9
        assert config.max_tokens == 1000
    
    def test_from_env_with_only_required_variable(self, monkeypatch):
        """Test from_env() with only GEMINI_API_KEY set, uses defaults for others"""
        # Clear all environment variables first
        monkeypatch.delenv('MODEL_NAME', raising=False)
        monkeypatch.delenv('MAX_INPUT_LENGTH', raising=False)
        monkeypatch.delenv('STORAGE_BACKEND', raising=False)
        monkeypatch.delenv('STATE_FILE_PATH', raising=False)
        monkeypatch.delenv('PROMPTS_CONFIG_PATH', raising=False)
        monkeypatch.delenv('KNOWLEDGE_CONFIG_PATH', raising=False)
        monkeypatch.delenv('TEMPERATURE', raising=False)
        monkeypatch.delenv('MAX_TOKENS', raising=False)
        
        # Set only required variable
        monkeypatch.setenv('GEMINI_API_KEY', 'required_key')
        
        config = SystemConfig.from_env()
        
        # Verify required field
        assert config.api_key == 'required_key'
        
        # Verify defaults
        assert config.model_name == 'gemini-3.1-flash-lite'
        assert config.max_input_length == 500
        assert config.storage_backend == 'file'
        assert config.state_file_path == './conversation_state.json'
        assert config.prompts_config_path == './config/prompts.json'
        assert config.knowledge_config_path == './config/knowledge_windows.json'
        assert config.temperature == 0.7
        assert config.max_tokens == 500
    
    def test_from_env_missing_api_key_raises_error(self, monkeypatch):
        """Test from_env() raises clear error when GEMINI_API_KEY is missing"""
        # Set GEMINI_API_KEY to None to simulate missing
        monkeypatch.setenv('GEMINI_API_KEY', '')
        
        # Also ensure load_dotenv doesn't load from parent directories
        monkeypatch.setattr('dotenv.load_dotenv', lambda **kwargs: None)
        
        with pytest.raises(ValueError) as exc_info:
            SystemConfig.from_env()
        
        # Verify error message is clear
        assert "GEMINI_API_KEY" in str(exc_info.value)
        assert "required" in str(exc_info.value).lower()
    
    def test_from_env_empty_api_key_raises_error(self, monkeypatch):
        """Test from_env() raises error when GEMINI_API_KEY is empty string"""
        monkeypatch.setenv('GEMINI_API_KEY', '')
        
        with pytest.raises(ValueError) as exc_info:
            SystemConfig.from_env()
        
        assert "GEMINI_API_KEY" in str(exc_info.value)
    
    def test_from_env_integer_conversion(self, monkeypatch):
        """Test from_env() correctly converts string integers to int"""
        monkeypatch.setenv('GEMINI_API_KEY', 'test_key')
        monkeypatch.setenv('MAX_INPUT_LENGTH', '750')
        monkeypatch.setenv('MAX_TOKENS', '800')
        
        config = SystemConfig.from_env()
        
        assert isinstance(config.max_input_length, int)
        assert config.max_input_length == 750
        assert isinstance(config.max_tokens, int)
        assert config.max_tokens == 800
    
    def test_from_env_float_conversion(self, monkeypatch):
        """Test from_env() correctly converts string floats to float"""
        monkeypatch.setenv('GEMINI_API_KEY', 'test_key')
        monkeypatch.setenv('TEMPERATURE', '0.85')
        
        config = SystemConfig.from_env()
        
        assert isinstance(config.temperature, float)
        assert config.temperature == 0.85
    
    def test_from_env_loads_from_dotenv_file(self, monkeypatch):
        """Test from_env() loads from .env file when present"""
        # Mock load_dotenv to set specific values
        def mock_load_dotenv(**kwargs):
            import os
            os.environ['GEMINI_API_KEY'] = 'dotenv_key'
            os.environ['MODEL_NAME'] = 'dotenv_model'
        
        monkeypatch.setattr('dotenv.load_dotenv', mock_load_dotenv)
        
        config = SystemConfig.from_env()
        
        assert config.api_key == 'dotenv_key'
        assert config.model_name == 'dotenv_model'


class TestTurnNumber:
    """Test TurnNumber enum"""
    
    def test_turn_values(self):
        assert TurnNumber.TURN_1.value == 1
        assert TurnNumber.TURN_2.value == 2
        assert TurnNumber.TURN_3.value == 3
    
    def test_turn_from_value(self):
        assert TurnNumber(1) == TurnNumber.TURN_1
        assert TurnNumber(2) == TurnNumber.TURN_2
        assert TurnNumber(3) == TurnNumber.TURN_3
