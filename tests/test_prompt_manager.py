"""
Unit tests for PromptManager class.

Tests the PromptManager's ability to load prompts from configuration,
retrieve turn-specific prompts, and handle error conditions.

Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 8.2, 8.3, 8.4, 8.5
"""

import json
import pytest
import tempfile
from pathlib import Path
from src.prompt_manager import PromptManager, PromptManagerError


@pytest.fixture
def valid_config_file():
    """Create a temporary valid configuration file"""
    config_data = {
        "persona": {
            "name": "安掌櫃",
            "identity": "長安西市的粟特人女老闆",
            "personality": ["熱情好客", "精明幹練"],
            "language_style": "唐朝半白話文",
            "knowledge_constraints": "完全不知道任何現代科技"
        },
        "prohibited_terms": [
            "微波爐", "冰箱", "拉鍊", "塑膠", "手機"
        ],
        "transition_phrases": [
            "哎呀！郎君這是說什麼傻話？",
            "您這外鄉人，不懂咱們長安的規矩...",
            "說起這個，咱們大唐人可有妙法..."
        ],
        "turns": {
            "1": {
                "system_prompt": "你是安掌櫃，長安西市的粟特人女老闆。本輪收束目標：胡餅和臘肉。",
                "convergence_target": {
                    "point_1": "胡餅現烤現吃",
                    "point_2": "香料醃製臘肉"
                },
                "fallback_response": "咱們大唐人吃東西有兩套本事...",
                "preset_options": {
                    "A": "烤餅冷了怎麼辦？",
                    "B": "肉會不會壞？"
                }
            },
            "2": {
                "system_prompt": "你是安掌櫃，長安西市的粟特人女老闆。本輪收束目標：絲綢和蹀躞帶。",
                "convergence_target": {
                    "point_1": "絲綢材質優勢",
                    "point_2": "繫帶與蹀躞帶固定方式"
                },
                "fallback_response": "咱們大唐的衣裳講究料子和綁法...",
                "preset_options": {
                    "A": "沒有拉鍊怎麼穿？",
                    "B": "絲綢會不會冷？"
                }
            },
            "3": {
                "system_prompt": "你是安掌櫃，長安西市的粟特人女老闆。本輪收束目標：品色服制度。",
                "convergence_target": {
                    "point_1": "品色服制度",
                    "point_2": "禁色警告"
                },
                "fallback_response": "紫色可是三品以上大員才能穿的...",
                "preset_options": {
                    "A": "我想買紫色衣服",
                    "B": "為什麼顏色不一樣？"
                }
            }
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        json.dump(config_data, f, ensure_ascii=False)
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    Path(temp_path).unlink(missing_ok=True)


@pytest.fixture
def real_config_path():
    """Path to the real prompts.json configuration file"""
    return "config/prompts.json"


@pytest.fixture
def prompt_manager(valid_config_file):
    """Create a PromptManager instance with valid configuration"""
    return PromptManager(valid_config_file)


class TestPromptManagerInitialization:
    """Test PromptManager initialization and configuration loading"""
    
    def test_initialization_with_valid_config(self, valid_config_file):
        """Test successful initialization with valid configuration file"""
        pm = PromptManager(valid_config_file)
        assert pm is not None
        assert pm._config is not None
    
    def test_initialization_with_missing_config(self):
        """Test graceful handling of missing configuration file"""
        # Should not raise exception, but log error and use default config
        pm = PromptManager("nonexistent_file.json")
        assert pm is not None
        assert pm._config is not None
        
        # Should still be able to call methods (with default config)
        system_prompt = pm.get_system_prompt(1)
        assert isinstance(system_prompt, str)
    
    def test_initialization_with_invalid_json(self):
        """Test error handling for invalid JSON file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{ invalid json }")
            temp_path = f.name
        
        try:
            with pytest.raises(PromptManagerError, match="Invalid JSON"):
                PromptManager(temp_path)
        finally:
            Path(temp_path).unlink(missing_ok=True)
    
    def test_initialization_with_incomplete_config(self):
        """Test error handling for configuration missing required fields"""
        incomplete_config = {
            "persona": {},
            # Missing prohibited_terms, transition_phrases, turns
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(incomplete_config, f)
            temp_path = f.name
        
        try:
            with pytest.raises(PromptManagerError, match="missing required keys"):
                PromptManager(temp_path)
        finally:
            Path(temp_path).unlink(missing_ok=True)


class TestGetSystemPrompt:
    """Test get_system_prompt() method"""
    
    def test_get_system_prompt_turn_1(self, prompt_manager):
        """Test retrieving system prompt for turn 1"""
        prompt = prompt_manager.get_system_prompt(1)
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "安掌櫃" in prompt
    
    def test_get_system_prompt_turn_2(self, prompt_manager):
        """Test retrieving system prompt for turn 2"""
        prompt = prompt_manager.get_system_prompt(2)
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "安掌櫃" in prompt
    
    def test_get_system_prompt_turn_3(self, prompt_manager):
        """Test retrieving system prompt for turn 3"""
        prompt = prompt_manager.get_system_prompt(3)
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "安掌櫃" in prompt
    
    def test_get_system_prompt_invalid_turn(self, prompt_manager):
        """Test error handling for invalid turn number"""
        with pytest.raises(PromptManagerError, match="Invalid turn number"):
            prompt_manager.get_system_prompt(0)
        
        with pytest.raises(PromptManagerError, match="Invalid turn number"):
            prompt_manager.get_system_prompt(4)
        
        with pytest.raises(PromptManagerError, match="Invalid turn number"):
            prompt_manager.get_system_prompt(-1)
    
    def test_system_prompts_are_different(self, prompt_manager):
        """Test that each turn has a different system prompt"""
        prompt1 = prompt_manager.get_system_prompt(1)
        prompt2 = prompt_manager.get_system_prompt(2)
        prompt3 = prompt_manager.get_system_prompt(3)
        
        # Prompts should be different for each turn
        assert prompt1 != prompt2
        assert prompt2 != prompt3
        assert prompt1 != prompt3


class TestGetConvergenceTarget:
    """Test get_convergence_target() method"""
    
    def test_get_convergence_target_turn_1(self, prompt_manager):
        """Test retrieving convergence target for turn 1"""
        target = prompt_manager.get_convergence_target(1)
        assert isinstance(target, dict)
        assert "point_1" in target
        assert "point_2" in target
        assert "胡餅" in target["point_1"]
        assert "臘肉" in target["point_2"]
    
    def test_get_convergence_target_turn_2(self, prompt_manager):
        """Test retrieving convergence target for turn 2"""
        target = prompt_manager.get_convergence_target(2)
        assert isinstance(target, dict)
        assert "point_1" in target
        assert "point_2" in target
        assert "絲綢" in target["point_1"]
    
    def test_get_convergence_target_turn_3(self, prompt_manager):
        """Test retrieving convergence target for turn 3"""
        target = prompt_manager.get_convergence_target(3)
        assert isinstance(target, dict)
        assert "point_1" in target
        assert "point_2" in target
        assert "品色服" in target["point_1"]
    
    def test_get_convergence_target_invalid_turn(self, prompt_manager):
        """Test error handling for invalid turn number"""
        with pytest.raises(PromptManagerError, match="Invalid turn number"):
            prompt_manager.get_convergence_target(0)
        
        with pytest.raises(PromptManagerError, match="Invalid turn number"):
            prompt_manager.get_convergence_target(5)


class TestGetTransitionPhrases:
    """Test get_transition_phrases() method"""
    
    def test_get_transition_phrases_returns_list(self, prompt_manager):
        """Test that transition phrases are returned as a list"""
        phrases = prompt_manager.get_transition_phrases()
        assert isinstance(phrases, list)
        assert len(phrases) > 0
    
    def test_transition_phrases_content(self, prompt_manager):
        """Test that transition phrases contain expected content"""
        phrases = prompt_manager.get_transition_phrases()
        
        # Should contain at least some Tang dynasty style phrases
        assert any("郎君" in phrase for phrase in phrases)
    
    def test_transition_phrases_returns_copy(self, prompt_manager):
        """Test that method returns a copy, not the original list"""
        phrases1 = prompt_manager.get_transition_phrases()
        phrases2 = prompt_manager.get_transition_phrases()
        
        # Should be equal but not the same object
        assert phrases1 == phrases2
        assert phrases1 is not phrases2


class TestGetProhibitedTerms:
    """Test get_prohibited_terms() method"""
    
    def test_get_prohibited_terms_returns_list(self, prompt_manager):
        """Test that prohibited terms are returned as a list"""
        terms = prompt_manager.get_prohibited_terms()
        assert isinstance(terms, list)
        assert len(terms) > 0
    
    def test_prohibited_terms_content(self, prompt_manager):
        """Test that prohibited terms contain expected modern technology terms"""
        terms = prompt_manager.get_prohibited_terms()
        
        # Check for key prohibited terms
        required_terms = ["微波爐", "冰箱", "拉鍊", "塑膠", "手機"]
        for term in required_terms:
            assert term in terms, f"Required prohibited term '{term}' not found"
    
    def test_prohibited_terms_returns_copy(self, prompt_manager):
        """Test that method returns a copy, not the original list"""
        terms1 = prompt_manager.get_prohibited_terms()
        terms2 = prompt_manager.get_prohibited_terms()
        
        # Should be equal but not the same object
        assert terms1 == terms2
        assert terms1 is not terms2


class TestAdditionalMethods:
    """Test additional helper methods"""
    
    def test_get_persona(self, prompt_manager):
        """Test get_persona() method"""
        persona = prompt_manager.get_persona()
        assert isinstance(persona, dict)
        assert "name" in persona
        assert persona["name"] == "安掌櫃"
    
    def test_get_fallback_response(self, prompt_manager):
        """Test get_fallback_response() method"""
        for turn in [1, 2, 3]:
            fallback = prompt_manager.get_fallback_response(turn)
            assert isinstance(fallback, str)
            assert len(fallback) > 0
    
    def test_get_fallback_response_invalid_turn(self, prompt_manager):
        """Test error handling for invalid turn in fallback response"""
        with pytest.raises(PromptManagerError, match="Invalid turn number"):
            prompt_manager.get_fallback_response(0)
    
    def test_get_preset_options(self, prompt_manager):
        """Test get_preset_options() method"""
        for turn in [1, 2, 3]:
            options = prompt_manager.get_preset_options(turn)
            assert isinstance(options, dict)
            assert "A" in options
            assert "B" in options
            assert isinstance(options["A"], str)
            assert isinstance(options["B"], str)


class TestRealConfiguration:
    """Test with the real prompts.json configuration file"""
    
    def test_real_config_loads_successfully(self, real_config_path):
        """Test that the real configuration file loads without errors"""
        pm = PromptManager(real_config_path)
        assert pm is not None
    
    def test_real_config_all_turns_work(self, real_config_path):
        """Test that all turns work with real configuration"""
        pm = PromptManager(real_config_path)
        
        for turn in [1, 2, 3]:
            # Should not raise exceptions
            system_prompt = pm.get_system_prompt(turn)
            assert len(system_prompt) > 100  # Real prompts should be substantial
            
            convergence_target = pm.get_convergence_target(turn)
            assert "point_1" in convergence_target
            assert "point_2" in convergence_target
    
    def test_real_config_prohibited_terms(self, real_config_path):
        """Test that real configuration has comprehensive prohibited terms list"""
        pm = PromptManager(real_config_path)
        terms = pm.get_prohibited_terms()
        
        # Should have a substantial list of prohibited terms
        assert len(terms) >= 10
        
        # Check for essential prohibited terms
        essential_terms = ["微波爐", "冰箱", "拉鍊", "塑膠", "手機"]
        for term in essential_terms:
            assert term in terms
    
    def test_real_config_transition_phrases(self, real_config_path):
        """Test that real configuration has multiple transition phrases"""
        pm = PromptManager(real_config_path)
        phrases = pm.get_transition_phrases()
        
        # Should have multiple transition phrases
        assert len(phrases) >= 5
    
    def test_real_config_convergence_targets_match_requirements(self, real_config_path):
        """Test that real configuration convergence targets match requirements"""
        pm = PromptManager(real_config_path)
        
        # Turn 1: Food cooking and preservation
        target1 = pm.get_convergence_target(1)
        assert "胡餅" in target1["point_1"]
        assert "臘肉" in target1["point_2"] or "香料" in target1["point_2"]
        
        # Turn 2: Clothing materials and fastening
        target2 = pm.get_convergence_target(2)
        assert "絲綢" in target2["point_1"] or "蜀錦" in target2["point_1"]
        assert "繫帶" in target2["point_2"] or "蹀躞帶" in target2["point_2"]
        
        # Turn 3: Clothing colors and social hierarchy
        target3 = pm.get_convergence_target(3)
        assert "品色服" in target3["point_1"] or "紫" in target3["point_1"]
        assert "禁色" in target3["point_2"] or "紫" in target3["point_2"]


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_missing_turn_in_config(self):
        """Test handling of configuration missing a turn"""
        incomplete_config = {
            "persona": {"name": "安掌櫃"},
            "prohibited_terms": ["微波爐"],
            "transition_phrases": ["哎呀"],
            "turns": {
                "1": {
                    "system_prompt": "Test",
                    "convergence_target": {"point_1": "A", "point_2": "B"}
                },
                # Missing turn 2
                "3": {
                    "system_prompt": "Test",
                    "convergence_target": {"point_1": "A", "point_2": "B"}
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(incomplete_config, f)
            temp_path = f.name
        
        try:
            with pytest.raises(PromptManagerError, match="missing turn"):
                PromptManager(temp_path)
        finally:
            Path(temp_path).unlink(missing_ok=True)
    
    def test_turn_missing_system_prompt(self):
        """Test handling of turn missing system_prompt"""
        incomplete_config = {
            "persona": {"name": "安掌櫃"},
            "prohibited_terms": ["微波爐"],
            "transition_phrases": ["哎呀"],
            "turns": {
                "1": {
                    # Missing system_prompt
                    "convergence_target": {"point_1": "A", "point_2": "B"}
                },
                "2": {
                    "system_prompt": "Test",
                    "convergence_target": {"point_1": "A", "point_2": "B"}
                },
                "3": {
                    "system_prompt": "Test",
                    "convergence_target": {"point_1": "A", "point_2": "B"}
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(incomplete_config, f)
            temp_path = f.name
        
        try:
            with pytest.raises(PromptManagerError, match="missing 'system_prompt'"):
                PromptManager(temp_path)
        finally:
            Path(temp_path).unlink(missing_ok=True)
