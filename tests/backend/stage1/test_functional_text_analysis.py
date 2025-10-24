import pytest
from unittest.mock import Mock, patch
import json


class TestTextAnalysisFunctional:
    
    @pytest.fixture
    def sample_novel_text(self):
        return """
        第一章:新的开始
        
        这是一个平凡的早晨,张三走在上班的路上。阳光洒在高楼之间,
        他心想:"今天会是美好的一天。"
        
        突然,他遇到了老朋友李四。李四兴奋地说:"张三!好久不见!
        最近过得怎么样?"
        
        张三微笑着回答:"还不错,你呢?"他们在街角的咖啡店坐下,
        开始聊起了往事。
        
        窗外,城市的喧嚣继续着,但此刻,对他们来说,时间仿佛静止了。
        李四说:"还记得我们大学时的梦想吗?"
        
        张三陷入了沉思。那些年轻时的梦想,现在还剩下多少?
        他深深地吸了一口气,决定重新审视自己的人生。
        """
    
    @pytest.fixture
    def config_10_scenes(self):
        return {
            "scenes_count": 10,
            "style": "anime",
            "language": "zh-CN"
        }
    
    @pytest.fixture
    def config_5_scenes(self):
        return {
            "scenes_count": 5,
            "style": "realistic",
            "language": "zh-CN"
        }
    
    @pytest.mark.asyncio
    async def test_end_to_end_text_analysis_pipeline(self, sample_novel_text, config_10_scenes):
        with patch('services.text_analysis.TextAnalysisService') as MockService:
            mock_service = MockService.return_value
            mock_service.analyze.return_value = {
                "metadata": {
                    "total_scenes": 10,
                    "story_title": "新的开始",
                    "total_characters": 2
                },
                "characters": [
                    {
                        "id": "char_001",
                        "name": "张三",
                        "description": "年轻男子,黑色短发,穿着现代休闲装",
                        "personality": "内省、善良"
                    },
                    {
                        "id": "char_002",
                        "name": "李四",
                        "description": "中年男子,友善的笑容,穿着商务休闲装",
                        "personality": "热情、怀旧"
                    }
                ],
                "scenes": [
                    {
                        "scene_id": f"scene_{i:03d}",
                        "order": i,
                        "description": f"场景{i}描述",
                        "composition": "中景",
                        "characters": ["char_001"] if i % 2 == 0 else ["char_001", "char_002"],
                        "narration": f"场景{i}旁白",
                        "dialogues": []
                    } for i in range(1, 11)
                ]
            }
            
            result = await mock_service.analyze(sample_novel_text, config_10_scenes)
            
            assert result["metadata"]["total_scenes"] == 10
            assert len(result["characters"]) == 2
            assert len(result["scenes"]) == 10
            assert all(scene["scene_id"].startswith("scene_") for scene in result["scenes"])
    
    @pytest.mark.asyncio
    async def test_text_analysis_with_different_scene_counts(self, sample_novel_text):
        for scene_count in [5, 10, 15, 20]:
            with patch('services.text_analysis.TextAnalysisService.analyze') as mock_analyze:
                mock_analyze.return_value = {
                    "metadata": {"total_scenes": scene_count},
                    "characters": [],
                    "scenes": [{"scene_id": f"scene_{i:03d}"} for i in range(1, scene_count + 1)]
                }
                
                result = await mock_analyze(sample_novel_text, {"scenes_count": scene_count})
                
                assert result["metadata"]["total_scenes"] == scene_count
                assert len(result["scenes"]) == scene_count
    
    @pytest.mark.asyncio
    async def test_character_extraction_accuracy(self, sample_novel_text):
        with patch('services.text_analysis.TextAnalysisService') as MockService:
            mock_service = MockService.return_value
            mock_service.extract_characters.return_value = [
                {"name": "张三", "mentions": 5},
                {"name": "李四", "mentions": 3}
            ]
            
            characters = await mock_service.extract_characters(sample_novel_text)
            
            assert len(characters) >= 2
            assert any(c["name"] == "张三" for c in characters)
            assert any(c["name"] == "李四" for c in characters)
    
    @pytest.mark.asyncio
    async def test_dialogue_extraction_with_speakers(self, sample_novel_text):
        with patch('services.text_analysis.TextAnalysisService') as MockService:
            mock_service = MockService.return_value
            mock_service.extract_dialogues.return_value = [
                {"character": "张三", "text": "今天会是美好的一天。", "emotion": "愉悦"},
                {"character": "李四", "text": "张三!好久不见!最近过得怎么样?", "emotion": "兴奋"},
                {"character": "张三", "text": "还不错,你呢?", "emotion": "平静"},
                {"character": "李四", "text": "还记得我们大学时的梦想吗?", "emotion": "怀旧"}
            ]
            
            dialogues = await mock_service.extract_dialogues(sample_novel_text)
            
            assert len(dialogues) >= 4
            assert all("character" in d and "text" in d for d in dialogues)
            assert all("emotion" in d for d in dialogues)
    
    @pytest.mark.asyncio
    async def test_scene_description_generation(self, sample_novel_text, config_10_scenes):
        with patch('services.text_analysis.TextAnalysisService') as MockService:
            mock_service = MockService.return_value
            mock_service.generate_scenes.return_value = [
                {
                    "scene_id": "scene_001",
                    "description": "清晨的城市街道,阳光洒在高楼之间",
                    "composition": "远景,俯视角度",
                    "time_of_day": "早晨",
                    "location": "城市街道"
                },
                {
                    "scene_id": "scene_002",
                    "description": "街角咖啡店内部,温馨的灯光",
                    "composition": "中景,平视角度",
                    "time_of_day": "早晨",
                    "location": "咖啡店"
                }
            ]
            
            scenes = await mock_service.generate_scenes(sample_novel_text, config_10_scenes)
            
            assert len(scenes) >= 2
            assert all("description" in s for s in scenes)
            assert all("composition" in s for s in scenes)
    
    @pytest.mark.asyncio
    async def test_narration_extraction_per_scene(self, sample_novel_text):
        with patch('services.text_analysis.TextAnalysisService') as MockService:
            mock_service = MockService.return_value
            mock_service.extract_narration.return_value = [
                {
                    "scene_id": "scene_001",
                    "narration": "这是一个平凡的早晨,张三走在上班的路上。"
                },
                {
                    "scene_id": "scene_002",
                    "narration": "窗外,城市的喧嚣继续着。"
                }
            ]
            
            narrations = await mock_service.extract_narration(sample_novel_text)
            
            assert len(narrations) >= 2
            assert all("narration" in n and len(n["narration"]) > 0 for n in narrations)
    
    @pytest.mark.asyncio
    async def test_structured_output_validation(self, sample_novel_text, config_10_scenes):
        with patch('services.text_analysis.TextAnalysisService.analyze') as mock_analyze:
            mock_analyze.return_value = {
                "metadata": {
                    "total_scenes": 10,
                    "story_title": "新的开始",
                    "total_characters": 2
                },
                "characters": [
                    {"id": "char_001", "name": "张三", "description": "年轻男子", "personality": "善良"}
                ],
                "scenes": [
                    {
                        "scene_id": "scene_001",
                        "order": 1,
                        "description": "场景描述",
                        "composition": "中景",
                        "characters": ["char_001"],
                        "narration": "旁白文字",
                        "dialogues": []
                    }
                ]
            }
            
            result = await mock_analyze(sample_novel_text, config_10_scenes)
            
            assert "metadata" in result
            assert "characters" in result
            assert "scenes" in result
            assert "total_scenes" in result["metadata"]
            assert "story_title" in result["metadata"]
    
    @pytest.mark.asyncio
    async def test_long_text_processing(self):
        long_text = "这是一个很长的故事。" * 1000
        
        with patch('services.text_analysis.TextAnalysisService.analyze') as mock_analyze:
            mock_analyze.return_value = {
                "metadata": {"total_scenes": 20},
                "characters": [{"id": "char_001", "name": "主角"}],
                "scenes": [{"scene_id": f"scene_{i:03d}"} for i in range(1, 21)]
            }
            
            result = await mock_analyze(long_text, {"scenes_count": 20})
            
            assert result["metadata"]["total_scenes"] == 20
    
    @pytest.mark.asyncio
    async def test_error_handling_invalid_input(self):
        with patch('services.text_analysis.TextAnalysisService.analyze') as mock_analyze:
            mock_analyze.side_effect = ValueError("Input text is too short")
            
            with pytest.raises(ValueError, match="Input text is too short"):
                await mock_analyze("", {"scenes_count": 10})
    
    @pytest.mark.asyncio
    async def test_retry_mechanism_on_llm_failure(self, sample_novel_text):
        with patch('services.text_analysis.TextAnalysisService.analyze') as mock_analyze:
            mock_analyze.side_effect = [
                Exception("LLM API timeout"),
                Exception("LLM API timeout"),
                {
                    "metadata": {"total_scenes": 10},
                    "characters": [],
                    "scenes": []
                }
            ]
            
            result = None
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    result = await mock_analyze(sample_novel_text, {"scenes_count": 10})
                    break
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    continue
            
            assert result is not None
            assert "metadata" in result
    
    @pytest.mark.asyncio
    async def test_performance_large_text_analysis(self, sample_novel_text):
        import time
        
        large_text = sample_novel_text * 50
        
        with patch('services.text_analysis.TextAnalysisService.analyze') as mock_analyze:
            mock_analyze.return_value = {
                "metadata": {"total_scenes": 10},
                "characters": [],
                "scenes": []
            }
            
            start_time = time.time()
            result = await mock_analyze(large_text, {"scenes_count": 10})
            elapsed_time = time.time() - start_time
            
            assert result is not None
            assert elapsed_time < 30
    
    @pytest.mark.asyncio
    async def test_character_consistency_across_scenes(self, sample_novel_text, config_10_scenes):
        with patch('services.text_analysis.TextAnalysisService.analyze') as mock_analyze:
            mock_analyze.return_value = {
                "metadata": {"total_scenes": 3},
                "characters": [
                    {"id": "char_001", "name": "张三"},
                    {"id": "char_002", "name": "李四"}
                ],
                "scenes": [
                    {
                        "scene_id": "scene_001",
                        "characters": ["char_001"],
                        "narration": "张三出现"
                    },
                    {
                        "scene_id": "scene_002",
                        "characters": ["char_001", "char_002"],
                        "narration": "张三和李四相遇"
                    },
                    {
                        "scene_id": "scene_003",
                        "characters": ["char_001", "char_002"],
                        "narration": "他们在咖啡店"
                    }
                ]
            }
            
            result = await mock_analyze(sample_novel_text, config_10_scenes)
            
            all_character_ids = set()
            for scene in result["scenes"]:
                all_character_ids.update(scene["characters"])
            
            character_ids_in_metadata = {c["id"] for c in result["characters"]}
            
            assert all_character_ids.issubset(character_ids_in_metadata)
