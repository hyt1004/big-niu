"""
Stage5 视频合成单元测试
测试视频合成相关的基础功能
"""

import pytest
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock, call
import tempfile
import shutil

project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

backend_path = project_root / "backend"
sys.path.insert(0, str(backend_path))

from app.services.stage5_video_composition import (
    Stage5VideoCompositionService,
    SubtitleEntry,
    Stage5Output,
)


class TestSubtitleEntry:
    """字幕条目测试"""

    def test_subtitle_entry_creation(self):
        """测试字幕条目创建"""
        entry = SubtitleEntry(
            index=1,
            start_time=0.0,
            end_time=3.5,
            text="这是测试字幕",
        )
        
        assert entry.index == 1
        assert entry.start_time == 0.0
        assert entry.end_time == 3.5
        assert entry.text == "这是测试字幕"
    
    def test_subtitle_timestamp_formatting(self):
        """测试时间戳格式化"""
        entry = SubtitleEntry(
            index=1,
            start_time=0.0,
            end_time=3.5,
            text="测试",
        )
        
        srt_output = entry.to_srt_format()
        
        assert "1" in srt_output
        assert "00:00:00,000 --> 00:00:03,500" in srt_output
        assert "测试" in srt_output
    
    def test_subtitle_timestamp_with_hours(self):
        """测试小时级时间戳格式化"""
        entry = SubtitleEntry(
            index=10,
            start_time=3661.5,
            end_time=3665.250,
            text="长时间字幕",
        )
        
        srt_output = entry.to_srt_format()
        
        assert "01:01:01,500 --> 01:01:05,250" in srt_output
    
    def test_subtitle_srt_format_structure(self):
        """测试SRT格式结构"""
        entry = SubtitleEntry(
            index=5,
            start_time=10.0,
            end_time=15.0,
            text="格式测试",
        )
        
        srt_output = entry.to_srt_format()
        lines = srt_output.strip().split('\n')
        
        assert len(lines) == 3
        assert lines[0] == "5"
        assert "-->" in lines[1]
        assert lines[2] == "格式测试"


class TestStage5Output:
    """Stage5输出数据模型测试"""

    def test_stage5_output_creation(self):
        """测试输出对象创建"""
        output = Stage5Output(
            video_id="test_video_001",
            video_path="/path/to/video.mp4",
            video_url="https://cdn.example.com/video.mp4",
            duration=125.5,
            resolution="1920x1080",
            file_size=45678901,
            format="mp4",
            scenes_count=10,
        )
        
        assert output.video_id == "test_video_001"
        assert output.duration == 125.5
        assert output.scenes_count == 10
    
    def test_stage5_output_to_dict(self):
        """测试输出对象转字典"""
        output = Stage5Output(
            video_id="test_video_002",
            video_path="/path/to/video.mp4",
            video_url=None,
            duration=60.0,
            resolution="1920x1080",
            file_size=12345678,
            format="mp4",
            scenes_count=5,
        )
        
        output_dict = output.to_dict()
        
        assert output_dict["video_id"] == "test_video_002"
        assert output_dict["duration"] == 60.0
        assert output_dict["video_url"] is None
        assert output_dict["scenes_count"] == 5


class TestVideoCompositionService:
    """视频合成服务基础测试"""

    @pytest.fixture
    def temp_dirs(self):
        """创建临时目录"""
        output_dir = tempfile.mkdtemp()
        temp_dir = tempfile.mkdtemp()
        yield output_dir, temp_dir
        shutil.rmtree(output_dir)
        shutil.rmtree(temp_dir)
    
    def test_service_initialization(self, temp_dirs):
        """测试服务初始化"""
        output_dir, temp_dir = temp_dirs
        
        service = Stage5VideoCompositionService(
            output_dir=output_dir,
            temp_dir=temp_dir,
        )
        
        assert service.output_dir == output_dir
        assert service.temp_dir == temp_dir
        assert os.path.exists(output_dir)
        assert os.path.exists(temp_dir)
    
    def test_generate_subtitles_structure(self, temp_dirs):
        """测试字幕生成结构"""
        output_dir, temp_dir = temp_dirs
        service = Stage5VideoCompositionService(output_dir, temp_dir)
        
        stage4_data = {
            "scenes": [
                {
                    "scene_id": "scene_001",
                    "audio_segments": [
                        {
                            "type": "narration",
                            "text": "第一段旁白",
                            "start_time": 0.0,
                            "duration": 3.0,
                        },
                        {
                            "type": "dialogue",
                            "text": "第一句对话",
                            "start_time": 3.0,
                            "duration": 2.0,
                        },
                    ],
                },
            ],
        }
        
        subtitle_path = os.path.join(temp_dir, "test_subtitles.srt")
        result = service._generate_subtitles(stage4_data, subtitle_path)
        
        assert os.path.exists(result)
        
        with open(result, "r", encoding="utf-8") as f:
            content = f.read()
            assert "第一段旁白" in content
            assert "第一句对话" in content
            assert "00:00:00,000 --> 00:00:03,000" in content
            assert "00:00:03,000 --> 00:00:05,000" in content
    
    def test_generate_subtitles_multiple_scenes(self, temp_dirs):
        """测试多场景字幕生成"""
        output_dir, temp_dir = temp_dirs
        service = Stage5VideoCompositionService(output_dir, temp_dir)
        
        stage4_data = {
            "scenes": [
                {
                    "scene_id": "scene_001",
                    "audio_segments": [
                        {
                            "type": "narration",
                            "text": "场景1旁白",
                            "start_time": 0.0,
                            "duration": 2.0,
                        },
                    ],
                },
                {
                    "scene_id": "scene_002",
                    "audio_segments": [
                        {
                            "type": "narration",
                            "text": "场景2旁白",
                            "start_time": 0.0,
                            "duration": 3.0,
                        },
                    ],
                },
            ],
        }
        
        subtitle_path = os.path.join(temp_dir, "test_subtitles2.srt")
        result = service._generate_subtitles(stage4_data, subtitle_path)
        
        assert os.path.exists(result)
        
        with open(result, "r", encoding="utf-8") as f:
            content = f.read()
            assert "场景1旁白" in content
            assert "场景2旁白" in content


class TestFFmpegCommands:
    """FFmpeg命令生成测试"""

    @pytest.fixture
    def temp_dirs(self):
        """创建临时目录"""
        output_dir = tempfile.mkdtemp()
        temp_dir = tempfile.mkdtemp()
        yield output_dir, temp_dir
        shutil.rmtree(output_dir)
        shutil.rmtree(temp_dir)
    
    @patch('subprocess.run')
    def test_create_scene_video_command(self, mock_run, temp_dirs):
        """测试场景视频创建命令"""
        output_dir, temp_dir = temp_dirs
        service = Stage5VideoCompositionService(output_dir, temp_dir)
        
        mock_run.return_value = MagicMock(returncode=0, stderr="")
        
        image_path = "test_image.png"
        duration = 5.5
        output_path = os.path.join(temp_dir, "scene_video.mp4")
        
        service._create_scene_video(image_path, duration, output_path)
        
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        
        assert "ffmpeg" in call_args
        assert "-loop" in call_args
        assert "1" in call_args
        assert "-t" in call_args
        assert str(duration) in call_args
        assert "-i" in call_args
        assert image_path in call_args
        assert output_path in call_args
    
    @patch('subprocess.run')
    def test_merge_audio_segments_command(self, mock_run, temp_dirs):
        """测试音频合并命令"""
        output_dir, temp_dir = temp_dirs
        service = Stage5VideoCompositionService(output_dir, temp_dir)
        
        mock_run.return_value = MagicMock(returncode=0, stderr="")
        
        audio_paths = ["audio1.mp3", "audio2.mp3", "audio3.mp3"]
        output_path = os.path.join(temp_dir, "merged_audio.mp3")
        
        service._merge_audio_segments(audio_paths, output_path)
        
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        
        assert "ffmpeg" in call_args
        assert "-f" in call_args
        assert "concat" in call_args
        assert output_path in call_args
    
    @patch('subprocess.run')
    def test_merge_videos_command(self, mock_run, temp_dirs):
        """测试视频合并命令"""
        output_dir, temp_dir = temp_dirs
        service = Stage5VideoCompositionService(output_dir, temp_dir)
        
        mock_run.return_value = MagicMock(returncode=0, stderr="")
        
        video_paths = ["video1.mp4", "video2.mp4"]
        output_path = os.path.join(temp_dir, "merged_video.mp4")
        
        service._merge_videos(video_paths, output_path)
        
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        
        assert "ffmpeg" in call_args
        assert "-f" in call_args
        assert "concat" in call_args
        assert output_path in call_args
    
    @patch('subprocess.run')
    def test_add_audio_and_subtitles_command(self, mock_run, temp_dirs):
        """测试添加音频和字幕命令"""
        output_dir, temp_dir = temp_dirs
        service = Stage5VideoCompositionService(output_dir, temp_dir)
        
        mock_run.return_value = MagicMock(returncode=0, stderr="")
        
        video_path = "video.mp4"
        audio_path = "audio.mp3"
        subtitle_path = "subtitles.srt"
        output_path = os.path.join(temp_dir, "final_video.mp4")
        
        service._add_audio_and_subtitles(
            video_path, audio_path, subtitle_path, output_path
        )
        
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        
        assert "ffmpeg" in call_args
        assert "-i" in call_args
        assert video_path in call_args
        assert audio_path in call_args
        assert "-vf" in call_args
        assert f"subtitles={subtitle_path}" in str(call_args)
        assert output_path in call_args


class TestErrorHandling:
    """错误处理测试"""

    @pytest.fixture
    def temp_dirs(self):
        """创建临时目录"""
        output_dir = tempfile.mkdtemp()
        temp_dir = tempfile.mkdtemp()
        yield output_dir, temp_dir
        shutil.rmtree(output_dir)
        shutil.rmtree(temp_dir)
    
    @patch('subprocess.run')
    def test_ffmpeg_failure_handling(self, mock_run, temp_dirs):
        """测试FFmpeg失败处理"""
        output_dir, temp_dir = temp_dirs
        service = Stage5VideoCompositionService(output_dir, temp_dir)
        
        mock_run.return_value = MagicMock(
            returncode=1,
            stderr="FFmpeg error: invalid input"
        )
        
        with pytest.raises(ValueError, match="FFmpeg failed"):
            service._create_scene_video(
                "invalid_image.png",
                5.0,
                os.path.join(temp_dir, "output.mp4")
            )
    
    def test_compose_video_simple_input_validation(self, temp_dirs):
        """测试简单合成输入验证"""
        output_dir, temp_dir = temp_dirs
        service = Stage5VideoCompositionService(output_dir, temp_dir)
        
        with pytest.raises(ValueError, match="must have the same length"):
            service.compose_video_simple(
                image_paths=["img1.png", "img2.png"],
                audio_paths=["audio1.mp3"],
                durations=[5.0],
                subtitle_texts=[],
                video_id="test_video"
            )


class TestVideoResolutionAndFormat:
    """视频分辨率和格式测试"""

    @pytest.fixture
    def temp_dirs(self):
        """创建临时目录"""
        output_dir = tempfile.mkdtemp()
        temp_dir = tempfile.mkdtemp()
        yield output_dir, temp_dir
        shutil.rmtree(output_dir)
        shutil.rmtree(temp_dir)
    
    @patch('subprocess.run')
    def test_video_resolution_1920x1080(self, mock_run, temp_dirs):
        """测试1920x1080分辨率设置"""
        output_dir, temp_dir = temp_dirs
        service = Stage5VideoCompositionService(output_dir, temp_dir)
        
        mock_run.return_value = MagicMock(returncode=0, stderr="")
        
        service._create_scene_video(
            "test.png",
            5.0,
            os.path.join(temp_dir, "output.mp4")
        )
        
        call_args = mock_run.call_args[0][0]
        assert "scale=1920:1080" in str(call_args)
    
    @patch('subprocess.run')
    def test_video_codec_h264(self, mock_run, temp_dirs):
        """测试H.264编码器设置"""
        output_dir, temp_dir = temp_dirs
        service = Stage5VideoCompositionService(output_dir, temp_dir)
        
        mock_run.return_value = MagicMock(returncode=0, stderr="")
        
        service._create_scene_video(
            "test.png",
            5.0,
            os.path.join(temp_dir, "output.mp4")
        )
        
        call_args = mock_run.call_args[0][0]
        assert "libx264" in call_args
