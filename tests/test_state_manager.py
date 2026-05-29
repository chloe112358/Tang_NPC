"""Unit tests for StateManager"""

import pytest
from src.state_manager import StateManager
from src.storage import MemoryStorage, FileStorage, StorageError
from src.models import ConversationState, TurnNumber
from datetime import datetime
import tempfile
import os


class TestStateManagerInitialization:
    """Test StateManager initialization behavior"""
    
    def test_initialization_starts_at_turn_1(self):
        """System initializes to Turn 1 (Requirement 1.6)"""
        storage = MemoryStorage()
        state_manager = StateManager(storage)
        
        assert state_manager.get_current_turn() == 1
        assert not state_manager.is_complete()
    
    def test_initialization_with_empty_history(self):
        """New StateManager has empty conversation history"""
        storage = MemoryStorage()
        state_manager = StateManager(storage)
        
        history = state_manager.get_conversation_history()
        assert len(history) == 0
    
    def test_initialization_loads_existing_state(self):
        """StateManager loads existing state from storage"""
        storage = MemoryStorage()
        
        # Save a state at Turn 2
        existing_state = ConversationState(
            current_turn=TurnNumber.TURN_2,
            is_complete=False,
            conversation_history=[("input1", "response1")],
            timestamp=datetime.now().isoformat()
        )
        storage.save("conversation_state", existing_state.to_dict())
        
        # Create new StateManager - should load existing state
        state_manager = StateManager(storage)
        
        assert state_manager.get_current_turn() == 2
        assert len(state_manager.get_conversation_history()) == 1
    
    def test_initialization_defaults_to_turn_1_on_load_failure(self):
        """StateManager defaults to Turn 1 if state load fails (Requirement 11.5)"""
        # Use FileStorage with a non-existent directory to simulate load failure
        storage = MemoryStorage()
        
        # Don't save any state - load will return None
        state_manager = StateManager(storage)
        
        # Should default to Turn 1
        assert state_manager.get_current_turn() == 1
        assert not state_manager.is_complete()


class TestStateManagerTurnProgression:
    """Test turn advancement and state transitions"""
    
    def test_advance_turn_from_1_to_2(self):
        """Advancing from Turn 1 moves to Turn 2 (Requirement 1.2)"""
        storage = MemoryStorage()
        state_manager = StateManager(storage)
        
        assert state_manager.get_current_turn() == 1
        
        state_manager.advance_turn()
        
        assert state_manager.get_current_turn() == 2
        assert not state_manager.is_complete()
    
    def test_advance_turn_from_2_to_3(self):
        """Advancing from Turn 2 moves to Turn 3 (Requirement 1.3)"""
        storage = MemoryStorage()
        state_manager = StateManager(storage)
        
        # Advance to Turn 2
        state_manager.advance_turn()
        assert state_manager.get_current_turn() == 2
        
        # Advance to Turn 3
        state_manager.advance_turn()
        
        assert state_manager.get_current_turn() == 3
        assert not state_manager.is_complete()
    
    def test_advance_turn_from_3_marks_complete(self):
        """Advancing from Turn 3 marks conversation as complete (Requirement 1.4)"""
        storage = MemoryStorage()
        state_manager = StateManager(storage)
        
        # Advance through all turns
        state_manager.advance_turn()  # Turn 1 → 2
        state_manager.advance_turn()  # Turn 2 → 3
        
        assert state_manager.get_current_turn() == 3
        assert not state_manager.is_complete()
        
        # Advance from Turn 3
        state_manager.advance_turn()
        
        assert state_manager.get_current_turn() == 3  # Stays at Turn 3
        assert state_manager.is_complete()
    
    def test_advance_turn_when_already_complete_has_no_effect(self):
        """Advancing when already complete has no effect"""
        storage = MemoryStorage()
        state_manager = StateManager(storage)
        
        # Advance to completion
        state_manager.advance_turn()
        state_manager.advance_turn()
        state_manager.advance_turn()
        
        assert state_manager.is_complete()
        
        # Try to advance again
        state_manager.advance_turn()
        
        # Should still be complete at Turn 3
        assert state_manager.get_current_turn() == 3
        assert state_manager.is_complete()
    
    def test_is_complete_returns_false_before_turn_3(self):
        """is_complete returns False before Turn 3 is finished"""
        storage = MemoryStorage()
        state_manager = StateManager(storage)
        
        assert not state_manager.is_complete()
        
        state_manager.advance_turn()  # Turn 2
        assert not state_manager.is_complete()
        
        state_manager.advance_turn()  # Turn 3
        assert not state_manager.is_complete()
    
    def test_is_complete_returns_true_after_turn_3(self):
        """is_complete returns True only after Turn 3 is finished (Requirement 1.4)"""
        storage = MemoryStorage()
        state_manager = StateManager(storage)
        
        # Advance through all turns
        state_manager.advance_turn()
        state_manager.advance_turn()
        state_manager.advance_turn()
        
        assert state_manager.is_complete()


class TestStateManagerPersistence:
    """Test state saving and loading"""
    
    def test_save_state_persists_to_storage(self):
        """save_state persists state to storage (Requirement 6.1)"""
        storage = MemoryStorage()
        state_manager = StateManager(storage)
        
        # Advance turn
        state_manager.advance_turn()
        
        # Load state directly from storage
        saved_data = storage.load("conversation_state")
        
        assert saved_data is not None
        assert saved_data['current_turn'] == 2
    
    def test_load_state_retrieves_from_storage(self):
        """load_state retrieves state from storage (Requirement 6.2)"""
        storage = MemoryStorage()
        
        # Save a state directly to storage
        state_dict = {
            'current_turn': 3,
            'is_complete': False,
            'conversation_history': [("q1", "a1"), ("q2", "a2")],
            'timestamp': datetime.now().isoformat()
        }
        storage.save("conversation_state", state_dict)
        
        # Create StateManager - should load the saved state
        state_manager = StateManager(storage)
        
        assert state_manager.get_current_turn() == 3
        assert len(state_manager.get_conversation_history()) == 2
    
    def test_state_persists_after_advance_turn(self):
        """State is automatically persisted after advancing turn"""
        storage = MemoryStorage()
        state_manager = StateManager(storage)
        
        state_manager.advance_turn()
        
        # Create new StateManager - should load persisted state
        new_state_manager = StateManager(storage)
        
        assert new_state_manager.get_current_turn() == 2
    
    def test_file_storage_persistence(self):
        """State persists correctly with FileStorage backend"""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = FileStorage(tmpdir)
            state_manager = StateManager(storage)
            
            # Advance and add history
            state_manager.advance_turn()
            state_manager.add_to_history("test input", "test response")
            
            # Create new StateManager with same storage
            new_state_manager = StateManager(storage)
            
            assert new_state_manager.get_current_turn() == 2
            assert len(new_state_manager.get_conversation_history()) == 1


class TestStateManagerReset:
    """Test reset functionality"""
    
    def test_reset_returns_to_turn_1(self):
        """Reset sets current turn to Turn 1 (Requirement 6.4)"""
        storage = MemoryStorage()
        state_manager = StateManager(storage)
        
        # Advance to Turn 3
        state_manager.advance_turn()
        state_manager.advance_turn()
        
        assert state_manager.get_current_turn() == 3
        
        # Reset
        state_manager.reset()
        
        assert state_manager.get_current_turn() == 1
    
    def test_reset_clears_history(self):
        """Reset clears conversation history (Requirement 6.5)"""
        storage = MemoryStorage()
        state_manager = StateManager(storage)
        
        # Add some history
        state_manager.add_to_history("input1", "response1")
        state_manager.add_to_history("input2", "response2")
        
        assert len(state_manager.get_conversation_history()) == 2
        
        # Reset
        state_manager.reset()
        
        assert len(state_manager.get_conversation_history()) == 0
    
    def test_reset_clears_completion_status(self):
        """Reset marks conversation as not complete (Requirement 6.3)"""
        storage = MemoryStorage()
        state_manager = StateManager(storage)
        
        # Complete the conversation
        state_manager.advance_turn()
        state_manager.advance_turn()
        state_manager.advance_turn()
        
        assert state_manager.is_complete()
        
        # Reset
        state_manager.reset()
        
        assert not state_manager.is_complete()
    
    def test_reset_persists_to_storage(self):
        """Reset state is persisted to storage"""
        storage = MemoryStorage()
        state_manager = StateManager(storage)
        
        # Advance and add history
        state_manager.advance_turn()
        state_manager.add_to_history("input", "response")
        
        # Reset
        state_manager.reset()
        
        # Create new StateManager - should load reset state
        new_state_manager = StateManager(storage)
        
        assert new_state_manager.get_current_turn() == 1
        assert len(new_state_manager.get_conversation_history()) == 0
        assert not new_state_manager.is_complete()


class TestStateManagerHistory:
    """Test conversation history management"""
    
    def test_add_to_history_appends_interaction(self):
        """add_to_history appends interaction to history (Requirement 6.1)"""
        storage = MemoryStorage()
        state_manager = StateManager(storage)
        
        state_manager.add_to_history("player input", "npc response")
        
        history = state_manager.get_conversation_history()
        assert len(history) == 1
        assert history[0] == ("player input", "npc response")
    
    def test_add_to_history_maintains_order(self):
        """add_to_history maintains chronological order"""
        storage = MemoryStorage()
        state_manager = StateManager(storage)
        
        state_manager.add_to_history("input1", "response1")
        state_manager.add_to_history("input2", "response2")
        state_manager.add_to_history("input3", "response3")
        
        history = state_manager.get_conversation_history()
        assert len(history) == 3
        assert history[0] == ("input1", "response1")
        assert history[1] == ("input2", "response2")
        assert history[2] == ("input3", "response3")
    
    def test_add_to_history_persists_to_storage(self):
        """History is automatically persisted after adding"""
        storage = MemoryStorage()
        state_manager = StateManager(storage)
        
        state_manager.add_to_history("test", "response")
        
        # Create new StateManager - should load persisted history
        new_state_manager = StateManager(storage)
        
        history = new_state_manager.get_conversation_history()
        assert len(history) == 1
        assert history[0] == ("test", "response")
    
    def test_get_conversation_history_returns_copy(self):
        """get_conversation_history returns a copy to prevent external modification"""
        storage = MemoryStorage()
        state_manager = StateManager(storage)
        
        state_manager.add_to_history("input", "response")
        
        history = state_manager.get_conversation_history()
        history.append(("modified", "modified"))
        
        # Original history should be unchanged
        actual_history = state_manager.get_conversation_history()
        assert len(actual_history) == 1


class TestStateManagerEdgeCases:
    """Test edge cases and error handling"""
    
    def test_custom_state_key(self):
        """StateManager can use custom state key"""
        storage = MemoryStorage()
        state_manager = StateManager(storage, state_key="custom_key")
        
        state_manager.advance_turn()
        
        # Check that state is saved under custom key
        saved_data = storage.load("custom_key")
        assert saved_data is not None
        assert saved_data['current_turn'] == 2
    
    def test_get_state_returns_current_state(self):
        """get_state returns the current ConversationState object"""
        storage = MemoryStorage()
        state_manager = StateManager(storage)
        
        state_manager.advance_turn()
        state_manager.add_to_history("input", "response")
        
        state = state_manager.get_state()
        
        assert isinstance(state, ConversationState)
        assert state.current_turn == TurnNumber.TURN_2
        assert len(state.conversation_history) == 1
    
    def test_timestamp_updates_on_state_changes(self):
        """Timestamp is updated when state changes"""
        storage = MemoryStorage()
        state_manager = StateManager(storage)
        
        initial_state = state_manager.get_state()
        initial_timestamp = initial_state.timestamp
        
        # Wait a tiny bit and make a change
        import time
        time.sleep(0.01)
        
        state_manager.advance_turn()
        
        updated_state = state_manager.get_state()
        updated_timestamp = updated_state.timestamp
        
        # Timestamps should be different
        assert updated_timestamp != initial_timestamp


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
