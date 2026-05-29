"""Response Generator for Tang Dynasty Dialogue System"""

import logging
from typing import Optional

from src.llm_client import LLMClient, APIConnectionError, APIRateLimitError, APIAuthError
from src.prompt_manager import PromptManager

logger = logging.getLogger(__name__)


class ResponseGeneratorError(Exception):
    """Base exception for ResponseGenerator-related errors"""
    pass


class ResponseGenerator:
    """
    Generates NPC responses using LLM with turn-specific prompts.
    
    The ResponseGenerator is responsible for:
    - Generating An Shopkeeper's responses using Google Gemini API
    - Applying turn-specific system prompts for convergence
    - Handling persona consistency and modern term detection
    - Providing fallback responses on API failure
    
    Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 8.1, 8.6, 11.2
    """
    
    def __init__(self, llm_client: LLMClient, prompt_manager: PromptManager):
        """
        Initialize ResponseGenerator with LLM client and prompt manager.
        
        Args:
            llm_client: LLMClient instance for API calls
            prompt_manager: PromptManager instance for prompt retrieval
            
        Requirements: 8.1
        """
        self.llm_client = llm_client
        self.prompt_manager = prompt_manager
        logger.info("ResponseGenerator initialized")
    
    def generate_response(self, player_input: str, turn: int) -> str:
        """
        Generate An Shopkeeper's response for given input and turn.
        
        This method:
        1. Builds the full prompt with system instructions
        2. Calls the LLM API to generate response
        3. Validates the response for prohibited terms
        4. Returns fallback response if API fails
        
        Args:
            player_input: Player's question or statement
            turn: Current turn number (1, 2, or 3)
            
        Returns:
            NPC response text in Tang Dynasty style
            
        Raises:
            ResponseGeneratorError: If turn number is invalid
            
        Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 8.6, 11.2
        """
        if turn not in [1, 2, 3]:
            raise ResponseGeneratorError(f"Invalid turn number: {turn}. Must be 1, 2, or 3.")
        
        logger.info(f"Generating response for turn {turn}")
        logger.debug(f"Player input: {player_input}")
        
        try:
            # Build the full prompt with system instructions
            full_prompt = self._build_prompt(player_input, turn)
            logger.debug(f"Built prompt for turn {turn}")
            
            # Call LLM API to generate response
            response = self.llm_client.generate(
                prompt=full_prompt,
                temperature=0.7,
                max_tokens=500
            )
            
            logger.info(f"Successfully generated response from LLM")
            logger.debug(f"LLM response: {response}")
            
            # Validate response doesn't contain prohibited terms
            if not self._validate_response(response):
                logger.warning("Response contains prohibited terms, retrying with lower temperature")
                
                # Retry with lower temperature for more deterministic output
                response = self.llm_client.generate(
                    prompt=full_prompt,
                    temperature=0.5,
                    max_tokens=500
                )
                
                # If still invalid, use fallback
                if not self._validate_response(response):
                    logger.error("Response still contains prohibited terms after retry, using fallback")
                    return self._get_fallback_response(turn)
            
            return response.strip()
            
        except (APIConnectionError, APIRateLimitError, APIAuthError) as e:
            # LLM API failed, use fallback response
            logger.error(f"LLM API error: {type(e).__name__}: {str(e)}")
            logger.info(f"Using fallback response for turn {turn}")
            return self._get_fallback_response(turn)
        
        except Exception as e:
            # Unexpected error, use fallback response
            logger.error(f"Unexpected error generating response: {type(e).__name__}: {str(e)}")
            logger.info(f"Using fallback response for turn {turn}")
            return self._get_fallback_response(turn)
    
    def _build_prompt(self, player_input: str, turn: int) -> str:
        """
        Construct full prompt with system instructions and user input.
        
        The prompt structure:
        1. System prompt with persona, rules, and convergence targets
        2. Player input
        3. Request for response generation
        
        Args:
            player_input: Player's question or statement
            turn: Current turn number (1, 2, or 3)
            
        Returns:
            Complete prompt string ready for LLM API
            
        Requirements: 8.2, 8.3, 8.4
        """
        # Get turn-specific system prompt
        system_prompt = self.prompt_manager.get_system_prompt(turn)
        
        # Construct full prompt
        full_prompt = f"{system_prompt}\n\n現在，玩家說：{player_input}\n\n請生成安掌櫃的回應："
        
        logger.debug(f"Built prompt with {len(full_prompt)} characters")
        return full_prompt
    
    def _validate_response(self, response: str) -> bool:
        """
        Check response doesn't contain prohibited modern terms.
        
        This validation ensures the NPC maintains Tang Dynasty persona
        by avoiding any modern technology vocabulary.
        
        Args:
            response: Generated NPC response text
            
        Returns:
            True if response is valid (no prohibited terms), False otherwise
            
        Requirements: 2.3, 8.5
        """
        if not response:
            logger.warning("Empty response received")
            return False
        
        # Get prohibited terms from prompt manager
        prohibited_terms = self.prompt_manager.get_prohibited_terms()
        
        # Check if any prohibited term appears in response
        response_lower = response.lower()
        for term in prohibited_terms:
            if term in response_lower:
                logger.warning(f"Response contains prohibited term: {term}")
                return False
        
        logger.debug("Response validation passed")
        return True
    
    def _get_fallback_response(self, turn: int) -> str:
        """
        Return pre-written fallback response if API fails.
        
        Fallback responses are pre-written responses that still convey
        the convergence content for each turn, ensuring educational
        goals are met even when the LLM API is unavailable.
        
        Args:
            turn: Current turn number (1, 2, or 3)
            
        Returns:
            Fallback response string for the specified turn
            
        Requirements: 8.6, 11.2
        """
        try:
            fallback = self.prompt_manager.get_fallback_response(turn)
            logger.info(f"Retrieved fallback response for turn {turn}")
            return fallback
        except Exception as e:
            # If even fallback retrieval fails, return a generic message
            logger.error(f"Failed to retrieve fallback response: {str(e)}")
            return "安掌櫃正忙著招呼其他客人，請稍候片刻..."
