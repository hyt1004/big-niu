import pytest
from unittest.mock import Mock, patch, MagicMock
import json


class TestTextAnalysisUnit:
    
    @pytest.fixture
    def sample_story_text(self):
        return """
        这是一个平凡的早晨,张三走在上班的路上。阳光洒在高楼之间,
        他心想:"今天会是美好的一天。"突然,他遇到了老朋友李四。
        李四兴奋地说:"张三!好久不见!"
        """
    
    @pytest.fixture
    def expected_structured_output(self):
        return {
            "metadata": {
                "total_scenes": 10,
                "story_title": "测试故事",
                "total_characters": 2
            },
            "characters": [
                {
                    "id": "char_001",
                    "name": "张三",
                    "description": "年轻男子,黑色短发,穿着现代休闲装",
                    "personality": "勇敢、善良"
                },
                {
                    "id": "char_002",
                    "name": "李四",
                    "description": "中年男子,友善的笑容",
                    "personality": "热情、健谈"
                }
            ],
            "scenes": [
                {
                    "scene_id": "scene_001",
                    "order": 1,
                    "description": "清晨的城市街道,阳光洒在高楼之间",
                    "composition": "远景,俯视角度",
                    "characters": ["char_001"],
                    "narration": "这是一个平凡的早晨,张三走在上班的路上。",
                    "dialogues": [
                        {
                            "character": "char_001",
                            "text": "今天会是美好的一天。",
                            "emotion": "愉悦"
                        }
                    ]
                }
            ]
        }
    
    def test_extract_characters_from_text(self, sample_story_text):
        with patch('services.text_analysis.nlp_model.extract_characters') as mock_extract:
            mock_extract.return_value = [
                {"name": "张三", "description": "年轻男子"},
                {"name": "李四", "description": "中年男子"}
            ]
            
            characters = extract_characters(sample_story_text)
            
            assert len(characters) >= 2
            assert any(char["name"] == "张三" for char in characters)
            assert any(char["name"] == "李四" for char in characters)
            mock_extract.assert_called_once()
    
    def test_extract_dialogues_from_text(self, sample_story_text):
        with patch('services.text_analysis.nlp_model.extract_dialogues') as mock_extract:
            mock_extract.return_value = [
                {"character": "张三", "text": "今天会是美好的一天。"},
                {"character": "李四", "text": "张三!好久不见!"}
            ]
            
            dialogues = extract_dialogues(sample_story_text)
            
            assert len(dialogues) >= 2
            assert dialogues[0]["character"] == "张三"
            assert dialogues[1]["character"] == "李四"
    
    def test_split_into_scenes_default_count(self, sample_story_text):
        with patch('services.text_analysis.scene_splitter.split') as mock_split:
            mock_split.return_value = [f"scene_{i:03d}" for i in range(1, 11)]
            
            scenes = split_into_scenes(sample_story_text, scenes_count=10)
            
            assert len(scenes) == 10
            mock_split.assert_called_once_with(sample_story_text, 10)
    
    def test_split_into_scenes_custom_count(self, sample_story_text):
        custom_count = 5
        
        with patch('services.text_analysis.scene_splitter.split') as mock_split:
            mock_split.return_value = [f"scene_{i:03d}" for i in range(1, custom_count + 1)]
            
            scenes = split_into_scenes(sample_story_text, scenes_count=custom_count)
            
            assert len(scenes) == custom_count
            mock_split.assert_called_once_with(sample_story_text, custom_count)
    
    def test_build_scene_description(self):
        scene_data = {
            "text": "清晨的城市街道,阳光洒在高楼之间",
            "characters": ["张三"],
            "dialogues": []
        }
        
        with patch('services.text_analysis.scene_builder.build_description') as mock_build:
            mock_build.return_value = "清晨的城市街道,阳光洒在高楼之间,一位年轻男子行走"
            
            description = build_scene_description(scene_data)
            
            assert "清晨" in description
            assert "城市街道" in description
            mock_build.assert_called_once()
    
    def test_assign_character_ids(self):
        characters = [
            {"name": "张三", "description": "年轻男子"},
            {"name": "李四", "description": "中年男子"}
        ]
        
        result = assign_character_ids(characters)
        
        assert len(result) == 2
        assert result[0]["id"] == "char_001"
        assert result[1]["id"] == "char_002"
        assert result[0]["name"] == "张三"
    
    def test_validate_structured_output_valid(self, expected_structured_output):
        result = validate_structured_output(expected_structured_output)
        
        assert result is True
    
    def test_validate_structured_output_missing_metadata(self):
        invalid_output = {
            "characters": [],
            "scenes": []
        }
        
        with pytest.raises(ValueError, match="Missing required field: metadata"):
            validate_structured_output(invalid_output)
    
    def test_validate_structured_output_missing_scenes(self):
        invalid_output = {
            "metadata": {"total_scenes": 10},
            "characters": []
        }
        
        with pytest.raises(ValueError, match="Missing required field: scenes"):
            validate_structured_output(invalid_output)
    
    def test_generate_scene_composition(self):
        scene_text = "张三站在高楼前,仰望天空"
        
        with patch('services.text_analysis.composition_analyzer.analyze') as mock_analyze:
            mock_analyze.return_value = "中景,仰视角度"
            
            composition = generate_scene_composition(scene_text)
            
            assert "角度" in composition or "景" in composition
            mock_analyze.assert_called_once_with(scene_text)
    
    def test_extract_emotion_from_dialogue(self):
        dialogue = "今天会是美好的一天!"
        
        with patch('services.text_analysis.emotion_analyzer.analyze') as mock_analyze:
            mock_analyze.return_value = "愉悦"
            
            emotion = extract_emotion(dialogue)
            
            assert emotion in ["愉悦", "兴奋", "平静", "悲伤", "愤怒"]
            mock_analyze.assert_called_once_with(dialogue)
    
    @patch('services.text_analysis.gpt4_client.complete')
    def test_llm_integration_for_text_analysis(self, mock_gpt4):
        mock_gpt4.return_value = json.dumps({
            "characters": [{"name": "张三"}],
            "scenes": [{"scene_id": "scene_001"}]
        })
        
        result = analyze_with_llm("测试文本")
        
        assert "characters" in result
        assert "scenes" in result
        mock_gpt4.assert_called_once()
    
    def test_handle_empty_input_text(self):
        with pytest.raises(ValueError, match="Input text cannot be empty"):
            analyze_text("")
    
    def test_handle_very_short_text(self):
        short_text = "短文本"
        
        with pytest.warns(UserWarning, match="Text is very short"):
            result = analyze_text(short_text, min_length=10)
    
    def test_character_deduplication(self):
        characters = [
            {"name": "张三", "description": "年轻男子"},
            {"name": "张三", "description": "年轻人"},
            {"name": "李四", "description": "中年男子"}
        ]
        
        result = deduplicate_characters(characters)
        
        assert len(result) == 2
        character_names = [c["name"] for c in result]
        assert character_names.count("张三") == 1
        assert character_names.count("李四") == 1


def extract_characters(text):
    pass

def extract_dialogues(text):
    pass

def split_into_scenes(text, scenes_count):
    pass

def build_scene_description(scene_data):
    pass

def assign_character_ids(characters):
    pass

def validate_structured_output(output):
    pass

def generate_scene_composition(scene_text):
    pass

def extract_emotion(dialogue):
    pass

def analyze_with_llm(text):
    pass

def analyze_text(text, min_length=0):
    pass

def deduplicate_characters(characters):
    pass
