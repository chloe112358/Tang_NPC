"""State management for Tang Dynasty Dialogue System"""

from typing import Tuple
from src.models import ConversationState, TurnNumber
from src.storage import StorageBackend, StorageError
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class StateManager:
    """
    Manages conversation state tracking and persistence.
    
    The StateManager is responsible for:
    - Tracking the current turn (1, 2, or 3)
    - Managing conversation completion status
    - Persisting and loading conversation state
    - Maintaining conversation history
    - Handling state transitions between turns
    
    Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 6.1, 6.2, 6.3, 6.4, 6.5, 11.5
    """
    
    DEFAULT_STATE_KEY = "conversation_state"
    
    def __init__(self, storage_backend: StorageBackend, state_key: str = DEFAULT_STATE_KEY):
        """
        Initialize StateManager with a storage backend.
        
        Args:
            storage_backend: Storage backend implementation (FileStorage, MemoryStorage, etc.)
            state_key: Key used to identify the state in storage (default: "conversation_state")
        """
        self.storage_backend = storage_backend
        self.state_key = state_key
        self._state: ConversationState = self._initialize_state()
    
    def _initialize_state(self) -> ConversationState:
        """
        Initialize state by loading from storage or creating default state.
        
        If state load fails, initializes to Turn 1 as default (Requirement 11.5).
        
        Returns:
            ConversationState object (either loaded or newly created)
        """
        try:
            loaded_state = self.load_state()
            if loaded_state is not None:
                logger.info(f"Loaded state from storage: Turn {loaded_state.current_turn.value}")
                return loaded_state
        except StorageError as e:
            logger.warning(f"Failed to load state from storage: {e}. Initializing to Turn 1.")
        
        # Default to Turn 1 if load fails or no state exists (Requirement 1.6, 11.5)
        logger.info("Initializing new conversation state at Turn 1")
        return ConversationState(
            current_turn=TurnNumber.TURN_1,
            is_complete=False,
            conversation_history=[],
            timestamp=datetime.now().isoformat()
        )
    
    def get_current_turn(self) -> int:
        """
        Return current turn number (1-3).
        
        Returns:
            Current turn number as integer (1, 2, or 3)
            
        Requirements: 1.1, 1.2, 1.3
        """
        return self._state.current_turn.value
    
    def advance_turn(self) -> None:
        """
        Move to next turn, mark complete if turn 3 finished.
        
        State transitions:
        - Turn 1 → Turn 2
        - Turn 2 → Turn 3
        - Turn 3 → Complete (is_complete = True)
        
        If already complete, this method has no effect.
        
        Requirements: 1.2, 1.3, 1.4
        """
        if self._state.is_complete:
            logger.warning("Attempted to advance turn when conversation is already complete")
            return
        
        current_turn_value = self._state.current_turn.value
        
        if current_turn_value == 1:
            self._state.current_turn = TurnNumber.TURN_2
            logger.info("Advanced from Turn 1 to Turn 2")
        elif current_turn_value == 2:
            self._state.current_turn = TurnNumber.TURN_3
            logger.info("Advanced from Turn 2 to Turn 3")
        elif current_turn_value == 3:
            self._state.is_complete = True
            logger.info("Completed Turn 3, conversation marked as complete")
        
        # Update timestamp
        self._state.timestamp = datetime.now().isoformat()
        
        # Persist state after advancing turn
        try:
            self.save_state(self._state)
        except StorageError as e:
            logger.error(f"Failed to save state after advancing turn: {e}")
    
    def is_complete(self) -> bool:
        """
        Check if all three turns are finished.
        
        Returns:
            True if conversation is complete (all 3 turns finished), False otherwise
            
        Requirements: 1.4
        """
        return self._state.is_complete
    
    def save_state(self, state: ConversationState) -> None:
        """
        Persist current state to storage.
        
        Args:
            state: ConversationState object to persist
            
        Raises:
            StorageError: If save operation fails
            
        Requirements: 1.5, 6.1
        """
        try:
            state_dict = state.to_dict()
            self.storage_backend.save(self.state_key, state_dict)
            logger.debug(f"Saved state: Turn {state.current_turn.value}, Complete: {state.is_complete}")
        except StorageError as e:
            logger.error(f"Failed to save state: {e}")
            raise
    
    def load_state(self) -> ConversationState:
        """
        Load state from storage, default to Turn 1 if not found.
        
        Returns:
            ConversationState object loaded from storage, or None if not found
            
        Raises:
            StorageError: If load operation fails (excluding key not found)
            
        Requirements: 1.5, 6.2, 11.5
        """
        try:
            state_dict = self.storage_backend.load(self.state_key)
            
            if state_dict is None:
                logger.info("No saved state found in storage")
                return None
            
            state = ConversationState.from_dict(state_dict)
            logger.info(f"Loaded state: Turn {state.current_turn.value}, Complete: {state.is_complete}")
            return state
            
        except StorageError as e:
            logger.error(f"Failed to load state: {e}")
            raise
    
    def reset(self) -> None:
        """
        Reset to Turn 1 and clear history.
        
        This method:
        - Sets current turn to Turn 1
        - Clears conversation history
        - Marks conversation as not complete
        - Persists the reset state
        
        Requirements: 6.3, 6.4, 6.5
        """
        logger.info("Resetting conversation state to Turn 1")
        
        self._state = ConversationState(
            current_turn=TurnNumber.TURN_1,
            is_complete=False,
            conversation_history=[],
            timestamp=datetime.now().isoformat()
        )
        
        # Persist reset state
        try:
            self.save_state(self._state)
        except StorageError as e:
            logger.error(f"Failed to save state after reset: {e}")
    
    def add_to_history(self, player_input: str, npc_response: str) -> None:
        """
        Append interaction to conversation history.
        
        Args:
            player_input: Player's input text
            npc_response: NPC's response text
            
        Requirements: 6.1
        """
        interaction: Tuple[str, str] = (player_input, npc_response)
        self._state.conversation_history.append(interaction)
        self._state.timestamp = datetime.now().isoformat()
        
        logger.debug(f"Added interaction to history (total: {len(self._state.conversation_history)})")
        
        # Persist state after adding to history
        try:
            self.save_state(self._state)
        except StorageError as e:
            logger.error(f"Failed to save state after adding to history: {e}")
    
    def get_state(self) -> ConversationState:
        """
        Get the current conversation state.
        
        Returns:
            Current ConversationState object
        """
        return self._state
    
    def get_conversation_history(self) -> list[Tuple[str, str]]:
        """
        Get the conversation history.
        
        Returns:
            List of (player_input, npc_response) tuples
        """
        return self._state.conversation_history.copy()
