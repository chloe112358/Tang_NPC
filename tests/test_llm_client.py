"""Unit tests for LLMClient"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.llm_client import LLMClient, APIConnectionError, APIRateLimitError, APIAuthError
from google.api_core import exceptions as google_exceptions


class TestLLMClientInitialization:
    """Test LLMClient initialization"""
    
    def test_init_with_valid_api_key(self):
        """Test initialization with valid API key"""
        with patch('src.llm_client.genai.configure'):
            with patch('src.llm_client.genai.GenerativeModel') as mock_model:
                client = LLMClient(api_key="test_key", model_name="gemini-3.1-flash-lite")
                assert client.api_key == "test_key"
                assert client.model_name == "gemini-3.1-flash-lite"
                mock_model.assert_called_once_with("gemini-3.1-flash-lite")
    
    def test_init_with_empty_api_key(self):
        """Test initialization with empty API key raises APIAuthError"""
        with pytest.raises(APIAuthError, match="API key cannot be empty"):
            LLMClient(api_key="", model_name="gemini-3.1-flash-lite")
    
    def test_init_with_whitespace_api_key(self):
        """Test initialization with whitespace-only API key raises APIAuthError"""
        with pytest.raises(APIAuthError, match="API key cannot be empty"):
            LLMClient(api_key="   ", model_name="gemini-3.1-flash-lite")
    
    def test_init_with_default_model_name(self):
        """Test initialization uses default model name"""
        with patch('src.llm_client.genai.configure'):
            with patch('src.llm_client.genai.GenerativeModel') as mock_model:
                client = LLMClient(api_key="test_key")
                assert client.model_name == "gemini-3.1-flash-lite"


class TestLLMClientGenerate:
    """Test LLMClient generate method"""
    
    @patch('src.llm_client.genai.configure')
    @patch('src.llm_client.genai.GenerativeModel')
    def test_generate_success(self, mock_model_class, mock_configure):
        """Test successful generation with valid prompt"""
        # Setup mock
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = "Generated response text"
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        
        # Test
        client = LLMClient(api_key="test_key")
        result = client.generate(prompt="Test prompt", temperature=0.7, max_tokens=500)
        
        assert result == "Generated response text"
        mock_model.generate_content.assert_called_once()
    
    @patch('src.llm_client.genai.configure')
    @patch('src.llm_client.genai.GenerativeModel')
    def test_generate_with_custom_parameters(self, mock_model_class, mock_configure):
        """Test generation with custom temperature and max_tokens"""
        # Setup mock
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = "Response"
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        
        # Test
        client = LLMClient(api_key="test_key")
        result = client.generate(prompt="Test", temperature=0.5, max_tokens=300)
        
        assert result == "Response"
        # Verify generation_config was passed
        call_args = mock_model.generate_content.call_args
        assert call_args is not None
    
    @patch('src.llm_client.genai.configure')
    @patch('src.llm_client.genai.GenerativeModel')
    def test_generate_authentication_error(self, mock_model_class, mock_configure):
        """Test APIAuthError is raised on authentication failure"""
        # Setup mock
        mock_model = Mock()
        mock_model.generate_content.side_effect = google_exceptions.Unauthenticated("Invalid API key")
        mock_model_class.return_value = mock_model
        
        # Test
        client = LLMClient(api_key="test_key")
        with pytest.raises(APIAuthError, match="Authentication failed"):
            client.generate(prompt="Test")
    
    @patch('src.llm_client.genai.configure')
    @patch('src.llm_client.genai.GenerativeModel')
    def test_generate_permission_denied_error(self, mock_model_class, mock_configure):
        """Test APIAuthError is raised on permission denied"""
        # Setup mock
        mock_model = Mock()
        mock_model.generate_content.side_effect = google_exceptions.PermissionDenied("Permission denied")
        mock_model_class.return_value = mock_model
        
        # Test
        client = LLMClient(api_key="test_key")
        with pytest.raises(APIAuthError, match="Permission denied"):
            client.generate(prompt="Test")
    
    @patch('src.llm_client.genai.configure')
    @patch('src.llm_client.genai.GenerativeModel')
    @patch('src.llm_client.time.sleep')  # Mock sleep to speed up test
    def test_generate_rate_limit_error_with_retry(self, mock_sleep, mock_model_class, mock_configure):
        """Test APIRateLimitError is raised after retries on rate limit"""
        # Setup mock
        mock_model = Mock()
        mock_model.generate_content.side_effect = google_exceptions.ResourceExhausted("Rate limit exceeded")
        mock_model_class.return_value = mock_model
        
        # Test
        client = LLMClient(api_key="test_key")
        with pytest.raises(APIRateLimitError, match="Rate limit exceeded after 3 attempts"):
            client.generate(prompt="Test")
        
        # Verify retries happened (3 attempts total)
        assert mock_model.generate_content.call_count == 3
        # Verify exponential backoff (2 sleeps: 1s, 2s)
        assert mock_sleep.call_count == 2
        mock_sleep.assert_any_call(1)
        mock_sleep.assert_any_call(2)
    
    @patch('src.llm_client.genai.configure')
    @patch('src.llm_client.genai.GenerativeModel')
    @patch('src.llm_client.time.sleep')
    def test_generate_connection_error_with_retry(self, mock_sleep, mock_model_class, mock_configure):
        """Test APIConnectionError is raised after retries on connection failure"""
        # Setup mock
        mock_model = Mock()
        mock_model.generate_content.side_effect = ConnectionError("Network error")
        mock_model_class.return_value = mock_model
        
        # Test
        client = LLMClient(api_key="test_key")
        with pytest.raises(APIConnectionError, match="Connection failed after 3 attempts"):
            client.generate(prompt="Test")
        
        # Verify retries happened
        assert mock_model.generate_content.call_count == 3
        assert mock_sleep.call_count == 2
    
    @patch('src.llm_client.genai.configure')
    @patch('src.llm_client.genai.GenerativeModel')
    @patch('src.llm_client.time.sleep')
    def test_generate_retry_success_on_second_attempt(self, mock_sleep, mock_model_class, mock_configure):
        """Test successful generation after one retry"""
        # Setup mock - fail first, succeed second
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = "Success after retry"
        mock_model.generate_content.side_effect = [
            ConnectionError("Network error"),
            mock_response
        ]
        mock_model_class.return_value = mock_model
        
        # Test
        client = LLMClient(api_key="test_key")
        result = client.generate(prompt="Test")
        
        assert result == "Success after retry"
        assert mock_model.generate_content.call_count == 2
        assert mock_sleep.call_count == 1
        mock_sleep.assert_called_once_with(1)  # First backoff delay
    
    @patch('src.llm_client.genai.configure')
    @patch('src.llm_client.genai.GenerativeModel')
    def test_generate_empty_response_error(self, mock_model_class, mock_configure):
        """Test APIConnectionError is raised on empty response"""
        # Setup mock
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = None
        mock_response.prompt_feedback = None
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        
        # Test
        client = LLMClient(api_key="test_key")
        with pytest.raises(APIConnectionError, match="Empty response received"):
            client.generate(prompt="Test")
    
    @patch('src.llm_client.genai.configure')
    @patch('src.llm_client.genai.GenerativeModel')
    @patch('src.llm_client.time.sleep')
    def test_exponential_backoff_delays(self, mock_sleep, mock_model_class, mock_configure):
        """Test exponential backoff uses correct delays: 1s, 2s, 4s"""
        # Setup mock
        mock_model = Mock()
        mock_model.generate_content.side_effect = ConnectionError("Network error")
        mock_model_class.return_value = mock_model
        
        # Test
        client = LLMClient(api_key="test_key")
        with pytest.raises(APIConnectionError):
            client.generate(prompt="Test")
        
        # Verify exponential backoff delays
        assert mock_sleep.call_count == 2  # 2 sleeps for 3 attempts
        calls = [call[0][0] for call in mock_sleep.call_args_list]
        assert calls == [1, 2]  # First retry: 1s, second retry: 2s


class TestLLMClientErrorHandling:
    """Test LLMClient error handling"""
    
    @patch('src.llm_client.genai.configure')
    @patch('src.llm_client.genai.GenerativeModel')
    @patch('src.llm_client.time.sleep')
    def test_service_unavailable_retry(self, mock_sleep, mock_model_class, mock_configure):
        """Test retry on ServiceUnavailable error"""
        mock_model = Mock()
        mock_model.generate_content.side_effect = google_exceptions.ServiceUnavailable("Service unavailable")
        mock_model_class.return_value = mock_model
        
        client = LLMClient(api_key="test_key")
        with pytest.raises(APIConnectionError, match="Connection failed after 3 attempts"):
            client.generate(prompt="Test")
        
        assert mock_model.generate_content.call_count == 3
    
    @patch('src.llm_client.genai.configure')
    @patch('src.llm_client.genai.GenerativeModel')
    @patch('src.llm_client.time.sleep')
    def test_deadline_exceeded_retry(self, mock_sleep, mock_model_class, mock_configure):
        """Test retry on DeadlineExceeded error"""
        mock_model = Mock()
        mock_model.generate_content.side_effect = google_exceptions.DeadlineExceeded("Timeout")
        mock_model_class.return_value = mock_model
        
        client = LLMClient(api_key="test_key")
        with pytest.raises(APIConnectionError, match="Connection failed after 3 attempts"):
            client.generate(prompt="Test")
        
        assert mock_model.generate_content.call_count == 3
    
    @patch('src.llm_client.genai.configure')
    @patch('src.llm_client.genai.GenerativeModel')
    @patch('src.llm_client.time.sleep')
    def test_internal_server_error_retry(self, mock_sleep, mock_model_class, mock_configure):
        """Test retry on InternalServerError"""
        mock_model = Mock()
        mock_model.generate_content.side_effect = google_exceptions.InternalServerError("Internal error")
        mock_model_class.return_value = mock_model
        
        client = LLMClient(api_key="test_key")
        with pytest.raises(APIConnectionError, match="Connection failed after 3 attempts"):
            client.generate(prompt="Test")
        
        assert mock_model.generate_content.call_count == 3
