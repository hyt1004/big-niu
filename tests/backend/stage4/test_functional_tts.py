"""
Stage4 TTS 功能测试
测试火山引擎 TTS 完整的音频生成功能
"""

import pytest
import json
import os
import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# 添加 backend 目录到 Python 路径
backend_path = project_root / "backend"
sys.path.insert(0, str(backend_path))

from app.services.stage4_tts import Stage4TTSService
from app.models.schemas import Character, Scene, Dialogue, Stage1Output


# 测试数据路径
MOCKDATA_DIR = Path(__file__).parent / "mockdata"
STAGE1_OUTPUT = MOCKDATA_DIR / "stage1_output.json"
EXPECTED_OUTPUT = MOCKDATA_DIR / "stage4_expected_output.json"


@pytest.fixture
def stage1_data():
    """加载 Stage1 输出数据"""
    with open(STAGE1_OUTPUT, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def expected_output():
    """加载预期输出数据"""
    with open(EXPECTED_OUTPUT, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def temp_output_dir():
    """创建临时输出目录"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_volcengine_response():
    """模拟火山引擎响应"""
    return {
        "code": 3000,
        "message": "success",
        "data": {
            "audio": "base64_encoded_audio_data_for_testing"
        }
    }


class TestMockDataValidation:
    """Mock 数据验证测试"""
    
    def test_stage1_output_exists(self):
        """测试 Stage1 输出文件存在"""
        assert STAGE1_OUTPUT.exists()
    
    def test_stage1_output_structure(self, stage1_data):
        """测试 Stage1 输出结构"""
        assert "metadata" in stage1_data
        assert "characters" in stage1_data
        assert "scenes" in stage1_data
        assert len(stage1_data["scenes"]) == 3
    
    def test_expected_output_structure(self, expected_output):
        """测试预期输出结构"""
        assert "scenes" in expected_output
        assert "total_video_duration" in expected_output
        assert "character_voices" in expected_output


class TestSceneAudioGeneration:
    """场景音频生成测试"""
    
    def setup_method(self):
        """设置测试环境"""
        os.environ["VOLCENGINE_APPID"] = "test_appid"
        os.environ["VOLCENGINE_ACCESS_TOKEN"] = "test_token"
        os.environ["VOLCENGINE_CLUSTER"] = "volcano_tts"
    
    @pytest.mark.asyncio
    async def test_generate_scene_001_audio(self, stage1_data, temp_output_dir, mock_volcengine_response):
        """测试生成场景1的音频"""
        # 创建 TTS 服务
        tts_service = Stage4TTSService(output_dir=temp_output_dir)
        
        # 转换数据格式
        characters = [Character(**char) for char in stage1_data["characters"]]
        scene_data = stage1_data["scenes"][0]
        scene = Scene(
            scene_id=scene_data["scene_id"],
            description=scene_data["description"],
            narration=scene_data["narration"],
            dialogues=[Dialogue(**dialogue) for dialogue in scene_data["dialogues"]]
        )
        
        # 模拟火山引擎响应
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value=mock_volcengine_response)
            mock_post.return_value.__aenter__.return_value = mock_response
            
            # 生成场景音频
            result = await tts_service.generate_scene_audio(
                scene=scene,
                characters=characters,
                scene_index=1,
                use_real_tts=True
            )
            
            # 验证输出
            assert result.scene_id == "scene_001"
            assert len(result.audio_segments) == 2  # 1旁白 + 1对话
            assert result.total_duration > 0
            
            # 验证旁白音频段
            narration_segment = result.audio_segments[0]
            assert narration_segment.type == "narration"
            assert "汪淼" in narration_segment.text
            assert narration_segment.voice == "narrator"
            
            # 验证对话音频段
            dialogue_segment = result.audio_segments[1]
            assert dialogue_segment.type == "dialogue"
            assert dialogue_segment.character == "char_001"
            assert dialogue_segment.text == "这到底是什么？"
            assert dialogue_segment.voice == "male_middle_aged"
    
    @pytest.mark.asyncio
    async def test_generate_scene_002_audio(self, stage1_data, temp_output_dir, mock_volcengine_response):
        """测试生成场景2的音频（多个对话）"""
        tts_service = Stage4TTSService(output_dir=temp_output_dir)
        
        # 转换数据格式
        characters = [Character(**char) for char in stage1_data["characters"]]
        scene_data = stage1_data["scenes"][1]
        scene = Scene(
            scene_id=scene_data["scene_id"],
            description=scene_data["description"],
            narration=scene_data["narration"],
            dialogues=[Dialogue(**dialogue) for dialogue in scene_data["dialogues"]]
        )
        
        # 模拟火山引擎响应
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value=mock_volcengine_response)
            mock_post.return_value.__aenter__.return_value = mock_response
            
            # 生成场景音频
            result = await tts_service.generate_scene_audio(
                scene=scene,
                characters=characters,
                scene_index=2,
                use_real_tts=True
            )
            
            # 验证输出
            assert result.scene_id == "scene_002"
            assert len(result.audio_segments) == 5  # 1旁白 + 4对话
            assert result.total_duration > 0
            
            # 验证所有对话都有正确的角色分配
            dialogue_segments = [seg for seg in result.audio_segments if seg.type == "dialogue"]
            assert len(dialogue_segments) == 4
            
            # 验证角色音色分配
            char_001_segments = [seg for seg in dialogue_segments if seg.character == "char_001"]
            char_002_segments = [seg for seg in dialogue_segments if seg.character == "char_002"]
            
            assert len(char_001_segments) == 2  # 汪淼有2个对话
            assert len(char_002_segments) == 2  # 小李有2个对话
            
            # 验证音色一致性
            for seg in char_001_segments:
                assert seg.voice == "male_middle_aged"
            for seg in char_002_segments:
                assert seg.voice == "male_young"
    
    @pytest.mark.asyncio
    async def test_generate_all_scenes_audio(self, stage1_data, temp_output_dir, mock_volcengine_response):
        """测试生成所有场景的音频"""
        tts_service = Stage4TTSService(output_dir=temp_output_dir)
        
        # 转换数据格式
        characters = [Character(**char) for char in stage1_data["characters"]]
        scenes = []
        for scene_data in stage1_data["scenes"]:
            scene = Scene(
                scene_id=scene_data["scene_id"],
                description=scene_data["description"],
                narration=scene_data["narration"],
                dialogues=[Dialogue(**dialogue) for dialogue in scene_data["dialogues"]]
            )
            scenes.append(scene)
        
        stage1_output = Stage1Output(
            characters=characters,
            scenes=scenes,
            total_duration=60.0
        )
        
        # 模拟火山引擎响应
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value=mock_volcengine_response)
            mock_post.return_value.__aenter__.return_value = mock_response
            
            # 生成所有场景音频
            result = await tts_service.generate_all_audio(
                stage1_output=stage1_output,
                use_real_tts=True,
                concurrent=False  # 使用串行模式便于测试
            )
            
            # 验证输出
            assert len(result.scenes) == 3
            assert result.total_video_duration > 0
            assert len(result.character_voices) == 4  # 3个角色 + 旁白
            
            # 验证每个场景都有音频
            for scene_result in result.scenes:
                assert len(scene_result.audio_segments) > 0
                assert scene_result.total_duration > 0


class TestAudioSegmentTiming:
    """音频时间轴测试"""
    
    def test_calculate_start_times(self, expected_output):
        """测试音频段开始时间计算"""
        scene = expected_output["scenes"][0]
        segments = scene["audio_segments"]
        
        # 验证时间轴连续性
        for i in range(1, len(segments)):
            prev_segment = segments[i-1]
            curr_segment = segments[i]
            expected_start = prev_segment["start_time"] + prev_segment["duration"]
            assert curr_segment["start_time"] == expected_start
    
    def test_total_duration_calculation(self, expected_output):
        """测试总时长计算"""
        scene = expected_output["scenes"][0]
        segments = scene["audio_segments"]
        
        # 计算总时长
        last_segment = segments[-1]
        calculated_duration = last_segment["start_time"] + last_segment["duration"]
        
        assert scene["total_duration"] == calculated_duration


class TestCharacterVoiceAssignment:
    """角色音色分配测试"""
    
    def test_voice_assignment_consistency(self, stage1_data, expected_output):
        """测试音色分配的一致性"""
        character_voices = expected_output["character_voices"]
        
        # 验证每个角色只分配一个音色
        assert len(character_voices) == 4  # 3个角色 + 旁白
        
        # 验证所有场景中同一角色使用相同音色
        for scene in expected_output["scenes"]:
            for segment in scene["audio_segments"]:
                if segment["type"] == "dialogue":
                    char_id = segment["character"]
                    expected_voice = character_voices[char_id]
                    assert segment["voice"] == expected_voice


class TestVolcengineTTSIntegration:
    """火山引擎 TTS 集成测试"""
    
    def setup_method(self):
        """设置测试环境"""
        os.environ["VOLCENGINE_APPID"] = "test_appid"
        os.environ["VOLCENGINE_ACCESS_TOKEN"] = "test_token"
        os.environ["VOLCENGINE_CLUSTER"] = "volcano_tts"
    
    @pytest.mark.asyncio
    async def test_volcengine_tts_request_parameters(self, temp_output_dir):
        """测试火山引擎 TTS 请求参数"""
        tts_service = Stage4TTSService(output_dir=temp_output_dir)
        
        # 测试不同情绪的参数映射
        test_cases = [
            ("Anxious and confused", {"speed": 1.1, "pitch": 1.1, "volume": 1.0}),
            ("Sad and depressed", {"speed": 0.9, "pitch": 0.9, "volume": 1.0}),
            ("Happy and excited", {"speed": 1.05, "pitch": 1.05, "volume": 1.0}),
            ("Calm and peaceful", {"speed": 0.95, "pitch": 1.0, "volume": 1.0}),
        ]
        
        for emotion, expected_params in test_cases:
            params = tts_service._map_emotion_to_params(emotion)
            assert params["speed"] == expected_params["speed"]
            assert params["pitch"] == expected_params["pitch"]
            assert params["volume"] == expected_params["volume"]
    
    @pytest.mark.asyncio
    async def test_volcengine_tts_voice_assignment(self, stage1_data, temp_output_dir):
        """测试火山引擎 TTS 音色分配"""
        tts_service = Stage4TTSService(output_dir=temp_output_dir)
        
        # 测试角色音色分配
        characters = [Character(**char) for char in stage1_data["characters"]]
        
        # 汪淼 - 中年男性
        wang_miao = next(char for char in characters if char.id == "char_001")
        voice = tts_service._assign_character_voice(wang_miao)
        assert voice == "BV700_streaming"
        
        # 小李 - 年轻男性
        xiao_li = next(char for char in characters if char.id == "char_002")
        voice = tts_service._assign_character_voice(xiao_li)
        assert voice == "BV701_streaming"
        
        # 叶文洁 - 老年女性
        ye_wenjie = next(char for char in characters if char.id == "char_003")
        voice = tts_service._assign_character_voice(ye_wenjie)
        assert voice == "BV002_streaming"
    
    @pytest.mark.asyncio
    async def test_volcengine_tts_error_handling(self, temp_output_dir):
        """测试火山引擎 TTS 错误处理"""
        tts_service = Stage4TTSService(output_dir=temp_output_dir)
        
        # 模拟网络错误
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_post.side_effect = Exception("Network error")
            
            with pytest.raises(Exception, match="Network error"):
                await tts_service._generate_audio_volcengine(
                    "测试文本", "BV001_streaming", {"speed": 1.0, "pitch": 1.0, "volume": 1.0}
                )
        
        # 模拟 API 错误响应
        error_response = {
            "code": 4001,
            "message": "Invalid request",
            "data": None
        }
        
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value=error_response)
            mock_post.return_value.__aenter__.return_value = mock_response
            
            with pytest.raises(Exception, match="Invalid request"):
                await tts_service._generate_audio_volcengine(
                    "测试文本", "BV001_streaming", {"speed": 1.0, "pitch": 1.0, "volume": 1.0}
                )


class TestAudioFileSaving:
    """音频文件保存测试"""
    
    def setup_method(self):
        """设置测试环境"""
        os.environ["VOLCENGINE_APPID"] = "test_appid"
        os.environ["VOLCENGINE_ACCESS_TOKEN"] = "test_token"
        os.environ["VOLCENGINE_CLUSTER"] = "volcano_tts"
    
    @pytest.mark.asyncio
    async def test_save_audio_file(self, temp_output_dir, mock_volcengine_response):
        """测试保存音频文件"""
        tts_service = Stage4TTSService(output_dir=temp_output_dir)
        
        # 模拟火山引擎响应
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value=mock_volcengine_response)
            mock_post.return_value.__aenter__.return_value = mock_response
            
            # 生成并保存音频
            text = "测试音频内容"
            voice = "BV001_streaming"
            emotion_params = {"speed": 1.0, "pitch": 1.0, "volume": 1.0}
            output_path = Path(temp_output_dir) / "test_audio.mp3"
            
            audio_data = await tts_service._generate_audio_volcengine(
                text, voice, output_path, emotion_params
            )
            
            # 验证音频数据
            assert audio_data is not None
            assert len(audio_data) > 0
    
