"""Unit tests for ResponseGenerator"""

import pytest
from unittest.mock import Mock, MagicMock, patch
import logging

from src.response_generator import ResponseGenerator, ResponseGeneratorError
from src.llm_client import LLMClient, APIConnectionError, APIRateLimitError, APIAuthError
from src.prompt_manager import PromptManager


@pytest.fixture
def mock_llm_client():
    """Create a mock LLM client"""
    client = Mock(spec=LLMClient)
    return client


@pytest.fixture
def mock_prompt_manager():
    """Create a mock prompt manager with realistic data"""
    manager = Mock(spec=PromptManager)
    
    # Mock system prompts
    manager.get_system_prompt.side_effect = lambda turn: {
        1: "你是安掌櫃，長安西市的粟特人女老闆。本輪收束目標：胡餅現烤現吃、香料醃製臘肉。",
        2: "你是安掌櫃，長安西市的粟特人女老闆。本輪收束目標：絲綢材質優勢、繫帶與蹀躞帶固定方式。",
        3: "你是安掌櫃，長安西市的粟特人女老闆。本輪收束目標：品色服制度、禁色警告。"
    }[turn]
    
    # Mock prohibited terms
    manager.get_prohibited_terms.return_value = [
        '微波爐', '冰箱', '拉鍊', '塑膠', '手機', '電腦',
        '冷藏', '加熱', '魔鬼氈', '尼龍', '聚酯纖維'
    ]
    
    # Mock fallback responses
    manager.get_fallback_response.side_effect = lambda turn: {
        1: "哎呀！郎君這是說什麼傻話？咱們大唐人吃東西的本事有兩套：一是現做現吃——你瞧這胡餅，剛從胡餅爐裡烤出來，燙手的才好吃，放涼了早就被搶光了，誰還帶回去熱？二是香料醃製——鮮肉若吃不完，胡椒、鹽、薑大量抹入做成臘肉，放上數月都不壞，哪裡需要天天用冰鎮著！",
        2: "一拉就合上？郎君的腦袋裡裝的都是些什麼奇巧機關啊！咱們大唐的衣裳，講究的是料子和綁法。料子嘛，蜀錦、絲綢才是天下第一，輕薄透氣、光澤流動，您那衣裳摸著滑溜卻無光氣，差得遠了！綁法呢，靠的是腰間繫帶與蹀躞帶，不但固定衣裳，還能掛刀、掛香囊，俐落又體面，這叫規矩！",
        3: "（嚇得捂住你的嘴）噓！郎君快噤聲！您不想活啦？在長安城，紫、緋（紅）可是三品以上大員才能穿的官服！黃色更是聖上專用！咱們平民百姓就算富可敵國，也只能穿白、黑或粗麻色。要是亂穿上街，可是要被金吾衛抓去打板子的！這品色服制度，可不是鬧著玩的！"
    }[turn]
    
    return manager


@pytest.fixture
def response_generator(mock_llm_client, mock_prompt_manager):
    """Create a ResponseGenerator instance with mocked dependencies"""
    return ResponseGenerator(mock_llm_client, mock_prompt_manager)


class TestResponseGeneratorInitialization:
    """Test ResponseGenerator initialization"""
    
    def test_initialization_success(self, mock_llm_client, mock_prompt_manager):
        """ResponseGenerator initializes successfully with valid dependencies"""
        generator = ResponseGenerator(mock_llm_client, mock_prompt_manager)
        
        assert generator.llm_client == mock_llm_client
        assert generator.prompt_manager == mock_prompt_manager


class TestGenerateResponse:
    """Test generate_response method"""
    
    def test_generate_response_success_turn_1(self, response_generator, mock_llm_client):
        """Successfully generates response for turn 1"""
        # Mock LLM response
        mock_llm_client.generate.return_value = "哎呀！郎君這是說什麼傻話？咱們大唐人吃東西講究現做現吃，胡餅從爐裡烤出來就要趁熱吃！"
        
        response = response_generator.generate_response("這烤餅冷了怎麼辦？", 1)
        
        assert isinstance(response, str)
        assert len(response) > 0
        assert "胡餅" in response or "現做現吃" in response
        mock_llm_client.generate.assert_called_once()
    
    def test_generate_response_success_turn_2(self, response_generator, mock_llm_client):
        """Successfully generates response for turn 2"""
        mock_llm_client.generate.return_value = "郎君有所不知，咱們大唐的衣裳用的是絲綢，靠繫帶固定，俐落又體面！"
        
        response = response_generator.generate_response("你們的衣服怎麼穿？", 2)
        
        assert isinstance(response, str)
        assert len(response) > 0
        mock_llm_client.generate.assert_called_once()
    
    def test_generate_response_success_turn_3(self, response_generator, mock_llm_client):
        """Successfully generates response for turn 3"""
        mock_llm_client.generate.return_value = "噓！郎君快噤聲！紫色可是三品以上大員才能穿的，咱們平民不能亂穿！"
        
        response = response_generator.generate_response("我想買紫色衣服", 3)
        
        assert isinstance(response, str)
        assert len(response) > 0
        mock_llm_client.generate.assert_called_once()
    
    def test_generate_response_invalid_turn_number(self, response_generator):
        """Raises error for invalid turn number"""
        with pytest.raises(ResponseGeneratorError) as exc_info:
            response_generator.generate_response("test input", 0)
        
        assert "Invalid turn number" in str(exc_info.value)
        
        with pytest.raises(ResponseGeneratorError) as exc_info:
            response_generator.generate_response("test input", 4)
        
        assert "Invalid turn number" in str(exc_info.value)
    
    def test_generate_response_strips_whitespace(self, response_generator, mock_llm_client):
        """Response is stripped of leading/trailing whitespace"""
        mock_llm_client.generate.return_value = "  \n  這是回應  \n  "
        
        response = response_generator.generate_response("test", 1)
        
        assert response == "這是回應"
        assert not response.startswith(" ")
        assert not response.endswith(" ")
    
    def test_generate_response_with_preset_option(self, response_generator, mock_llm_client):
        """Handles preset options (A/B) correctly"""
        mock_llm_client.generate.return_value = "哎呀！郎君這是說什麼傻話？"
        
        response = response_generator.generate_response("A", 1)
        
        assert isinstance(response, str)
        assert len(response) > 0
        mock_llm_client.generate.assert_called_once()
    
    def test_generate_response_with_free_text(self, response_generator, mock_llm_client):
        """Handles free text input correctly"""
        mock_llm_client.generate.return_value = "郎君有所不知..."
        
        response = response_generator.generate_response("我想問一個奇怪的問題", 1)
        
        assert isinstance(response, str)
        assert len(response) > 0
        mock_llm_client.generate.assert_called_once()


class TestBuildPrompt:
    """Test _build_prompt method"""
    
    def test_build_prompt_structure(self, response_generator, mock_prompt_manager):
        """Prompt has correct structure with system instructions and player input"""
        player_input = "這烤餅冷了怎麼辦？"
        turn = 1
        
        prompt = response_generator._build_prompt(player_input, turn)
        
        # Verify prompt contains system prompt
        assert "安掌櫃" in prompt
        assert "粟特人" in prompt
        
        # Verify prompt contains player input
        assert player_input in prompt
        
        # Verify prompt has request for response
        assert "請生成安掌櫃的回應" in prompt
        
        # Verify prompt manager was called
        mock_prompt_manager.get_system_prompt.assert_called_once_with(turn)
    
    def test_build_prompt_different_turns(self, response_generator, mock_prompt_manager):
        """Builds different prompts for different turns"""
        prompt_1 = response_generator._build_prompt("test", 1)
        prompt_2 = response_generator._build_prompt("test", 2)
        prompt_3 = response_generator._build_prompt("test", 3)
        
        # Prompts should be different due to different system prompts
        assert prompt_1 != prompt_2
        assert prompt_2 != prompt_3
        assert prompt_1 != prompt_3
        
        # Verify prompt manager was called for each turn
        assert mock_prompt_manager.get_system_prompt.call_count == 3
    
    def test_build_prompt_with_special_characters(self, response_generator):
        """Handles player input with special characters"""
        player_input = "這是什麼？！@#$%^&*()"
        
        prompt = response_generator._build_prompt(player_input, 1)
        
        assert player_input in prompt
        assert isinstance(prompt, str)


class TestValidateResponse:
    """Test _validate_response method"""
    
    def test_validate_response_valid(self, response_generator):
        """Valid response without prohibited terms passes validation"""
        valid_response = "哎呀！郎君這是說什麼傻話？咱們大唐人吃東西講究現做現吃！"
        
        assert response_generator._validate_response(valid_response) is True
    
    def test_validate_response_with_prohibited_term_microwave(self, response_generator):
        """Response with '微波爐' fails validation"""
        invalid_response = "您可以用微波爐加熱。"
        
        assert response_generator._validate_response(invalid_response) is False
    
    def test_validate_response_with_prohibited_term_refrigerator(self, response_generator):
        """Response with '冰箱' fails validation"""
        invalid_response = "放在冰箱裡保存就好了。"
        
        assert response_generator._validate_response(invalid_response) is False
    
    def test_validate_response_with_prohibited_term_zipper(self, response_generator):
        """Response with '拉鍊' fails validation"""
        invalid_response = "用拉鍊固定衣服。"
        
        assert response_generator._validate_response(invalid_response) is False
    
    def test_validate_response_with_prohibited_term_plastic(self, response_generator):
        """Response with '塑膠' fails validation"""
        invalid_response = "這是塑膠做的。"
        
        assert response_generator._validate_response(invalid_response) is False
    
    def test_validate_response_with_prohibited_term_phone(self, response_generator):
        """Response with '手機' fails validation"""
        invalid_response = "用手機聯絡。"
        
        assert response_generator._validate_response(invalid_response) is False
    
    def test_validate_response_with_multiple_prohibited_terms(self, response_generator):
        """Response with multiple prohibited terms fails validation"""
        invalid_response = "用微波爐加熱，然後放冰箱保存。"
        
        assert response_generator._validate_response(invalid_response) is False
    
    def test_validate_response_empty_string(self, response_generator):
        """Empty response fails validation"""
        assert response_generator._validate_response("") is False
    
    def test_validate_response_none(self, response_generator):
        """None response fails validation"""
        assert response_generator._validate_response(None) is False
    
    def test_validate_response_case_insensitive(self, response_generator):
        """Validation is case-insensitive"""
        # Even if prohibited term is in different case, should still fail
        # Note: Chinese characters don't have case, but the validation should handle it
        invalid_response = "用微波爐加熱"
        
        assert response_generator._validate_response(invalid_response) is False


class TestGetFallbackResponse:
    """Test _get_fallback_response method"""
    
    def test_get_fallback_response_turn_1(self, response_generator, mock_prompt_manager):
        """Returns fallback response for turn 1"""
        fallback = response_generator._get_fallback_response(1)
        
        assert isinstance(fallback, str)
        assert len(fallback) > 0
        assert "胡餅" in fallback or "臘肉" in fallback
        mock_prompt_manager.get_fallback_response.assert_called_once_with(1)
    
    def test_get_fallback_response_turn_2(self, response_generator, mock_prompt_manager):
        """Returns fallback response for turn 2"""
        fallback = response_generator._get_fallback_response(2)
        
        assert isinstance(fallback, str)
        assert len(fallback) > 0
        assert "絲綢" in fallback or "繫帶" in fallback or "蹀躞帶" in fallback
        mock_prompt_manager.get_fallback_response.assert_called_once_with(2)
    
    def test_get_fallback_response_turn_3(self, response_generator, mock_prompt_manager):
        """Returns fallback response for turn 3"""
        fallback = response_generator._get_fallback_response(3)
        
        assert isinstance(fallback, str)
        assert len(fallback) > 0
        assert "紫" in fallback or "緋" in fallback or "品色服" in fallback
        mock_prompt_manager.get_fallback_response.assert_called_once_with(3)
    
    def test_get_fallback_response_when_prompt_manager_fails(self, response_generator, mock_prompt_manager):
        """Returns generic message when prompt manager fails"""
        mock_prompt_manager.get_fallback_response.side_effect = Exception("Config error")
        
        fallback = response_generator._get_fallback_response(1)
        
        assert fallback == "安掌櫃正忙著招呼其他客人，請稍候片刻..."


class TestAPIErrorHandling:
    """Test API error handling and fallback behavior"""
    
    def test_generate_response_api_connection_error(self, response_generator, mock_llm_client, mock_prompt_manager):
        """Returns fallback response on API connection error"""
        mock_llm_client.generate.side_effect = APIConnectionError("Network error")
        
        response = response_generator.generate_response("test input", 1)
        
        # Should return fallback response
        assert isinstance(response, str)
        assert len(response) > 0
        mock_prompt_manager.get_fallback_response.assert_called_once_with(1)
    
    def test_generate_response_api_rate_limit_error(self, response_generator, mock_llm_client, mock_prompt_manager):
        """Returns fallback response on API rate limit error"""
        mock_llm_client.generate.side_effect = APIRateLimitError("Rate limit exceeded")
        
        response = response_generator.generate_response("test input", 2)
        
        # Should return fallback response
        assert isinstance(response, str)
        assert len(response) > 0
        mock_prompt_manager.get_fallback_response.assert_called_once_with(2)
    
    def test_generate_response_api_auth_error(self, response_generator, mock_llm_client, mock_prompt_manager):
        """Returns fallback response on API authentication error"""
        mock_llm_client.generate.side_effect = APIAuthError("Invalid API key")
        
        response = response_generator.generate_response("test input", 3)
        
        # Should return fallback response
        assert isinstance(response, str)
        assert len(response) > 0
        mock_prompt_manager.get_fallback_response.assert_called_once_with(3)
    
    def test_generate_response_unexpected_error(self, response_generator, mock_llm_client, mock_prompt_manager):
        """Returns fallback response on unexpected error"""
        mock_llm_client.generate.side_effect = RuntimeError("Unexpected error")
        
        response = response_generator.generate_response("test input", 1)
        
        # Should return fallback response
        assert isinstance(response, str)
        assert len(response) > 0
        mock_prompt_manager.get_fallback_response.assert_called_once_with(1)


class TestProhibitedTermsRetry:
    """Test retry logic when response contains prohibited terms"""
    
    def test_retry_with_lower_temperature_on_prohibited_terms(self, response_generator, mock_llm_client):
        """Retries with lower temperature when response contains prohibited terms"""
        # First call returns response with prohibited term
        # Second call returns valid response
        mock_llm_client.generate.side_effect = [
            "您可以用微波爐加熱。",  # Invalid - contains prohibited term
            "咱們大唐人講究現做現吃！"  # Valid
        ]
        
        response = response_generator.generate_response("test input", 1)
        
        # Should have called generate twice
        assert mock_llm_client.generate.call_count == 2
        
        # Second call should have lower temperature
        second_call_kwargs = mock_llm_client.generate.call_args_list[1][1]
        assert second_call_kwargs['temperature'] == 0.5
        
        # Should return the valid response
        assert "現做現吃" in response
        assert "微波爐" not in response
    
    def test_use_fallback_when_retry_still_has_prohibited_terms(self, response_generator, mock_llm_client, mock_prompt_manager):
        """Uses fallback when retry still contains prohibited terms"""
        # Both calls return responses with prohibited terms
        mock_llm_client.generate.side_effect = [
            "您可以用微波爐加熱。",  # Invalid
            "放在冰箱裡保存。"  # Still invalid
        ]
        
        response = response_generator.generate_response("test input", 1)
        
        # Should have called generate twice
        assert mock_llm_client.generate.call_count == 2
        
        # Should use fallback response
        mock_prompt_manager.get_fallback_response.assert_called_once_with(1)
        assert isinstance(response, str)
        assert len(response) > 0


class TestLLMClientParameters:
    """Test that LLM client is called with correct parameters"""
    
    def test_generate_calls_llm_with_correct_temperature(self, response_generator, mock_llm_client):
        """LLM client is called with temperature 0.7"""
        mock_llm_client.generate.return_value = "Valid response"
        
        response_generator.generate_response("test", 1)
        
        call_kwargs = mock_llm_client.generate.call_args[1]
        assert call_kwargs['temperature'] == 0.7
    
    def test_generate_calls_llm_with_correct_max_tokens(self, response_generator, mock_llm_client):
        """LLM client is called with max_tokens 500"""
        mock_llm_client.generate.return_value = "Valid response"
        
        response_generator.generate_response("test", 1)
        
        call_kwargs = mock_llm_client.generate.call_args[1]
        assert call_kwargs['max_tokens'] == 500
    
    def test_generate_calls_llm_with_built_prompt(self, response_generator, mock_llm_client, mock_prompt_manager):
        """LLM client is called with properly built prompt"""
        mock_llm_client.generate.return_value = "Valid response"
        player_input = "這烤餅冷了怎麼辦？"
        
        response_generator.generate_response(player_input, 1)
        
        # Get the prompt argument from the call
        call_kwargs = mock_llm_client.generate.call_args[1]
        prompt = call_kwargs['prompt']
        
        # Verify prompt contains expected elements
        assert player_input in prompt
        assert "安掌櫃" in prompt
        assert "請生成安掌櫃的回應" in prompt
