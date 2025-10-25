"""
Stage4 TTS 单元测试
测试火山引擎 TTS 音频生成相关的基础功能
"""

import pytest
import os
import sys
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


class TestVoiceMapping:
    """音色映射测试"""
    
    def test_assign_voice(self):
        """测试角色音色分配"""
        tts_service = Stage4TTSService(output_dir="./test_output")
        
        # 测试中年男性角色
        character = Character(
            id="char_001",
            name="Wang Miao",
            description="A middle-aged man in his 40s",
            age=45,
            gender="male"
        )
        voice = tts_service._assign_voice(character.id, [character], is_narration=False)
        assert voice == "BV700_streaming"  # 标准男声
        
        # 测试年轻女性角色
        character = Character(
            id="char_002",
            name="Xiao Li",
            description="A young female in her 20s",
            age=25,
            gender="female"
        )
        voice = tts_service._assign_voice(character.id, [character], is_narration=False)
        assert voice == "BV001_streaming"  # 标准女声
    
    def test_narrator_voice(self):
        """测试旁白音色"""
        tts_service = Stage4TTSService(output_dir="./test_output")
        voice = tts_service._assign_voice(None, None, is_narration=True)
        assert voice == "BV001_streaming"  # 标准女声


class TestEmotionMapping:
    """情绪参数映射测试"""
    
    def test_map_emotion_to_params(self):
        """测试情绪到语音参数的映射"""
        tts_service = Stage4TTSService(output_dir="./test_output")
        
        # 测试愤怒情绪
        emotion = "Anxious and confused"
        params = tts_service._map_emotion_to_params(emotion)
        assert "speed" in params
        assert "pitch" in params
        assert "volume" in params
        assert params["speed"] == 1.1
        assert params["pitch"] == 1.1
        
        # 测试悲伤情绪
        emotion = "Sad and depressed"
        params = tts_service._map_emotion_to_params(emotion)
        assert params["speed"] == 0.9
        assert params["pitch"] == 0.9
        
        # 测试默认情绪
        emotion = "Unknown emotion"
        params = tts_service._map_emotion_to_params(emotion)
        assert params["speed"] == 1.0
        assert params["pitch"] == 1.0


class TestDurationEstimation:
    """音频时长估算测试"""
    
    def test_estimate_chinese_duration(self):
        """测试中文文本时长估算"""
        tts_service = Stage4TTSService(output_dir="./test_output")
        
        text = "深夜，汪淼站在窗前，望着天空中闪烁的星星。"  # 20字
        duration = tts_service._estimate_duration(text)
        assert 5.0 <= duration <= 7.0  # 约3-4字/秒
    
    def test_estimate_english_duration(self):
        """测试英文文本时长估算"""
        tts_service = Stage4TTSService(output_dir="./test_output")
        
        text = "This is a test sentence."
        duration = tts_service._estimate_duration(text)
        assert duration > 0
        assert duration < 5.0  # 英文通常比中文快


class TestVolcengineTTSIntegration:
    """火山引擎 TTS 集成测试"""
    
    def setup_method(self):
        """设置测试环境"""
        # 设置环境变量（测试用）
        os.environ["VOLCENGINE_APPID"] = "test_appid"
        os.environ["VOLCENGINE_ACCESS_TOKEN"] = "test_token"
        os.environ["VOLCENGINE_CLUSTER"] = "volcano_tts"
    
    @pytest.mark.asyncio
    async def test_volcengine_tts_mock_generation(self):
        """测试火山引擎 TTS 模拟音频生成"""
        tts_service = Stage4TTSService(output_dir="./test_output")
        
        # 模拟火山引擎响应
        mock_response_data = {
            "code": 3000,
            "message": "success",
            "data": {
                "audio": "base64_encoded_audio_data"
            }
        }
        
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value=mock_response_data)
            mock_post.return_value.__aenter__.return_value = mock_response
            
            # 测试音频生成
            text = "深夜，汪淼站在窗前。"
            voice = "BV001_streaming"
            output_path = "./test_output/test_audio1.mp3"
            emotion_params = {"speed": 1.0, "pitch": 1.0, "volume": 1.0}
            
            audio_data = await tts_service._generate_audio_volcengine(
                text=text,
                voice=voice,
                output_path=output_path,
                emotion_params=emotion_params
            )
            
            assert audio_data is not None
            assert len(audio_data) > 0
    
    @pytest.mark.asyncio
    async def test_volcengine_tts_error_handling(self):
        """测试火山引擎 TTS 错误处理"""
        tts_service = Stage4TTSService(output_dir="./test_output")
        
        # 模拟错误响应
        mock_response_data = {
            "code": 4001,
            "message": "Invalid request",
            "data": None
        }
        
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value=mock_response_data)
            mock_post.return_value.__aenter__.return_value = mock_response
            
            # 测试错误处理
            text = "测试文本"
            voice = "BV001_streaming"
            output_path = "./test_output/test_audio2.mp3"
            emotion_params = {"speed": 1.0, "pitch": 1.0, "volume": 1.0}
            
            with pytest.raises(Exception):
                await tts_service._generate_audio_volcengine(
                    text, voice, output_path, emotion_params
                )


class TestAudioGeneration:
    """音频生成测试"""
    
    def setup_method(self):
        """设置测试环境"""
        os.environ["VOLCENGINE_APPID"] = "test_appid"
        os.environ["VOLCENGINE_ACCESS_TOKEN"] = "test_token"
        os.environ["VOLCENGINE_CLUSTER"] = "volcano_tts"
    
    @pytest.mark.asyncio
    async def test_generate_narration_audio(self):
        """测试生成旁白音频"""
        tts_service = Stage4TTSService(output_dir="./test_output")
        
        # 模拟火山引擎响应
        mock_response_data = {
            "code": 3000,
            "message": "success",
            "data": {
                "audio": "base64_encoded_audio_data"
            }
        }
        
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value=mock_response_data)
            mock_post.return_value.__aenter__.return_value = mock_response
            
            text = "深夜，汪淼站在窗前。"
            output_path = "./test_output/test_audio3.mp3"
            audio_data = await tts_service._generate_audio_volcengine(
                text, "BV001_streaming", output_path, {"speed": 1.0, "pitch": 1.0, "volume": 1.0}
            )
            
            assert audio_data is not None
            assert len(audio_data) > 0
    
    @pytest.mark.asyncio
    async def test_generate_dialogue_audio(self):
        """测试生成对话音频"""
        tts_service = Stage4TTSService(output_dir="./test_output")
        
        # 模拟火山引擎响应
        mock_response_data = {
            "code": 3000,
            "message": "success",
            "data": {
                "audio": "base64_encoded_audio_data"
            }
        }
        
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value=mock_response_data)
            mock_post.return_value.__aenter__.return_value = mock_response
            
            text = "这到底是什么？"
            output_path = "./test_output/test_audio4.mp3"
            audio_data = await tts_service._generate_audio_volcengine(
                text, "BV700_streaming", output_path, {"speed": 1.1, "pitch": 1.1, "volume": 1.0}
            )
            
            assert audio_data is not None
            assert len(audio_data) > 0
