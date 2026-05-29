"""Unit tests for storage backends"""

import pytest
import os
import json
import tempfile
import shutil
from src.storage import StorageBackend, StorageError, FileStorage, MemoryStorage


class TestFileStorage:
    """Test suite for FileStorage backend"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing"""
        temp_path = tempfile.mkdtemp()
        yield temp_path
        # Cleanup after test
        shutil.rmtree(temp_path, ignore_errors=True)
    
    @pytest.fixture
    def file_storage(self, temp_dir):
        """Create a FileStorage instance with temporary directory"""
        return FileStorage(base_path=temp_dir)
    
    def test_save_and_load_roundtrip(self, file_storage):
        """Test that saving and loading data preserves all information"""
        test_data = {
            'current_turn': 1,
            'is_complete': False,
            'conversation_history': [('player input', 'npc response')],
            'timestamp': '2024-01-01T12:00:00'
        }
        
        file_storage.save('test_key', test_data)
        loaded_data = file_storage.load('test_key')
        
        # Note: JSON serialization converts tuples to lists, which is expected behavior
        # The application layer (ConversationState.from_dict) handles this conversion
        assert loaded_data['current_turn'] == test_data['current_turn']
        assert loaded_data['is_complete'] == test_data['is_complete']
        assert loaded_data['timestamp'] == test_data['timestamp']
        # Verify conversation history content is preserved (tuples become lists in JSON)
        assert loaded_data['conversation_history'] == [['player input', 'npc response']]
    
    def test_load_nonexistent_key_returns_none(self, file_storage):
        """Test that loading a non-existent key returns None"""
        result = file_storage.load('nonexistent_key')
        assert result is None
    
    def test_delete_existing_key(self, file_storage):
        """Test deleting an existing key"""
        test_data = {'key': 'value'}
        file_storage.save('test_key', test_data)
        
        # Verify it exists
        assert file_storage.load('test_key') is not None
        
        # Delete it
        file_storage.delete('test_key')
        
        # Verify it's gone
        assert file_storage.load('test_key') is None
    
    def test_delete_nonexistent_key_succeeds(self, file_storage):
        """Test that deleting a non-existent key doesn't raise an error"""
        # Should not raise an exception
        file_storage.delete('nonexistent_key')
    
    def test_save_overwrites_existing_data(self, file_storage):
        """Test that saving with the same key overwrites previous data"""
        file_storage.save('test_key', {'version': 1})
        file_storage.save('test_key', {'version': 2})
        
        loaded_data = file_storage.load('test_key')
        assert loaded_data == {'version': 2}
    
    def test_sanitize_key_with_invalid_characters(self, file_storage):
        """Test that keys with invalid filename characters are sanitized"""
        test_data = {'test': 'data'}
        
        # Keys with invalid characters should be sanitized
        file_storage.save('test:key/with*invalid?chars', test_data)
        loaded_data = file_storage.load('test:key/with*invalid?chars')
        
        assert loaded_data == test_data
    
    def test_corrupted_json_raises_storage_error(self, file_storage, temp_dir):
        """Test that corrupted JSON file raises StorageError"""
        # Create a corrupted JSON file
        corrupted_file = os.path.join(temp_dir, 'corrupted.json')
        with open(corrupted_file, 'w') as f:
            f.write('{ invalid json content }')
        
        with pytest.raises(StorageError) as exc_info:
            file_storage.load('corrupted')
        
        assert 'Corrupted JSON' in str(exc_info.value)
    
    def test_atomic_write_creates_file(self, file_storage, temp_dir):
        """Test that atomic write creates the file correctly"""
        test_data = {'atomic': 'write'}
        file_storage.save('atomic_test', test_data)
        
        # Verify file exists and contains correct data
        file_path = os.path.join(temp_dir, 'atomic_test.json')
        assert os.path.exists(file_path)
        
        with open(file_path, 'r') as f:
            loaded = json.load(f)
        
        assert loaded == test_data
    
    def test_unicode_data_handling(self, file_storage):
        """Test that Unicode data (Chinese characters) is handled correctly"""
        test_data = {
            'npc_response': '哎呀！郎君這是說什麼傻話？',
            'turn': 1,
            'knowledge_window': {
                'title': '唐代的鮮與存',
                'body': '唐代沒有冰箱與微波爐...'
            }
        }
        
        file_storage.save('unicode_test', test_data)
        loaded_data = file_storage.load('unicode_test')
        
        assert loaded_data == test_data
        assert loaded_data['npc_response'] == '哎呀！郎君這是說什麼傻話？'
    
    def test_create_base_directory_if_not_exists(self, temp_dir):
        """Test that FileStorage creates base directory if it doesn't exist"""
        new_dir = os.path.join(temp_dir, 'new_storage_dir')
        assert not os.path.exists(new_dir)
        
        storage = FileStorage(base_path=new_dir)
        assert os.path.exists(new_dir)
        
        # Verify it's usable
        storage.save('test', {'data': 'value'})
        assert storage.load('test') == {'data': 'value'}


class TestMemoryStorage:
    """Test suite for MemoryStorage backend"""
    
    @pytest.fixture
    def memory_storage(self):
        """Create a MemoryStorage instance"""
        return MemoryStorage()
    
    def test_save_and_load_roundtrip(self, memory_storage):
        """Test that saving and loading data preserves all information"""
        test_data = {
            'current_turn': 2,
            'is_complete': False,
            'conversation_history': []
        }
        
        memory_storage.save('test_key', test_data)
        loaded_data = memory_storage.load('test_key')
        
        assert loaded_data == test_data
    
    def test_load_nonexistent_key_returns_none(self, memory_storage):
        """Test that loading a non-existent key returns None"""
        result = memory_storage.load('nonexistent_key')
        assert result is None
    
    def test_delete_existing_key(self, memory_storage):
        """Test deleting an existing key"""
        memory_storage.save('test_key', {'data': 'value'})
        
        # Verify it exists
        assert memory_storage.load('test_key') is not None
        
        # Delete it
        memory_storage.delete('test_key')
        
        # Verify it's gone
        assert memory_storage.load('test_key') is None
    
    def test_delete_nonexistent_key_raises_error(self, memory_storage):
        """Test that deleting a non-existent key raises StorageError"""
        with pytest.raises(StorageError) as exc_info:
            memory_storage.delete('nonexistent_key')
        
        assert 'not found' in str(exc_info.value)
    
    def test_save_overwrites_existing_data(self, memory_storage):
        """Test that saving with the same key overwrites previous data"""
        memory_storage.save('test_key', {'version': 1})
        memory_storage.save('test_key', {'version': 2})
        
        loaded_data = memory_storage.load('test_key')
        assert loaded_data == {'version': 2}
    
    def test_data_isolation(self, memory_storage):
        """Test that modifications to returned data don't affect stored data"""
        original_data = {'list': [1, 2, 3], 'nested': {'key': 'value'}}
        memory_storage.save('test_key', original_data)
        
        # Modify the returned data
        loaded_data = memory_storage.load('test_key')
        loaded_data['list'].append(4)
        loaded_data['nested']['key'] = 'modified'
        
        # Verify stored data is unchanged
        reloaded_data = memory_storage.load('test_key')
        assert reloaded_data == {'list': [1, 2, 3], 'nested': {'key': 'value'}}
    
    def test_clear_removes_all_data(self, memory_storage):
        """Test that clear() removes all stored data"""
        memory_storage.save('key1', {'data': 1})
        memory_storage.save('key2', {'data': 2})
        memory_storage.save('key3', {'data': 3})
        
        memory_storage.clear()
        
        assert memory_storage.load('key1') is None
        assert memory_storage.load('key2') is None
        assert memory_storage.load('key3') is None
        assert len(memory_storage.keys()) == 0
    
    def test_keys_returns_all_keys(self, memory_storage):
        """Test that keys() returns all stored keys"""
        memory_storage.save('key1', {'data': 1})
        memory_storage.save('key2', {'data': 2})
        memory_storage.save('key3', {'data': 3})
        
        keys = memory_storage.keys()
        assert set(keys) == {'key1', 'key2', 'key3'}
    
    def test_save_non_dict_raises_error(self, memory_storage):
        """Test that saving non-dictionary data raises StorageError"""
        with pytest.raises(StorageError) as exc_info:
            memory_storage.save('test_key', 'not a dict')
        
        assert 'must be a dictionary' in str(exc_info.value)


class TestStorageBackendInterface:
    """Test that both implementations conform to the StorageBackend interface"""
    
    def test_file_storage_implements_interface(self):
        """Test that FileStorage implements the StorageBackend interface"""
        temp_dir = tempfile.mkdtemp()
        try:
            storage = FileStorage(base_path=temp_dir)
            assert isinstance(storage, StorageBackend)
            assert hasattr(storage, 'save')
            assert hasattr(storage, 'load')
            assert hasattr(storage, 'delete')
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_memory_storage_implements_interface(self):
        """Test that MemoryStorage implements the StorageBackend interface"""
        storage = MemoryStorage()
        assert isinstance(storage, StorageBackend)
        assert hasattr(storage, 'save')
        assert hasattr(storage, 'load')
        assert hasattr(storage, 'delete')
    
    def test_file_storage_basic_operations(self):
        """Test basic save/load/delete operations on FileStorage"""
        temp_dir = tempfile.mkdtemp()
        try:
            storage = FileStorage(base_path=temp_dir)
            test_data = {'test': 'data', 'number': 42}
            
            # Save
            storage.save('test_key', test_data)
            
            # Load
            loaded = storage.load('test_key')
            assert loaded == test_data
            
            # Delete
            storage.delete('test_key')
            assert storage.load('test_key') is None
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_memory_storage_basic_operations(self):
        """Test basic save/load/delete operations on MemoryStorage"""
        storage = MemoryStorage()
        test_data = {'test': 'data', 'number': 42}
        
        # Save
        storage.save('test_key', test_data)
        
        # Load
        loaded = storage.load('test_key')
        assert loaded == test_data
        
        # Delete
        storage.delete('test_key')
        assert storage.load('test_key') is None
