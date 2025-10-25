"""
Stage5 视频合成功能测试
测试完整的视频合成功能
"""

import pytest
import json
import os
import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

backend_path = project_root / "backend"
sys.path.insert(0, str(backend_path))

from app.services.stage5_video_composition import (
    Stage5VideoCompositionService,
    Stage5Output,
)


MOCKDATA_DIR = Path(__file__).parent / "mockdata"
STAGE4_OUTPUT = MOCKDATA_DIR / "stage4_output.json"


@pytest.fixture
def stage4_data():
    """加载 Stage4 输出数据"""
    with open(STAGE4_OUTPUT, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def temp_output_dir():
    """创建临时输出目录"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_image_files(temp_output_dir):
    """创建模拟图像文件"""
    image_dir = os.path.join(temp_output_dir, "images")
    os.makedirs(image_dir, exist_ok=True)
    
    image_paths = []
    for i in range(1, 4):
        image_path = os.path.join(image_dir, f"scene_{i:03d}.png")
        with open(image_path, "wb") as f:
            f.write(b"PNG_MOCK_DATA")
        image_paths.append(image_path)
    
    return image_paths


@pytest.fixture
def mock_audio_files(temp_output_dir):
    """创建模拟音频文件"""
    audio_dir = os.path.join(temp_output_dir, "audio")
    os.makedirs(audio_dir, exist_ok=True)
    
    audio_paths = []
    for i in range(1, 8):
        audio_path = os.path.join(audio_dir, f"audio_{i:03d}.mp3")
        with open(audio_path, "wb") as f:
            f.write(b"MP3_MOCK_DATA")
        audio_paths.append(audio_path)
    
    return audio_paths


class TestMockDataValidation:
    """Mock 数据验证测试"""

    def test_stage4_output_exists(self):
        """测试 Stage4 输出文件存在"""
        assert STAGE4_OUTPUT.exists()
    
    def test_stage4_output_structure(self, stage4_data):
        """测试 Stage4 输出结构"""
        assert "scenes" in stage4_data
        assert "total_video_duration" in stage4_data
        assert len(stage4_data["scenes"]) == 3
    
    def test_stage4_scenes_have_required_fields(self, stage4_data):
        """测试场景包含必需字段"""
        for scene in stage4_data["scenes"]:
            assert "scene_id" in scene
            assert "image_path" in scene
            assert "audio_segments" in scene
            assert "total_duration" in scene
    
    def test_audio_segments_have_required_fields(self, stage4_data):
        """测试音频段包含必需字段"""
        for scene in stage4_data["scenes"]:
            for segment in scene["audio_segments"]:
                assert "type" in segment
                assert "text" in segment
                assert "audio_path" in segment
                assert "duration" in segment
                assert "start_time" in segment


class TestSubtitleGeneration:
    """字幕生成功能测试"""

    def test_generate_subtitles_from_stage4(self, stage4_data, temp_output_dir):
        """测试从Stage4数据生成字幕"""
        service = Stage5VideoCompositionService(
            output_dir=temp_output_dir,
            temp_dir=temp_output_dir
        )
        
        subtitle_path = os.path.join(temp_output_dir, "test_subtitles.srt")
        result = service._generate_subtitles(stage4_data, subtitle_path)
        
        assert os.path.exists(result)
        assert result == subtitle_path
        
        with open(result, "r", encoding="utf-8") as f:
            content = f.read()
            
            assert "深夜，汪淼站在窗前" in content
            assert "这到底是什么？" in content
            assert "三体文明正在接近地球" in content
    
    def test_subtitle_timing_accuracy(self, stage4_data, temp_output_dir):
        """测试字幕时间轴准确性"""
        service = Stage5VideoCompositionService(
            output_dir=temp_output_dir,
            temp_dir=temp_output_dir
        )
        
        subtitle_path = os.path.join(temp_output_dir, "timing_test.srt")
        service._generate_subtitles(stage4_data, subtitle_path)
        
        with open(subtitle_path, "r", encoding="utf-8") as f:
            content = f.read()
            
            assert "00:00:00,000 --> 00:00:12,500" in content
            assert "00:00:12,500 --> 00:00:14,000" in content
    
    def test_subtitle_index_sequence(self, stage4_data, temp_output_dir):
        """测试字幕索引序列"""
        service = Stage5VideoCompositionService(
            output_dir=temp_output_dir,
            temp_dir=temp_output_dir
        )
        
        subtitle_path = os.path.join(temp_output_dir, "index_test.srt")
        service._generate_subtitles(stage4_data, subtitle_path)
        
        with open(subtitle_path, "r", encoding="utf-8") as f:
            content = f.read()
            lines = content.strip().split('\n')
            
            indices = []
            for line in lines:
                if line.strip().isdigit():
                    indices.append(int(line.strip()))
            
            assert indices == list(range(1, len(indices) + 1))


class TestSimpleVideoComposition:
    """简单视频合成测试"""

    @patch('subprocess.run')
    def test_compose_video_simple_basic(self, mock_run, mock_image_files, mock_audio_files, temp_output_dir):
        """测试基本的简单视频合成"""
        mock_run.return_value = MagicMock(returncode=0, stderr="")
        
        service = Stage5VideoCompositionService(
            output_dir=temp_output_dir,
            temp_dir=temp_output_dir
        )
        
        image_paths = mock_image_files[:2]
        audio_paths = mock_audio_files[:2]
        durations = [5.0, 4.0]
        subtitle_texts = [
            (0.0, 5.0, "第一段字幕"),
            (5.0, 9.0, "第二段字幕"),
        ]
        
        output_path = os.path.join(temp_output_dir, "test_video.mp4")
        with open(output_path, "wb") as f:
            f.write(b"MOCK_VIDEO_DATA")
        
        result = service.compose_video_simple(
            image_paths=image_paths,
            audio_paths=audio_paths,
            durations=durations,
            subtitle_texts=subtitle_texts,
            video_id="test_video_001",
        )
        
        assert isinstance(result, Stage5Output)
        assert result.video_id == "test_video_001"
        assert result.duration == 9.0
        assert result.scenes_count == 2
        assert result.resolution == "1920x1080"
        assert result.format == "mp4"
    
    @patch('subprocess.run')
    def test_compose_video_simple_multiple_scenes(self, mock_run, mock_image_files, mock_audio_files, temp_output_dir):
        """测试多场景简单合成"""
        mock_run.return_value = MagicMock(returncode=0, stderr="")
        
        service = Stage5VideoCompositionService(
            output_dir=temp_output_dir,
            temp_dir=temp_output_dir
        )
        
        image_paths = mock_image_files
        audio_paths = mock_audio_files[:3]
        durations = [3.0, 4.5, 5.0]
        subtitle_texts = [
            (0.0, 3.0, "场景1"),
            (3.0, 7.5, "场景2"),
            (7.5, 12.5, "场景3"),
        ]
        
        output_path = os.path.join(temp_output_dir, "multi_scene.mp4")
        with open(output_path, "wb") as f:
            f.write(b"MOCK_VIDEO_DATA")
        
        result = service.compose_video_simple(
            image_paths=image_paths,
            audio_paths=audio_paths,
            durations=durations,
            subtitle_texts=subtitle_texts,
            video_id="multi_scene_001",
        )
        
        assert result.scenes_count == 3
        assert result.duration == 12.5


class TestFullVideoComposition:
    """完整视频合成测试"""

    @patch('subprocess.run')
    def test_compose_video_with_stage3_and_stage4_data(self, mock_run, stage4_data, mock_image_files, temp_output_dir):
        """测试使用Stage3和Stage4数据合成视频"""
        mock_run.return_value = MagicMock(returncode=0, stderr="")
        
        service = Stage5VideoCompositionService(
            output_dir=temp_output_dir,
            temp_dir=temp_output_dir
        )
        
        stage3_data = []
        for i, scene in enumerate(stage4_data["scenes"]):
            stage3_data.append({
                "scene_id": scene["scene_id"],
                "image_path": mock_image_files[i],
            })
        
        output_path = os.path.join(temp_output_dir, "test_full_video_001.mp4")
        with open(output_path, "wb") as f:
            f.write(b"MOCK_VIDEO_DATA")
        
        result = service.compose_video(
            stage3_data=stage3_data,
            stage4_data=stage4_data,
            video_id="test_full_video_001",
        )
        
        assert isinstance(result, Stage5Output)
        assert result.video_id == "test_full_video_001"
        assert result.scenes_count == 3
        assert result.duration == stage4_data["total_video_duration"]
        assert result.format == "mp4"
        assert result.file_size > 0


class TestVideoProcessingPipeline:
    """视频处理流程测试"""

    @patch('subprocess.run')
    def test_scene_video_creation(self, mock_run, mock_image_files, temp_output_dir):
        """测试场景视频创建"""
        mock_run.return_value = MagicMock(returncode=0, stderr="")
        
        service = Stage5VideoCompositionService(
            output_dir=temp_output_dir,
            temp_dir=temp_output_dir
        )
        
        image_path = mock_image_files[0]
        duration = 5.0
        output_path = os.path.join(temp_output_dir, "scene_video.mp4")
        
        with open(output_path, "wb") as f:
            f.write(b"MOCK_VIDEO")
        
        result = service._create_scene_video(image_path, duration, output_path)
        
        assert result == output_path
        mock_run.assert_called_once()
    
    @patch('subprocess.run')
    def test_audio_merging(self, mock_run, mock_audio_files, temp_output_dir):
        """测试音频合并"""
        mock_run.return_value = MagicMock(returncode=0, stderr="")
        
        service = Stage5VideoCompositionService(
            output_dir=temp_output_dir,
            temp_dir=temp_output_dir
        )
        
        audio_paths = mock_audio_files[:3]
        output_path = os.path.join(temp_output_dir, "merged_audio.mp3")
        
        with open(output_path, "wb") as f:
            f.write(b"MERGED_AUDIO")
        
        result = service._merge_audio_segments(audio_paths, output_path)
        
        assert result == output_path
        mock_run.assert_called_once()
    
    @patch('subprocess.run')
    def test_video_merging(self, mock_run, temp_output_dir):
        """测试视频合并"""
        mock_run.return_value = MagicMock(returncode=0, stderr="")
        
        service = Stage5VideoCompositionService(
            output_dir=temp_output_dir,
            temp_dir=temp_output_dir
        )
        
        video_dir = os.path.join(temp_output_dir, "videos")
        os.makedirs(video_dir, exist_ok=True)
        
        video_paths = []
        for i in range(3):
            video_path = os.path.join(video_dir, f"video_{i}.mp4")
            with open(video_path, "wb") as f:
                f.write(b"VIDEO_DATA")
            video_paths.append(video_path)
        
        output_path = os.path.join(temp_output_dir, "merged_video.mp4")
        with open(output_path, "wb") as f:
            f.write(b"MERGED_VIDEO")
        
        result = service._merge_videos(video_paths, output_path)
        
        assert result == output_path
        mock_run.assert_called_once()
    
    @patch('subprocess.run')
    def test_add_audio_and_subtitles(self, mock_run, mock_audio_files, temp_output_dir):
        """测试添加音频和字幕"""
        mock_run.return_value = MagicMock(returncode=0, stderr="")
        
        service = Stage5VideoCompositionService(
            output_dir=temp_output_dir,
            temp_dir=temp_output_dir
        )
        
        video_path = os.path.join(temp_output_dir, "video.mp4")
        with open(video_path, "wb") as f:
            f.write(b"VIDEO")
        
        audio_path = mock_audio_files[0]
        
        subtitle_path = os.path.join(temp_output_dir, "subtitles.srt")
        with open(subtitle_path, "w", encoding="utf-8") as f:
            f.write("1\n00:00:00,000 --> 00:00:05,000\n测试字幕\n\n")
        
        output_path = os.path.join(temp_output_dir, "final_video.mp4")
        with open(output_path, "wb") as f:
            f.write(b"FINAL_VIDEO")
        
        result = service._add_audio_and_subtitles(
            video_path, audio_path, subtitle_path, output_path
        )
        
        assert result == output_path
        mock_run.assert_called_once()


class TestErrorHandling:
    """错误处理测试"""

    def test_missing_image_for_scene(self, stage4_data, temp_output_dir):
        """测试缺失场景图像的错误处理"""
        service = Stage5VideoCompositionService(
            output_dir=temp_output_dir,
            temp_dir=temp_output_dir
        )
        
        stage3_data = [
            {
                "scene_id": "scene_001",
                "image_path": "/nonexistent/image.png",
            }
        ]
        
        with pytest.raises(ValueError, match="Image not found"):
            service.compose_video(
                stage3_data=stage3_data,
                stage4_data=stage4_data,
                video_id="error_test",
            )
    
    @patch('subprocess.run')
    def test_ffmpeg_error_handling(self, mock_run, mock_image_files, temp_output_dir):
        """测试FFmpeg错误处理"""
        mock_run.return_value = MagicMock(
            returncode=1,
            stderr="FFmpeg error: invalid codec"
        )
        
        service = Stage5VideoCompositionService(
            output_dir=temp_output_dir,
            temp_dir=temp_output_dir
        )
        
        with pytest.raises(ValueError, match="FFmpeg failed"):
            service._create_scene_video(
                mock_image_files[0],
                5.0,
                os.path.join(temp_output_dir, "output.mp4")
            )


class TestOutputValidation:
    """输出验证测试"""

    @patch('subprocess.run')
    def test_output_video_path_exists(self, mock_run, mock_image_files, mock_audio_files, temp_output_dir):
        """测试输出视频路径存在"""
        mock_run.return_value = MagicMock(returncode=0, stderr="")
        
        service = Stage5VideoCompositionService(
            output_dir=temp_output_dir,
            temp_dir=temp_output_dir
        )
        
        output_path = os.path.join(temp_output_dir, "test_output.mp4")
        with open(output_path, "wb") as f:
            f.write(b"VIDEO_DATA")
        
        result = service.compose_video_simple(
            image_paths=mock_image_files[:1],
            audio_paths=mock_audio_files[:1],
            durations=[5.0],
            subtitle_texts=[(0.0, 5.0, "测试")],
            video_id="test_output",
        )
        
        assert os.path.exists(result.video_path)
    
    @patch('subprocess.run')
    def test_output_metadata_accuracy(self, mock_run, mock_image_files, mock_audio_files, temp_output_dir):
        """测试输出元数据准确性"""
        mock_run.return_value = MagicMock(returncode=0, stderr="")
        
        service = Stage5VideoCompositionService(
            output_dir=temp_output_dir,
            temp_dir=temp_output_dir
        )
        
        output_path = os.path.join(temp_output_dir, "metadata_test.mp4")
        with open(output_path, "wb") as f:
            f.write(b"VIDEO_DATA_12345")
        
        result = service.compose_video_simple(
            image_paths=mock_image_files[:2],
            audio_paths=mock_audio_files[:2],
            durations=[3.0, 4.0],
            subtitle_texts=[(0.0, 3.0, "A"), (3.0, 7.0, "B")],
            video_id="metadata_test",
        )
        
        assert result.video_id == "metadata_test"
        assert result.duration == 7.0
        assert result.resolution == "1920x1080"
        assert result.format == "mp4"
        assert result.file_size > 0
