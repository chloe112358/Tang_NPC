"""
Tests for prompts.json configuration file structure and content.

This test validates that the prompts.json file contains all required elements
according to the design document and requirements.
"""

import json
import pytest
from pathlib import Path


@pytest.fixture
def prompts_config():
    """Load prompts.json configuration"""
    config_path = Path(__file__).parent.parent / "config" / "prompts.json"
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


class TestPromptsConfigStructure:
    """Test the structure of prompts.json configuration"""
    
    def test_persona_definition_exists(self, prompts_config):
        """Validates: Requirement 2.1 - Persona definition is present"""
        assert 'persona' in prompts_config
        persona = prompts_config['persona']
        
        # Check required persona fields
        assert 'name' in persona
        assert persona['name'] == '安掌櫃'
        
        assert 'identity' in persona
        assert '粟特人' in persona['identity']
        
        assert 'personality' in persona
        assert isinstance(persona['personality'], list)
        assert len(persona['personality']) > 0
        
        assert 'language_style' in persona
        assert '唐朝半白話文' in persona['language_style']
        
        assert 'knowledge_constraints' in persona
    
    def test_prohibited_terms_exist(self, prompts_config):
        """Validates: Requirement 2.3 - Prohibited terms list is present"""
        assert 'prohibited_terms' in prompts_config
        prohibited = prompts_config['prohibited_terms']
        
        assert isinstance(prohibited, list)
        assert len(prohibited) > 0
        
        # Check for key prohibited terms
        required_terms = ['微波爐', '冰箱', '拉鍊', '塑膠', '手機']
        for term in required_terms:
            assert term in prohibited, f"Required prohibited term '{term}' not found"
    
    def test_transition_phrases_exist(self, prompts_config):
        """Validates: Requirement 8.4 - Transition phrase examples are present"""
        assert 'transition_phrases' in prompts_config
        phrases = prompts_config['transition_phrases']
        
        assert isinstance(phrases, list)
        assert len(phrases) >= 5, "Should have multiple transition phrase examples"
    
    def test_all_three_turns_defined(self, prompts_config):
        """Validates: Requirements 3.1, 3.2, 3.3 - All three turns are defined"""
        assert 'turns' in prompts_config
        turns = prompts_config['turns']
        
        # Check all three turns exist
        assert '1' in turns
        assert '2' in turns
        assert '3' in turns
    
    def test_turn_1_structure(self, prompts_config):
        """Validates: Requirements 9.1, 9.2 - Turn 1 content is complete"""
        turn1 = prompts_config['turns']['1']
        
        # Check topic
        assert 'topic' in turn1
        assert '食物' in turn1['topic']
        
        # Check convergence targets
        assert 'convergence_target' in turn1
        target = turn1['convergence_target']
        assert 'point_1' in target
        assert 'point_2' in target
        assert '胡餅' in target['point_1']
        assert '臘肉' in target['point_2']
        
        # Check system prompt
        assert 'system_prompt' in turn1
        assert len(turn1['system_prompt']) > 100
        assert '安掌櫃' in turn1['system_prompt']
        assert '收束目標' in turn1['system_prompt']
        
        # Check preset options
        assert 'preset_options' in turn1
        assert 'A' in turn1['preset_options']
        assert 'B' in turn1['preset_options']
        
        # Check fallback response
        assert 'fallback_response' in turn1
        assert len(turn1['fallback_response']) > 50
    
    def test_turn_2_structure(self, prompts_config):
        """Validates: Requirements 9.3, 9.4 - Turn 2 content is complete"""
        turn2 = prompts_config['turns']['2']
        
        # Check topic
        assert 'topic' in turn2
        assert '服飾' in turn2['topic']
        
        # Check convergence targets
        assert 'convergence_target' in turn2
        target = turn2['convergence_target']
        assert 'point_1' in target
        assert 'point_2' in target
        assert '絲綢' in target['point_1']
        assert '蹀躞帶' in target['point_2']
        
        # Check system prompt
        assert 'system_prompt' in turn2
        assert len(turn2['system_prompt']) > 100
        assert '安掌櫃' in turn2['system_prompt']
        assert '收束目標' in turn2['system_prompt']
        
        # Check preset options
        assert 'preset_options' in turn2
        assert 'A' in turn2['preset_options']
        assert 'B' in turn2['preset_options']
        
        # Check fallback response
        assert 'fallback_response' in turn2
        assert len(turn2['fallback_response']) > 50
    
    def test_turn_3_structure(self, prompts_config):
        """Validates: Requirements 9.5, 9.6 - Turn 3 content is complete"""
        turn3 = prompts_config['turns']['3']
        
        # Check topic
        assert 'topic' in turn3
        assert '顏色' in turn3['topic'] or '階級' in turn3['topic']
        
        # Check convergence targets
        assert 'convergence_target' in turn3
        target = turn3['convergence_target']
        assert 'point_1' in target
        assert 'point_2' in target
        assert '品色服' in target['point_1']
        assert '禁色' in target['point_2'] or '紫' in target['point_2']
        
        # Check system prompt
        assert 'system_prompt' in turn3
        assert len(turn3['system_prompt']) > 100
        assert '安掌櫃' in turn3['system_prompt']
        assert '收束目標' in turn3['system_prompt']
        
        # Check preset options
        assert 'preset_options' in turn3
        assert 'A' in turn3['preset_options']
        assert 'B' in turn3['preset_options']
        
        # Check fallback response
        assert 'fallback_response' in turn3
        assert len(turn3['fallback_response']) > 50
    
    def test_response_guidelines_exist(self, prompts_config):
        """Validates: Requirement 8.3 - Response guidelines are defined"""
        assert 'response_guidelines' in prompts_config
        guidelines = prompts_config['response_guidelines']
        
        assert 'length' in guidelines
        assert 'tone' in guidelines
        assert 'structure' in guidelines
        assert 'modern_term_handling' in guidelines


class TestPromptsConfigContent:
    """Test the content quality of prompts.json"""
    
    def test_system_prompts_include_persona(self, prompts_config):
        """Validates: Requirement 2.2 - System prompts define Tang dynasty persona"""
        for turn_num in ['1', '2', '3']:
            system_prompt = prompts_config['turns'][turn_num]['system_prompt']
            
            # Check persona elements are present
            assert '安掌櫃' in system_prompt
            assert '粟特人' in system_prompt
            assert '唐' in system_prompt
    
    def test_system_prompts_include_convergence_strategy(self, prompts_config):
        """Validates: Requirement 3.4, 3.5 - System prompts include convergence strategy"""
        for turn_num in ['1', '2', '3']:
            system_prompt = prompts_config['turns'][turn_num]['system_prompt']
            
            # Check convergence strategy elements
            assert '收束' in system_prompt or '引導' in system_prompt
            assert '轉' in system_prompt  # 轉場 or 過渡
    
    def test_system_prompts_include_prohibited_terms(self, prompts_config):
        """Validates: Requirement 8.5 - System prompts specify prohibited terms"""
        for turn_num in ['1', '2', '3']:
            system_prompt = prompts_config['turns'][turn_num]['system_prompt']
            
            # Check prohibited terms section exists
            assert '禁用' in system_prompt or '禁' in system_prompt
            assert '微波爐' in system_prompt
            assert '冰箱' in system_prompt
    
    def test_system_prompts_include_transition_examples(self, prompts_config):
        """Validates: Requirement 8.4 - System prompts include transition phrase examples"""
        for turn_num in ['1', '2', '3']:
            system_prompt = prompts_config['turns'][turn_num]['system_prompt']
            
            # Check transition phrase examples section exists
            assert '轉場' in system_prompt or '短語' in system_prompt
    
    def test_convergence_targets_match_requirements(self, prompts_config):
        """Validates: Requirements 9.1, 9.3, 9.5 - Convergence targets match spec"""
        # Turn 1: Food cooking and preservation
        turn1_target = prompts_config['turns']['1']['convergence_target']
        assert '胡餅' in turn1_target['point_1']
        assert '臘肉' in turn1_target['point_2'] or '香料' in turn1_target['point_2']
        
        # Turn 2: Clothing materials and fastening
        turn2_target = prompts_config['turns']['2']['convergence_target']
        assert '絲綢' in turn2_target['point_1'] or '蜀錦' in turn2_target['point_1']
        assert '繫帶' in turn2_target['point_2'] or '蹀躞帶' in turn2_target['point_2']
        
        # Turn 3: Clothing colors and social hierarchy
        turn3_target = prompts_config['turns']['3']['convergence_target']
        assert '品色服' in turn3_target['point_1'] or '紫' in turn3_target['point_1']
        assert '禁色' in turn3_target['point_2'] or '紫' in turn3_target['point_2']
    
    def test_fallback_responses_contain_convergence_content(self, prompts_config):
        """Validates: Requirement 3.6 - Fallback responses contain core knowledge"""
        # Turn 1 fallback should mention 胡餅 and 臘肉
        turn1_fallback = prompts_config['turns']['1']['fallback_response']
        assert '胡餅' in turn1_fallback
        assert '臘肉' in turn1_fallback or '香料' in turn1_fallback
        
        # Turn 2 fallback should mention 絲綢 and 蹀躞帶
        turn2_fallback = prompts_config['turns']['2']['fallback_response']
        assert '絲綢' in turn2_fallback or '蜀錦' in turn2_fallback
        assert '繫帶' in turn2_fallback or '蹀躞帶' in turn2_fallback
        
        # Turn 3 fallback should mention 品色服 and forbidden colors
        turn3_fallback = prompts_config['turns']['3']['fallback_response']
        assert '紫' in turn3_fallback or '品色服' in turn3_fallback
        assert '禁' in turn3_fallback or '金吾衛' in turn3_fallback
    
    def test_no_modern_terms_in_fallback_responses(self, prompts_config):
        """Validates: Requirement 2.3 - Fallback responses don't contain prohibited terms"""
        prohibited = prompts_config['prohibited_terms']
        
        for turn_num in ['1', '2', '3']:
            fallback = prompts_config['turns'][turn_num]['fallback_response']
            
            for term in prohibited:
                assert term not in fallback, f"Fallback response contains prohibited term: {term}"
    
    def test_response_length_guidelines(self, prompts_config):
        """Validates: Requirement 2.5 - Response length guidelines are specified"""
        guidelines = prompts_config['response_guidelines']
        
        assert 'length' in guidelines
        assert '150' in guidelines['length'] or '250' in guidelines['length']
