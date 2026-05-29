"""Tests for KnowledgeWindowProvider"""

import pytest
import json
import tempfile
from pathlib import Path

from src.knowledge_window_provider import KnowledgeWindowProvider
from src.models import KnowledgeWindow


class TestKnowledgeWindowProvider:
    """Test KnowledgeWindowProvider functionality"""
    
    @pytest.fixture
    def valid_config_file(self):
        """Create a temporary valid configuration file"""
        config_data = {
            "turn_1": {
                "title": "唐代的鮮與存",
                "body": "唐代沒有冰箱與微波爐，但長安人解決「吃」的方式既實際又聰明。",
                "image_description": "左半邊是胡餅爐特寫；右半邊是市集攤位上掛滿臘肉"
            },
            "turn_2": {
                "title": "沒有拉鍊的絲綢帝國",
                "body": "拉鍊發明於 1891 年，合成纖維發明於 1940 年代。",
                "image_description": "對比圖——左邊是現代拉鍊；右邊是交領右衽穿法圖解"
            },
            "turn_3": {
                "title": "唐代服色制度（品色服）",
                "body": "現代人可以自由選擇衣服顏色，但在唐代，顏色是政治與階級的公開宣示。",
                "image_description": "品色服階級表格，展示紫、緋、綠、青、白各色官服的樣式"
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', 
                                         suffix='.json', delete=False) as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)
            temp_path = f.name
        
        yield temp_path
        
        # Cleanup
        Path(temp_path).unlink(missing_ok=True)
    
    @pytest.fixture
    def missing_turn_config_file(self):
        """Create a config file missing turn_2"""
        config_data = {
            "turn_1": {
                "title": "Title 1",
                "body": "Body 1",
                "image_description": "Image 1"
            },
            "turn_3": {
                "title": "Title 3",
                "body": "Body 3",
                "image_description": "Image 3"
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', 
                                         suffix='.json', delete=False) as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)
            temp_path = f.name
        
        yield temp_path
        
        Path(temp_path).unlink(missing_ok=True)
    
    @pytest.fixture
    def missing_field_config_file(self):
        """Create a config file with missing 'body' field in turn_1"""
        config_data = {
            "turn_1": {
                "title": "Title 1",
                "image_description": "Image 1"
                # Missing 'body' field
            },
            "turn_2": {
                "title": "Title 2",
                "body": "Body 2",
                "image_description": "Image 2"
            },
            "turn_3": {
                "title": "Title 3",
                "body": "Body 3",
                "image_description": "Image 3"
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', 
                                         suffix='.json', delete=False) as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)
            temp_path = f.name
        
        yield temp_path
        
        Path(temp_path).unlink(missing_ok=True)
    
    @pytest.fixture
    def invalid_json_file(self):
        """Create a file with invalid JSON"""
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', 
                                         suffix='.json', delete=False) as f:
            f.write("{ invalid json content }")
            temp_path = f.name
        
        yield temp_path
        
        Path(temp_path).unlink(missing_ok=True)
    
    def test_initialization_with_valid_config(self, valid_config_file):
        """Test successful initialization with valid configuration file"""
        provider = KnowledgeWindowProvider(valid_config_file)
        assert provider is not None
        assert provider.content_config_path == Path(valid_config_file)
    
    def test_initialization_with_nonexistent_file(self):
        """Test initialization raises FileNotFoundError for nonexistent file"""
        with pytest.raises(FileNotFoundError) as exc_info:
            KnowledgeWindowProvider("/nonexistent/path/config.json")
        
        assert "not found" in str(exc_info.value).lower()
    
    def test_initialization_with_invalid_json(self, invalid_json_file):
        """Test initialization raises ValueError for invalid JSON"""
        with pytest.raises(ValueError) as exc_info:
            KnowledgeWindowProvider(invalid_json_file)
        
        assert "invalid json" in str(exc_info.value).lower()
    
    def test_initialization_with_missing_turn(self, missing_turn_config_file):
        """Test initialization raises ValueError when a required turn is missing"""
        with pytest.raises(ValueError) as exc_info:
            KnowledgeWindowProvider(missing_turn_config_file)
        
        assert "turn_2" in str(exc_info.value).lower()
        assert "missing" in str(exc_info.value).lower()
    
    def test_initialization_with_missing_field(self, missing_field_config_file):
        """Test initialization raises ValueError when a required field is missing"""
        with pytest.raises(ValueError) as exc_info:
            KnowledgeWindowProvider(missing_field_config_file)
        
        assert "body" in str(exc_info.value).lower()
        assert "missing" in str(exc_info.value).lower()
    
    def test_get_knowledge_window_turn_1(self, valid_config_file):
        """Test get_knowledge_window returns correct content for turn 1"""
        provider = KnowledgeWindowProvider(valid_config_file)
        kw = provider.get_knowledge_window(1)
        
        assert isinstance(kw, KnowledgeWindow)
        assert kw.title == "唐代的鮮與存"
        assert "唐代沒有冰箱與微波爐" in kw.body
        assert "胡餅爐" in kw.image_description
    
    def test_get_knowledge_window_turn_2(self, valid_config_file):
        """Test get_knowledge_window returns correct content for turn 2"""
        provider = KnowledgeWindowProvider(valid_config_file)
        kw = provider.get_knowledge_window(2)
        
        assert isinstance(kw, KnowledgeWindow)
        assert kw.title == "沒有拉鍊的絲綢帝國"
        assert "拉鍊發明於 1891 年" in kw.body
        assert "拉鍊" in kw.image_description
    
    def test_get_knowledge_window_turn_3(self, valid_config_file):
        """Test get_knowledge_window returns correct content for turn 3"""
        provider = KnowledgeWindowProvider(valid_config_file)
        kw = provider.get_knowledge_window(3)
        
        assert isinstance(kw, KnowledgeWindow)
        assert kw.title == "唐代服色制度（品色服）"
        assert "顏色是政治與階級的公開宣示" in kw.body
        assert "品色服" in kw.image_description
    
    def test_get_knowledge_window_invalid_turn_zero(self, valid_config_file):
        """Test get_knowledge_window raises ValueError for turn 0"""
        provider = KnowledgeWindowProvider(valid_config_file)
        
        with pytest.raises(ValueError) as exc_info:
            provider.get_knowledge_window(0)
        
        assert "invalid turn number" in str(exc_info.value).lower()
        assert "0" in str(exc_info.value)
    
    def test_get_knowledge_window_invalid_turn_four(self, valid_config_file):
        """Test get_knowledge_window raises ValueError for turn 4"""
        provider = KnowledgeWindowProvider(valid_config_file)
        
        with pytest.raises(ValueError) as exc_info:
            provider.get_knowledge_window(4)
        
        assert "invalid turn number" in str(exc_info.value).lower()
        assert "4" in str(exc_info.value)
    
    def test_get_knowledge_window_invalid_turn_negative(self, valid_config_file):
        """Test get_knowledge_window raises ValueError for negative turn"""
        provider = KnowledgeWindowProvider(valid_config_file)
        
        with pytest.raises(ValueError) as exc_info:
            provider.get_knowledge_window(-1)
        
        assert "invalid turn number" in str(exc_info.value).lower()
    
    def test_get_knowledge_window_all_turns_sequential(self, valid_config_file):
        """Test getting knowledge windows for all turns sequentially"""
        provider = KnowledgeWindowProvider(valid_config_file)
        
        kw1 = provider.get_knowledge_window(1)
        kw2 = provider.get_knowledge_window(2)
        kw3 = provider.get_knowledge_window(3)
        
        # Verify all are different
        assert kw1.title != kw2.title != kw3.title
        assert kw1.body != kw2.body != kw3.body
        assert kw1.image_description != kw2.image_description != kw3.image_description
    
    def test_get_knowledge_window_multiple_calls_same_turn(self, valid_config_file):
        """Test multiple calls for same turn return consistent results"""
        provider = KnowledgeWindowProvider(valid_config_file)
        
        kw1_first = provider.get_knowledge_window(1)
        kw1_second = provider.get_knowledge_window(1)
        
        assert kw1_first.title == kw1_second.title
        assert kw1_first.body == kw1_second.body
        assert kw1_first.image_description == kw1_second.image_description
    
    def test_knowledge_window_contains_required_turn_1_content(self, valid_config_file):
        """Test turn 1 knowledge window contains required educational content
        
        Validates: Requirements 9.1, 9.2
        """
        provider = KnowledgeWindowProvider(valid_config_file)
        kw = provider.get_knowledge_window(1)
        
        # Should contain information about food and preservation
        # The fixture has simplified content, so we just verify it's about food/eating
        assert "吃" in kw.body or "食" in kw.body or kw.title == "唐代的鮮與存"
    
    def test_knowledge_window_contains_required_turn_2_content(self, valid_config_file):
        """Test turn 2 knowledge window contains required educational content
        
        Validates: Requirements 9.3, 9.4
        """
        provider = KnowledgeWindowProvider(valid_config_file)
        kw = provider.get_knowledge_window(2)
        
        # Should contain information about 絲綢 and fastening methods
        assert "拉鍊" in kw.body or "拉链" in kw.body
        assert "絲綢" in kw.body or "丝绸" in kw.body or "纖維" in kw.body or "纤维" in kw.body
    
    def test_knowledge_window_contains_required_turn_3_content(self, valid_config_file):
        """Test turn 3 knowledge window contains required educational content
        
        Validates: Requirements 9.5, 9.6
        """
        provider = KnowledgeWindowProvider(valid_config_file)
        kw = provider.get_knowledge_window(3)
        
        # Should contain information about 品色服 and color hierarchy
        assert "品色服" in kw.body or "服色" in kw.body or "顏色" in kw.body or "颜色" in kw.body
    
    def test_knowledge_window_fields_are_non_empty(self, valid_config_file):
        """Test all knowledge window fields are non-empty strings"""
        provider = KnowledgeWindowProvider(valid_config_file)
        
        for turn in [1, 2, 3]:
            kw = provider.get_knowledge_window(turn)
            
            assert isinstance(kw.title, str)
            assert len(kw.title) > 0
            
            assert isinstance(kw.body, str)
            assert len(kw.body) > 0
            
            assert isinstance(kw.image_description, str)
            assert len(kw.image_description) > 0
    
    def test_with_actual_config_file(self):
        """Test with the actual project configuration file"""
        actual_config_path = "config/knowledge_windows.json"
        
        # Skip if file doesn't exist (for isolated test environments)
        if not Path(actual_config_path).exists():
            pytest.skip("Actual config file not found")
        
        provider = KnowledgeWindowProvider(actual_config_path)
        
        # Test all three turns
        for turn in [1, 2, 3]:
            kw = provider.get_knowledge_window(turn)
            assert isinstance(kw, KnowledgeWindow)
            assert len(kw.title) > 0
            assert len(kw.body) > 0
            assert len(kw.image_description) > 0
