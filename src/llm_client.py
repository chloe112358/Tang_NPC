"""LLM Client for Google Gemini API integration"""

import time
from typing import Optional
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions


class APIConnectionError(Exception):
    """Raised when there are network/connection issues with the API"""
    pass


class APIRateLimitError(Exception):
    """Raised when API rate limit is exceeded"""
    pass


class APIAuthError(Exception):
    """Raised when API authentication fails (invalid API key)"""
    pass


class LLMClient:
    """Client for interacting with Google Gemini API"""
    
    def __init__(self, api_key: str, model_name: str = "gemini-3.1-flash-lite"):
        """
        Initialize Gemini API client.
        
        Args:
            api_key: Google Gemini API key
            model_name: Name of the Gemini model to use (default: gemini-3.1-flash-lite)
            
        Raises:
            APIAuthError: If API key is invalid or empty
        """
        if not api_key or not api_key.strip():
            raise APIAuthError("API key cannot be empty")
        
        self.api_key = api_key
        self.model_name = model_name
        
        # Configure the API
        genai.configure(api_key=self.api_key)
        
        # Initialize the model
        try:
            self.model = genai.GenerativeModel(self.model_name)
        except Exception as e:
            raise APIAuthError(f"Failed to initialize model: {str(e)}")
    
    def generate(
        self, 
        prompt: str, 
        temperature: float = 0.7, 
        max_tokens: int = 500
    ) -> str:
        """
        Call Gemini API to generate response with exponential backoff retry.
        
        Args:
            prompt: Full prompt including system instructions
            temperature: Sampling temperature (0.0-1.0, default 0.7)
            max_tokens: Maximum response length (default 500)
            
        Returns:
            Generated text response
            
        Raises:
            APIConnectionError: Network/connection issues after retries
            APIRateLimitError: Rate limit exceeded after retries
            APIAuthError: Invalid API key or authentication failure
        """
        max_attempts = 3
        backoff_delays = [1, 2, 4]  # Exponential backoff: 1s, 2s, 4s
        
        for attempt in range(max_attempts):
            try:
                # Configure generation parameters
                generation_config = genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                )
                
                # Generate response
                response = self.model.generate_content(
                    prompt,
                    generation_config=generation_config
                )
                
                # Extract text from response
                if response.text:
                    return response.text
                else:
                    # Handle blocked or empty responses - don't retry these
                    if hasattr(response, 'prompt_feedback') and response.prompt_feedback:
                        raise APIConnectionError(
                            f"Response blocked: {response.prompt_feedback}"
                        )
                    raise APIConnectionError("Empty response received from API")
                
            except google_exceptions.Unauthenticated as e:
                # Authentication error - don't retry
                raise APIAuthError(f"Authentication failed: {str(e)}")
            
            except google_exceptions.PermissionDenied as e:
                # Permission error - don't retry
                raise APIAuthError(f"Permission denied: {str(e)}")
            
            except APIConnectionError:
                # Empty response or blocked content - don't retry
                raise
            
            except google_exceptions.ResourceExhausted as e:
                # Rate limit error - retry with backoff
                if attempt < max_attempts - 1:
                    delay = backoff_delays[attempt]
                    time.sleep(delay)
                    continue
                else:
                    raise APIRateLimitError(
                        f"Rate limit exceeded after {max_attempts} attempts: {str(e)}"
                    )
            
            except (
                google_exceptions.ServiceUnavailable,
                google_exceptions.DeadlineExceeded,
                google_exceptions.InternalServerError,
                ConnectionError,
                TimeoutError
            ) as e:
                # Connection/network errors - retry with backoff
                if attempt < max_attempts - 1:
                    delay = backoff_delays[attempt]
                    time.sleep(delay)
                    continue
                else:
                    raise APIConnectionError(
                        f"Connection failed after {max_attempts} attempts: {str(e)}"
                    )
            
            except Exception as e:
                # Unexpected error - retry with backoff
                if attempt < max_attempts - 1:
                    delay = backoff_delays[attempt]
                    time.sleep(delay)
                    continue
                else:
                    raise APIConnectionError(
                        f"Unexpected error after {max_attempts} attempts: {str(e)}"
                    )
        
        # Should never reach here, but just in case
        raise APIConnectionError("Failed to generate response after all retry attempts")
