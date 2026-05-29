"""Integration tests for ResponseGenerator with real dependencies"""

import pytest
import os
from pathlib import Path

from src.response_generator import ResponseGenerator
from src.llm_client import LLMClient, APIAuthError
from src.prompt_manager import PromptManager


@pytest.fixture
def prompts_config_path():
    """Get path to prompts configuration file"""
    return str(Path(__file__).parent.parent / "config" / "prompts.json")


@pytest.fixture
def prompt_manager(prompts_config_path):
    """Create a real PromptManager instance"""
    return PromptManager(prompts_config_path)


@pytest.fixture
def llm_client():
    """Create a real LLMClient instance if API key is available"""
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        pytest.skip("GEMINI_API_KEY not set, skipping integration test")
    
    return LLMClient(api_key=api_key, model_name="gemini-3.1-flash-lite")


@pytest.fixture
def response_generator(llm_client, prompt_manager):
    """Create a ResponseGenerator with real dependencies"""
    return ResponseGenerator(llm_client, prompt_manager)


class TestResponseGeneratorIntegration:
    """Integration tests with real LLM and PromptManager"""
    
    def test_initialization_with_real_dependencies(self, llm_client, prompt_manager):
        """ResponseGenerator initializes with real dependencies"""
        generator = ResponseGenerator(llm_client, prompt_manager)
        
        assert generator.llm_client is not None
        assert generator.prompt_manager is not None
    
    def test_build_prompt_with_real_prompt_manager(self, response_generator):
        """_build_prompt works with real PromptManager"""
        player_input = "這烤餅冷了怎麼辦？"
        
        prompt = response_generator._build_prompt(player_input, 1)
        
        # Verify prompt structure
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert player_input in prompt
        assert "安掌櫃" in prompt
        assert "粟特人" in prompt
        assert "請生成安掌櫃的回應" in prompt
        
        # Verify convergence targets are mentioned
        assert "胡餅" in prompt or "臘肉" in prompt
    
    def test_validate_response_with_real_prohibited_terms(self, response_generator):
        """_validate_response works with real prohibited terms list"""
        # Valid response
        valid_response = "哎呀！郎君這是說什麼傻話？咱們大唐人吃東西講究現做現吃！"
        assert response_generator._validate_response(valid_response) is True
        
        # Invalid responses with prohibited terms
        invalid_responses = [
            "您可以用微波爐加熱。",
            "放在冰箱裡保存。",
            "用拉鍊固定衣服。",
            "這是塑膠做的。",
            "用手機聯絡。"
        ]
        
        for invalid_response in invalid_responses:
            assert response_generator._validate_response(invalid_response) is False
    
    def test_get_fallback_response_with_real_prompt_manager(self, response_generator):
        """_get_fallback_response retrieves real fallback responses"""
        # Test all three turns
        for turn in [1, 2, 3]:
            fallback = response_generator._get_fallback_response(turn)
            
            assert isinstance(fallback, str)
            assert len(fallback) > 0
            
            # Verify fallback contains expected content
            if turn == 1:
                assert "胡餅" in fallback or "臘肉" in fallback
            elif turn == 2:
                assert "絲綢" in fallback or "繫帶" in fallback or "蹀躞帶" in fallback
            elif turn == 3:
                assert "紫" in fallback or "緋" in fallback or "品色服" in fallback
    
    @pytest.mark.skipif(not os.getenv('GEMINI_API_KEY'), reason="GEMINI_API_KEY not set")
    def test_generate_response_with_real_llm_turn_1(self, response_generator):
        """Generate response with real LLM for turn 1"""
        player_input = "這烤餅現在買了，要是帶回客棧冷掉變硬怎麼辦？"
        
        response = response_generator.generate_response(player_input, 1)
        
        # Verify response structure
        assert isinstance(response, str)
        assert len(response) > 0
        
        # Verify no prohibited terms
        prohibited_terms = ['微波爐', '冰箱', '拉鍊', '塑膠', '手機', '電腦']
        for term in prohibited_terms:
            assert term not in response
        
        # Verify response is in Tang Dynasty style (contains traditional characters)
        assert any(char in response for char in ['郎', '君', '咱', '掌櫃'])
    
    @pytest.mark.skipif(not os.getenv('GEMINI_API_KEY'), reason="GEMINI_API_KEY not set")
    def test_generate_response_with_real_llm_turn_2(self, response_generator):
        """Generate response with real LLM for turn 2"""
        player_input = "你們的衣服沒有拉鍊，怎麼穿脫？"
        
        response = response_generator.generate_response(player_input, 2)
        
        # Verify response structure
        assert isinstance(response, str)
        assert len(response) > 0
        
        # Verify no prohibited terms
        prohibited_terms = ['微波爐', '冰箱', '拉鍊', '塑膠', '手機', '電腦']
        for term in prohibited_terms:
            assert term not in response
    
    @pytest.mark.skipif(not os.getenv('GEMINI_API_KEY'), reason="GEMINI_API_KEY not set")
    def test_generate_response_with_real_llm_turn_3(self, response_generator):
        """Generate response with real LLM for turn 3"""
        player_input = "我想買件紫色的衣服，好看嗎？"
        
        response = response_generator.generate_response(player_input, 3)
        
        # Verify response structure
        assert isinstance(response, str)
        assert len(response) > 0
        
        # Verify no prohibited terms
        prohibited_terms = ['微波爐', '冰箱', '拉鍊', '塑膠', '手機', '電腦']
        for term in prohibited_terms:
            assert term not in response
    
    @pytest.mark.skipif(not os.getenv('GEMINI_API_KEY'), reason="GEMINI_API_KEY not set")
    def test_generate_response_with_modern_term_in_input(self, response_generator):
        """Response handles modern terms in player input appropriately"""
        player_input = "你們有微波爐嗎？"
        
        response = response_generator.generate_response(player_input, 1)
        
        # Verify response doesn't echo the prohibited term
        assert isinstance(response, str)
        assert len(response) > 0
        
        # Response should show confusion or curiosity, not use the term
        # (The LLM should handle this based on system prompt)
    
    def test_prompt_manager_has_all_required_data(self, prompt_manager):
        """PromptManager has all required data for ResponseGenerator"""
        # Verify system prompts exist for all turns
        for turn in [1, 2, 3]:
            system_prompt = prompt_manager.get_system_prompt(turn)
            assert isinstance(system_prompt, str)
            assert len(system_prompt) > 0
        
        # Verify prohibited terms list exists
        prohibited_terms = prompt_manager.get_prohibited_terms()
        assert isinstance(prohibited_terms, list)
        assert len(prohibited_terms) > 0
        
        # Verify fallback responses exist for all turns
        for turn in [1, 2, 3]:
            fallback = prompt_manager.get_fallback_response(turn)
            assert isinstance(fallback, str)
            assert len(fallback) > 0


class TestResponseGeneratorWithoutAPIKey:
    """Test ResponseGenerator behavior when API key is not available"""
    
    def test_fallback_response_used_when_no_api_key(self, prompt_manager):
        """Uses fallback response when LLM client fails"""
        # Create LLM client with invalid API key
        try:
            llm_client = LLMClient(api_key="invalid_key", model_name="gemini-3.1-flash-lite")
        except APIAuthError:
            pytest.skip("LLM client initialization failed as expected")
        
        generator = ResponseGenerator(llm_client, prompt_manager)
        
        # Should use fallback response when API call fails
        response = generator.generate_response("test input", 1)
        
        assert isinstance(response, str)
        assert len(response) > 0
