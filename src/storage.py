"""Storage backend abstraction layer for Tang Dynasty Dialogue System"""

from abc import ABC, abstractmethod
from copy import deepcopy
from typing import Optional


class StorageBackend(ABC):
    """
    Abstract base class for storage backends.
    
    This interface defines the contract for persisting and retrieving
    conversation state data. Implementations can use different storage
    mechanisms (file system, memory, database, etc.).
    """
    
    @abstractmethod
    def save(self, key: str, data: dict) -> None:
        """
        Save data to storage.
        
        Args:
            key: Unique identifier for the data (e.g., session ID, state key)
            data: Dictionary containing the data to persist
            
        Raises:
            StorageError: If save operation fails
        """
        pass
    
    @abstractmethod
    def load(self, key: str) -> Optional[dict]:
        """
        Load data from storage.
        
        Args:
            key: Unique identifier for the data to retrieve
            
        Returns:
            Dictionary containing the loaded data, or None if key not found
            
        Raises:
            StorageError: If load operation fails (excluding key not found)
        """
        pass
    
    @abstractmethod
    def delete(self, key: str) -> None:
        """
        Delete data from storage.
        
        Args:
            key: Unique identifier for the data to delete
            
        Raises:
            StorageError: If delete operation fails
        """
        pass


class StorageError(Exception):
    """Base exception for storage-related errors"""
    pass


class FileStorage(StorageBackend):
    """
    File-based storage backend using JSON format.
    
    This implementation stores conversation state in JSON files on the file system.
    It uses atomic writes to prevent data corruption and handles common file system
    errors gracefully.
    """
    
    def __init__(self, base_path: str = "."):
        """
        Initialize FileStorage with a base directory path.
        
        Args:
            base_path: Directory path where state files will be stored (default: current directory)
        """
        import os
        self.base_path = base_path
        
        # Create base directory if it doesn't exist
        if not os.path.exists(base_path):
            try:
                os.makedirs(base_path, exist_ok=True)
            except OSError as e:
                raise StorageError(f"Failed to create storage directory: {e}")
    
    def save(self, key: str, data: dict) -> None:
        """
        Save data to a JSON file with atomic write operation.
        
        Uses a temporary file and atomic rename to prevent data corruption
        if the write operation is interrupted.
        
        Args:
            key: Unique identifier for the data (used as filename)
            data: Dictionary containing the data to persist
            
        Raises:
            StorageError: If save operation fails due to permission or I/O errors
        """
        import json
        import os
        import tempfile
        
        # Sanitize key to create a safe filename
        safe_filename = self._sanitize_key(key)
        file_path = os.path.join(self.base_path, f"{safe_filename}.json")
        
        try:
            # Write to a temporary file first
            temp_fd, temp_path = tempfile.mkstemp(
                dir=self.base_path,
                prefix=f".{safe_filename}_",
                suffix=".tmp"
            )
            
            try:
                # Write JSON data to temporary file
                with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                # Atomic rename: replace old file with new file
                # On Windows, we need to remove the target file first if it exists
                if os.path.exists(file_path):
                    os.replace(temp_path, file_path)
                else:
                    os.rename(temp_path, file_path)
                    
            except Exception as e:
                # Clean up temporary file if something goes wrong
                try:
                    os.unlink(temp_path)
                except OSError:
                    pass
                raise e
                
        except PermissionError as e:
            raise StorageError(f"Permission denied when saving to {file_path}: {e}")
        except OSError as e:
            raise StorageError(f"I/O error when saving to {file_path}: {e}")
        except Exception as e:
            raise StorageError(f"Unexpected error when saving to {file_path}: {e}")
    
    def load(self, key: str) -> Optional[dict]:
        """
        Load data from a JSON file.
        
        Args:
            key: Unique identifier for the data to retrieve
            
        Returns:
            Dictionary containing the loaded data, or None if file not found
            
        Raises:
            StorageError: If file is corrupted (invalid JSON) or permission denied
        """
        import json
        import os
        
        safe_filename = self._sanitize_key(key)
        file_path = os.path.join(self.base_path, f"{safe_filename}.json")
        
        # Return None if file doesn't exist (not an error condition)
        if not os.path.exists(file_path):
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data
                
        except json.JSONDecodeError as e:
            raise StorageError(f"Corrupted JSON in {file_path}: {e}")
        except PermissionError as e:
            raise StorageError(f"Permission denied when reading {file_path}: {e}")
        except OSError as e:
            raise StorageError(f"I/O error when reading {file_path}: {e}")
        except Exception as e:
            raise StorageError(f"Unexpected error when reading {file_path}: {e}")
    
    def delete(self, key: str) -> None:
        """
        Delete a JSON file from storage.
        
        Args:
            key: Unique identifier for the data to delete
            
        Raises:
            StorageError: If delete operation fails (excluding file not found)
        """
        import os
        
        safe_filename = self._sanitize_key(key)
        file_path = os.path.join(self.base_path, f"{safe_filename}.json")
        
        # Silently succeed if file doesn't exist (idempotent delete)
        if not os.path.exists(file_path):
            return
        
        try:
            os.unlink(file_path)
        except PermissionError as e:
            raise StorageError(f"Permission denied when deleting {file_path}: {e}")
        except OSError as e:
            raise StorageError(f"I/O error when deleting {file_path}: {e}")
        except Exception as e:
            raise StorageError(f"Unexpected error when deleting {file_path}: {e}")
    
    def _sanitize_key(self, key: str) -> str:
        """
        Sanitize a key to create a safe filename.
        
        Removes or replaces characters that are invalid in filenames.
        
        Args:
            key: Original key string
            
        Returns:
            Sanitized key safe for use as a filename
        """
        import re
        
        # Replace invalid filename characters with underscores
        # Invalid characters: < > : " / \ | ? *
        safe_key = re.sub(r'[<>:"/\\|?*]', '_', key)
        
        # Remove leading/trailing whitespace and dots
        safe_key = safe_key.strip('. ')
        
        # Ensure the key is not empty
        if not safe_key:
            safe_key = "default"
        
        return safe_key


class MemoryStorage(StorageBackend):
    """
    In-memory storage backend using a dictionary.
    
    This implementation stores data in a Python dictionary, making it suitable
    for testing and development. Data is not persisted across process restarts.
    
    Thread-safety: This implementation is NOT thread-safe. For concurrent access,
    use appropriate locking mechanisms or a different backend.
    """
    
    def __init__(self):
        """Initialize empty in-memory storage."""
        self._storage: dict[str, dict] = {}
    
    def save(self, key: str, data: dict) -> None:
        """
        Save data to in-memory storage.
        
        Args:
            key: Unique identifier for the data
            data: Dictionary containing the data to persist
            
        Raises:
            StorageError: If data is not a dictionary
        """
        if not isinstance(data, dict):
            raise StorageError(f"Data must be a dictionary, got {type(data).__name__}")
        
        # Store a deep copy to prevent external modifications
        self._storage[key] = deepcopy(data)
    
    def load(self, key: str) -> Optional[dict]:
        """
        Load data from in-memory storage.
        
        Args:
            key: Unique identifier for the data to retrieve
            
        Returns:
            Dictionary containing the loaded data, or None if key not found
        """
        if key not in self._storage:
            return None
        
        # Return a deep copy to prevent external modifications
        return deepcopy(self._storage[key])
    
    def delete(self, key: str) -> None:
        """
        Delete data from in-memory storage.
        
        Args:
            key: Unique identifier for the data to delete
            
        Raises:
            StorageError: If key does not exist
        """
        if key not in self._storage:
            raise StorageError(f"Key '{key}' not found in storage")
        
        del self._storage[key]
    
    def clear(self) -> None:
        """
        Clear all data from in-memory storage.
        
        This is a convenience method for testing purposes.
        """
        self._storage.clear()
    
    def keys(self) -> list[str]:
        """
        Get all keys in storage.
        
        Returns:
            List of all keys currently in storage
            
        This is a convenience method for testing purposes.
        """
        return list(self._storage.keys())
