"""
Stage5 视频合成验收测试
使用真实mockdata进行端到端测试验证
"""

import pytest
import json
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

backend_path = project_root / "backend"
sys.path.insert(0, str(backend_path))

from app.services.stage5_video_composition import (
    Stage5VideoCompositionService,
    SubtitleEntry,
    Stage5Output,
)


MOCKDATA_DIR = Path(__file__).parent / "mockdata"
STAGE4_OUTPUT = MOCKDATA_DIR / "stage4_output.json"
EXPECTED_SUBTITLES = MOCKDATA_DIR / "expected_subtitles.srt"
IMAGES_DIR = MOCKDATA_DIR / "images"
AUDIO_DIR = MOCKDATA_DIR / "audio"


class TestMockDataIntegrity:
    """验收测试 - Mock数据完整性"""

    def test_all_mockdata_files_exist(self):
        """验证所有必需的mockdata文件都存在"""
        assert MOCKDATA_DIR.exists(), "mockdata目录不存在"
        assert STAGE4_OUTPUT.exists(), "stage4_output.json不存在"
        assert EXPECTED_SUBTITLES.exists(), "expected_subtitles.srt不存在"
        assert IMAGES_DIR.exists(), "images目录不存在"
        assert AUDIO_DIR.exists(), "audio目录不存在"

    def test_image_files_exist_and_readable(self):
        """验证图像文件存在且可读"""
        for i in range(1, 4):
            image_path = IMAGES_DIR / f"scene_{i:03d}.png"
            assert image_path.exists(), f"图像文件 {image_path} 不存在"
            assert os.path.getsize(image_path) > 0, f"图像文件 {image_path} 为空"

    def test_audio_files_exist_and_readable(self):
        """验证音频文件存在且可读"""
        with open(STAGE4_OUTPUT, "r", encoding="utf-8") as f:
            stage4_data = json.load(f)
        
        for scene in stage4_data["scenes"]:
            for segment in scene["audio_segments"]:
                audio_path = Path(segment["audio_path"])
                assert audio_path.exists(), f"音频文件 {audio_path} 不存在"
                assert os.path.getsize(audio_path) > 0, f"音频文件 {audio_path} 为空"

    def test_stage4_output_format_correctness(self):
        """验证stage4_output.json格式正确性"""
        with open(STAGE4_OUTPUT, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        assert "scenes" in data, "缺少scenes字段"
        assert "total_video_duration" in data, "缺少total_video_duration字段"
        assert isinstance(data["scenes"], list), "scenes应为列表"
        assert len(data["scenes"]) == 3, "应有3个场景"
        assert data["total_video_duration"] == 63.5, "总时长应为63.5秒"
        
        for scene in data["scenes"]:
            assert "scene_id" in scene, "场景缺少scene_id"
            assert "image_path" in scene, "场景缺少image_path"
            assert "audio_segments" in scene, "场景缺少audio_segments"
            assert "total_duration" in scene, "场景缺少total_duration"
            
            for segment in scene["audio_segments"]:
                assert "type" in segment, "音频段缺少type"
                assert "text" in segment, "音频段缺少text"
                assert "audio_path" in segment, "音频段缺少audio_path"
                assert "duration" in segment, "音频段缺少duration"
                assert "start_time" in segment, "音频段缺少start_time"

    def test_expected_subtitles_format_correctness(self):
        """验证expected_subtitles.srt格式正确性"""
        with open(EXPECTED_SUBTITLES, "r", encoding="utf-8") as f:
            content = f.read()
        
        assert content.strip(), "字幕文件为空"
        
        lines = content.strip().split('\n')
        assert len(lines) > 0, "字幕文件无内容"
        
        assert "00:00:00,000 --> 00:00:12,500" in content, "缺少第一条字幕时间戳"
        assert "深夜，汪淼站在窗前" in content, "缺少第一条字幕文本"
        assert "三体文明正在接近地球" in content, "缺少最后一条字幕文本"
        
        subtitle_indices = [i for i, line in enumerate(lines) if line.strip().isdigit()]
        assert len(subtitle_indices) == 13, "应有13条字幕"


class TestSubtitleGenerationAcceptance:
    """验收测试 - 字幕生成功能"""

    def test_generate_subtitles_matches_expected_format(self):
        """验证生成的字幕与预期格式匹配"""
        service = Stage5VideoCompositionService()
        
        with open(STAGE4_OUTPUT, "r", encoding="utf-8") as f:
            stage4_data = json.load(f)
        
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.srt', delete=False, encoding='utf-8') as f:
            subtitle_path = f.name
        
        try:
            service._generate_subtitles(stage4_data, subtitle_path)
            
            with open(subtitle_path, "r", encoding="utf-8") as f:
                generated = f.read()
            
            with open(EXPECTED_SUBTITLES, "r", encoding="utf-8") as f:
                expected = f.read()
            
            generated_lines = [line.strip() for line in generated.strip().split('\n') if line.strip()]
            expected_lines = [line.strip() for line in expected.strip().split('\n') if line.strip()]
            
            assert len(generated_lines) > 0, "生成的字幕为空"
            assert "深夜，汪淼站在窗前" in generated, "生成的字幕缺少关键文本"
            assert "三体文明正在接近地球" in generated, "生成的字幕缺少结尾文本"
            
            assert "00:00:00,000 --> 00:00:12,500" in generated, "字幕时间戳不正确"
            
        finally:
            if os.path.exists(subtitle_path):
                os.remove(subtitle_path)

    def test_subtitle_timing_alignment(self):
        """验证字幕时间轴对齐准确性"""
        service = Stage5VideoCompositionService()
        
        with open(STAGE4_OUTPUT, "r", encoding="utf-8") as f:
            stage4_data = json.load(f)
        
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.srt', delete=False, encoding='utf-8') as f:
            subtitle_path = f.name
        
        try:
            service._generate_subtitles(stage4_data, subtitle_path)
            
            with open(subtitle_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            expected_timestamps = [
                "00:00:00,000 --> 00:00:12,500",
                "00:00:12,500 --> 00:00:14,000",
                "00:00:14,000 --> 00:00:27,000",
                "00:00:27,000 --> 00:00:28,000",
                "00:00:28,000 --> 00:00:30,500",
            ]
            
            for timestamp in expected_timestamps:
                assert timestamp in content, f"缺少时间戳: {timestamp}"
        
        finally:
            if os.path.exists(subtitle_path):
                os.remove(subtitle_path)

    def test_subtitle_content_completeness(self):
        """验证字幕内容完整性"""
        service = Stage5VideoCompositionService()
        
        with open(STAGE4_OUTPUT, "r", encoding="utf-8") as f:
            stage4_data = json.load(f)
        
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.srt', delete=False, encoding='utf-8') as f:
            subtitle_path = f.name
        
        try:
            service._generate_subtitles(stage4_data, subtitle_path)
            
            with open(subtitle_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            total_segments = sum(len(scene["audio_segments"]) for scene in stage4_data["scenes"])
            
            subtitle_indices = content.count('\n\n')
            assert subtitle_indices >= total_segments - 1, f"字幕数量不足，应有{total_segments}条"
            
            key_texts = [
                "深夜，汪淼站在窗前",
                "这到底是什么？",
                "不可能！",
                "叶文洁教授，我是汪淼",
                "三体文明正在接近地球",
            ]
            
            for text in key_texts:
                assert text in content, f"缺少关键文本: {text}"
        
        finally:
            if os.path.exists(subtitle_path):
                os.remove(subtitle_path)


class TestVideoCompositionServiceAcceptance:
    """验收测试 - 视频合成服务"""

    @patch('subprocess.run')
    def test_service_initialization_with_mockdata(self, mock_run):
        """验证服务可以正常初始化"""
        import tempfile
        import shutil
        
        output_dir = tempfile.mkdtemp()
        temp_dir = tempfile.mkdtemp()
        
        try:
            service = Stage5VideoCompositionService(
                output_dir=output_dir,
                temp_dir=temp_dir,
            )
            
            assert service.output_dir == output_dir
            assert service.temp_dir == temp_dir
            assert os.path.exists(output_dir)
            assert os.path.exists(temp_dir)
        
        finally:
            shutil.rmtree(output_dir)
            shutil.rmtree(temp_dir)

    @patch('subprocess.run')
    def test_full_video_composition_workflow(self, mock_run):
        """验证完整的视频合成工作流"""
        mock_run.return_value = MagicMock(returncode=0, stderr="")
        
        import tempfile
        import shutil
        
        output_dir = tempfile.mkdtemp()
        temp_dir = tempfile.mkdtemp()
        
        try:
            service = Stage5VideoCompositionService(
                output_dir=output_dir,
                temp_dir=temp_dir,
            )
            
            with open(STAGE4_OUTPUT, "r", encoding="utf-8") as f:
                stage4_data = json.load(f)
            
            stage3_data = []
            for scene in stage4_data["scenes"]:
                stage3_data.append({
                    "scene_id": scene["scene_id"],
                    "image_path": scene["image_path"],
                })
            
            output_path = os.path.join(output_dir, "acceptance_test.mp4")
            with open(output_path, "wb") as f:
                f.write(b"MOCK_VIDEO_DATA")
            
            result = service.compose_video(
                stage3_data=stage3_data,
                stage4_data=stage4_data,
                video_id="acceptance_test",
            )
            
            assert isinstance(result, Stage5Output)
            assert result.video_id == "acceptance_test"
            assert result.scenes_count == 3
            assert result.duration == 63.5
            assert result.resolution == "1920x1080"
            assert result.format == "mp4"
            assert result.file_size > 0
            
            ffmpeg_call_count = mock_run.call_count
            assert ffmpeg_call_count >= 4, f"FFmpeg调用次数不足: {ffmpeg_call_count}"
        
        finally:
            shutil.rmtree(output_dir)
            shutil.rmtree(temp_dir)

    @patch('subprocess.run')
    def test_video_composition_with_all_mockdata_files(self, mock_run):
        """验证使用所有mockdata文件进行视频合成"""
        mock_run.return_value = MagicMock(returncode=0, stderr="")
        
        import tempfile
        import shutil
        
        output_dir = tempfile.mkdtemp()
        temp_dir = tempfile.mkdtemp()
        
        try:
            service = Stage5VideoCompositionService(
                output_dir=output_dir,
                temp_dir=temp_dir,
            )
            
            with open(STAGE4_OUTPUT, "r", encoding="utf-8") as f:
                stage4_data = json.load(f)
            
            for scene in stage4_data["scenes"]:
                image_path = Path(scene["image_path"])
                assert image_path.exists(), f"图像文件缺失: {image_path}"
                
                for segment in scene["audio_segments"]:
                    audio_path = Path(segment["audio_path"])
                    assert audio_path.exists(), f"音频文件缺失: {audio_path}"
            
            stage3_data = [
                {"scene_id": scene["scene_id"], "image_path": scene["image_path"]}
                for scene in stage4_data["scenes"]
            ]
            
            output_path = os.path.join(output_dir, "all_mockdata_test.mp4")
            with open(output_path, "wb") as f:
                f.write(b"FULL_MOCK_VIDEO")
            
            result = service.compose_video(
                stage3_data=stage3_data,
                stage4_data=stage4_data,
                video_id="all_mockdata_test",
            )
            
            assert result.video_id == "all_mockdata_test"
            assert result.scenes_count == 3
            assert result.duration == stage4_data["total_video_duration"]
        
        finally:
            shutil.rmtree(output_dir)
            shutil.rmtree(temp_dir)


class TestOutputQualityAcceptance:
    """验收测试 - 输出质量验证"""

    @patch('subprocess.run')
    def test_output_video_meets_specifications(self, mock_run):
        """验证输出视频符合规格要求"""
        mock_run.return_value = MagicMock(returncode=0, stderr="")
        
        import tempfile
        import shutil
        
        output_dir = tempfile.mkdtemp()
        temp_dir = tempfile.mkdtemp()
        
        try:
            service = Stage5VideoCompositionService(
                output_dir=output_dir,
                temp_dir=temp_dir,
            )
            
            with open(STAGE4_OUTPUT, "r", encoding="utf-8") as f:
                stage4_data = json.load(f)
            
            stage3_data = [
                {"scene_id": scene["scene_id"], "image_path": scene["image_path"]}
                for scene in stage4_data["scenes"]
            ]
            
            output_path = os.path.join(output_dir, "quality_test.mp4")
            with open(output_path, "wb") as f:
                f.write(b"QUALITY_TEST_VIDEO" * 1000)
            
            result = service.compose_video(
                stage3_data=stage3_data,
                stage4_data=stage4_data,
                video_id="quality_test",
            )
            
            assert result.format == "mp4", "视频格式应为MP4"
            assert result.resolution == "1920x1080", "分辨率应为1920x1080"
            assert result.file_size > 0, "文件大小应大于0"
            assert result.duration == 63.5, "视频时长应为63.5秒"
            
            ffmpeg_calls = [call[0][0] for call in mock_run.call_args_list]
            
            has_h264_encoding = any("libx264" in str(call) for call in ffmpeg_calls)
            assert has_h264_encoding, "应使用H.264编码"
            
            has_scale = any("scale=1920:1080" in str(call) for call in ffmpeg_calls)
            assert has_scale, "应设置1920x1080分辨率"
        
        finally:
            shutil.rmtree(output_dir)
            shutil.rmtree(temp_dir)

    @patch('subprocess.run')
    def test_ffmpeg_commands_correctness(self, mock_run):
        """验证FFmpeg命令正确性"""
        mock_run.return_value = MagicMock(returncode=0, stderr="")
        
        import tempfile
        import shutil
        
        output_dir = tempfile.mkdtemp()
        temp_dir = tempfile.mkdtemp()
        
        try:
            service = Stage5VideoCompositionService(
                output_dir=output_dir,
                temp_dir=temp_dir,
            )
            
            with open(STAGE4_OUTPUT, "r", encoding="utf-8") as f:
                stage4_data = json.load(f)
            
            stage3_data = [
                {"scene_id": scene["scene_id"], "image_path": scene["image_path"]}
                for scene in stage4_data["scenes"]
            ]
            
            output_path = os.path.join(output_dir, "ffmpeg_test.mp4")
            with open(output_path, "wb") as f:
                f.write(b"FFMPEG_TEST")
            
            result = service.compose_video(
                stage3_data=stage3_data,
                stage4_data=stage4_data,
                video_id="ffmpeg_test",
            )
            
            ffmpeg_calls = [call[0][0] for call in mock_run.call_args_list]
            
            assert len(ffmpeg_calls) > 0, "应有FFmpeg调用"
            
            all_calls_have_ffmpeg = all("ffmpeg" in str(call) for call in ffmpeg_calls)
            assert all_calls_have_ffmpeg, "所有调用应包含ffmpeg命令"
            
            has_concat = any("-f" in str(call) and "concat" in str(call) for call in ffmpeg_calls)
            assert has_concat, "应有concat操作"
            
            has_subtitle = any("subtitles=" in str(call) for call in ffmpeg_calls)
            assert has_subtitle, "应有字幕添加操作"
        
        finally:
            shutil.rmtree(output_dir)
            shutil.rmtree(temp_dir)


class TestPerformanceAcceptance:
    """验收测试 - 性能要求"""

    @patch('subprocess.run')
    def test_service_handles_multiple_scenes(self, mock_run):
        """验证服务能处理多个场景"""
        mock_run.return_value = MagicMock(returncode=0, stderr="")
        
        import tempfile
        import shutil
        
        output_dir = tempfile.mkdtemp()
        temp_dir = tempfile.mkdtemp()
        
        try:
            service = Stage5VideoCompositionService(
                output_dir=output_dir,
                temp_dir=temp_dir,
            )
            
            with open(STAGE4_OUTPUT, "r", encoding="utf-8") as f:
                stage4_data = json.load(f)
            
            assert len(stage4_data["scenes"]) == 3, "应有3个场景"
            
            stage3_data = [
                {"scene_id": scene["scene_id"], "image_path": scene["image_path"]}
                for scene in stage4_data["scenes"]
            ]
            
            output_path = os.path.join(output_dir, "multi_scene_test.mp4")
            with open(output_path, "wb") as f:
                f.write(b"MULTI_SCENE")
            
            result = service.compose_video(
                stage3_data=stage3_data,
                stage4_data=stage4_data,
                video_id="multi_scene_test",
            )
            
            assert result.scenes_count == 3, "输出应包含3个场景"
            
        finally:
            shutil.rmtree(output_dir)
            shutil.rmtree(temp_dir)

    @patch('subprocess.run')
    def test_temp_files_creation(self, mock_run):
        """验证临时文件创建"""
        mock_run.return_value = MagicMock(returncode=0, stderr="")
        
        import tempfile
        import shutil
        
        output_dir = tempfile.mkdtemp()
        temp_dir = tempfile.mkdtemp()
        
        try:
            service = Stage5VideoCompositionService(
                output_dir=output_dir,
                temp_dir=temp_dir,
            )
            
            assert os.path.exists(output_dir), "输出目录应存在"
            assert os.path.exists(temp_dir), "临时目录应存在"
            
            with open(STAGE4_OUTPUT, "r", encoding="utf-8") as f:
                stage4_data = json.load(f)
            
            subtitle_path = os.path.join(temp_dir, "test_subtitle.srt")
            service._generate_subtitles(stage4_data, subtitle_path)
            
            assert os.path.exists(subtitle_path), "字幕文件应被创建"
        
        finally:
            shutil.rmtree(output_dir)
            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
