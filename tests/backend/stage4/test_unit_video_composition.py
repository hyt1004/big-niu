import pytest
from unittest.mock import Mock, patch, MagicMock, AsyncMock, mock_open
import os
import tempfile
from pathlib import Path
from backend.app.services.stage4_video_composition import TTSService, VideoCompositionService
from backend.app.models.schemas import Stage1Output, Stage3Output, Scene, Dialogue, Character, Metadata


class TestTTSService:
    
    @pytest.fixture
    def tts_service(self):
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test_api_key"}):
            return TTSService()
    
    @pytest.fixture
    def sample_text(self):
        return "这是一段测试文本，用于生成音频。"
    
    @pytest.mark.asyncio
    async def test_generate_audio_success(self, tts_service, sample_text, tmp_path):
        output_path = str(tmp_path / "test_audio.mp3")
        mock_audio_data = b"fake_audio_content"
        
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.content = mock_audio_data
            mock_response.raise_for_status = MagicMock()
            
            mock_context = MagicMock()
            mock_context.__aenter__ = AsyncMock(return_value=mock_context)
            mock_context.__aexit__ = AsyncMock(return_value=None)
            mock_context.post = AsyncMock(return_value=mock_response)
            mock_client.return_value = mock_context
            
            with patch.object(tts_service, "_get_audio_duration", return_value=3.5):
                result = await tts_service.generate_audio(sample_text, output_path)
                
                assert "audio_path" in result
                assert "duration" in result
                assert result["audio_path"] == output_path
                assert result["duration"] == 3.5
                assert os.path.exists(output_path)
                
                with open(output_path, "rb") as f:
                    assert f.read() == mock_audio_data
    
    @pytest.mark.asyncio
    async def test_generate_audio_with_custom_voice(self, tts_service, sample_text, tmp_path):
        output_path = str(tmp_path / "test_audio.mp3")
        mock_audio_data = b"fake_audio_content"
        
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.content = mock_audio_data
            mock_response.raise_for_status = MagicMock()
            
            mock_context = MagicMock()
            mock_context.__aenter__ = AsyncMock(return_value=mock_context)
            mock_context.__aexit__ = AsyncMock(return_value=None)
            mock_context.post = AsyncMock(return_value=mock_response)
            mock_client.return_value = mock_context
            
            with patch.object(tts_service, "_get_audio_duration", return_value=2.0):
                result = await tts_service.generate_audio(
                    sample_text,
                    output_path,
                    voice="nova"
                )
                
                assert result["duration"] == 2.0
                mock_context.post.assert_called_once()
                call_args = mock_context.post.call_args
                assert call_args[1]["json"]["voice"] == "nova"
    
    @pytest.mark.asyncio
    async def test_generate_audio_api_error(self, tts_service, sample_text, tmp_path):
        output_path = str(tmp_path / "test_audio.mp3")
        
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.raise_for_status = MagicMock(
                side_effect=Exception("API Error")
            )
            
            mock_context = MagicMock()
            mock_context.__aenter__ = AsyncMock(return_value=mock_context)
            mock_context.__aexit__ = AsyncMock(return_value=None)
            mock_context.post = AsyncMock(return_value=mock_response)
            mock_client.return_value = mock_context
            
            with pytest.raises(Exception):
                await tts_service.generate_audio(sample_text, output_path)
    
    def test_get_audio_duration_success(self, tts_service, tmp_path):
        audio_path = str(tmp_path / "test.mp3")
        Path(audio_path).touch()
        
        with patch("subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.stdout = "5.234\n"
            mock_run.return_value = mock_result
            
            duration = tts_service._get_audio_duration(audio_path)
            
            assert duration == 5.234
            mock_run.assert_called_once()
            assert "ffprobe" in mock_run.call_args[0][0]
    
    def test_get_audio_duration_failure(self, tts_service):
        with patch("subprocess.run", side_effect=Exception("ffprobe error")):
            duration = tts_service._get_audio_duration("/nonexistent/file.mp3")
            assert duration == 3.0


class TestVideoCompositionService:
    
    @pytest.fixture
    def mock_tts_service(self):
        mock = MagicMock(spec=TTSService)
        mock.generate_audio = AsyncMock(return_value={
            "audio_path": "/tmp/test_audio.mp3",
            "duration": 3.0
        })
        return mock
    
    @pytest.fixture
    def video_service(self, mock_tts_service, tmp_path):
        output_dir = str(tmp_path / "output")
        return VideoCompositionService(output_dir=output_dir, tts_service=mock_tts_service)
    
    @pytest.fixture
    def sample_scene_data(self):
        return {
            "scene_id": "scene_001",
            "narration": "这是一个测试场景的旁白。",
            "dialogues": [
                {"character": "char_001", "text": "你好，这是第一句对话。"},
                {"character": "char_002", "text": "很高兴见到你。"}
            ]
        }
    
    @pytest.mark.asyncio
    async def test_generate_scene_audio_with_narration_and_dialogues(
        self, video_service, sample_scene_data
    ):
        with patch.object(video_service, "_merge_audio_files") as mock_merge:
            result = await video_service.generate_scene_audio(
                scene_id=sample_scene_data["scene_id"],
                narration=sample_scene_data["narration"],
                dialogues=sample_scene_data["dialogues"]
            )
            
            assert result["scene_id"] == "scene_001"
            assert result["duration"] == 9.0
            assert len(result["segments"]) == 3
            
            assert result["segments"][0]["type"] == "narration"
            assert result["segments"][0]["start_time"] == 0.0
            assert result["segments"][1]["type"] == "dialogue"
            assert result["segments"][1]["start_time"] == 3.0
            assert result["segments"][2]["type"] == "dialogue"
            assert result["segments"][2]["start_time"] == 6.0
            
            mock_merge.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_scene_audio_no_narration(self, video_service):
        with patch.object(video_service, "_merge_audio_files") as mock_merge:
            result = await video_service.generate_scene_audio(
                scene_id="scene_002",
                narration="",
                dialogues=[{"character": "char_001", "text": "只有对话"}]
            )
            
            assert result["duration"] == 3.0
            assert len(result["segments"]) == 1
            assert result["segments"][0]["type"] == "dialogue"
            mock_merge.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_scene_audio_empty(self, video_service):
        result = await video_service.generate_scene_audio(
            scene_id="scene_003",
            narration="",
            dialogues=[]
        )
        
        assert result["scene_id"] == "scene_003"
        assert result["audio_path"] is None
        assert result["duration"] == 0.0
        assert len(result["segments"]) == 0
    
    def test_merge_audio_files_single_file(self, video_service, tmp_path):
        input_file = str(tmp_path / "input.mp3")
        output_file = str(tmp_path / "output.mp3")
        Path(input_file).write_text("test content")
        
        video_service._merge_audio_files([input_file], output_file)
        
        assert os.path.exists(output_file)
        assert Path(output_file).read_text() == "test content"
    
    def test_merge_audio_files_multiple_files(self, video_service, tmp_path):
        input_files = [
            str(tmp_path / "input1.mp3"),
            str(tmp_path / "input2.mp3"),
            str(tmp_path / "input3.mp3")
        ]
        
        for f in input_files:
            Path(f).touch()
        
        output_file = str(tmp_path / "merged.mp3")
        
        with patch("subprocess.run") as mock_run:
            video_service._merge_audio_files(input_files, output_file)
            
            mock_run.assert_called_once()
            call_args = mock_run.call_args[0][0]
            assert "ffmpeg" in call_args
            assert "-f" in call_args
            assert "concat" in call_args
    
    def test_create_video_with_ffmpeg_without_subtitles(self, video_service, tmp_path):
        video_inputs = [
            {"image_path": str(tmp_path / "img1.png"), "duration": 3.0},
            {"image_path": str(tmp_path / "img2.png"), "duration": 2.5}
        ]
        
        for inp in video_inputs:
            Path(inp["image_path"]).touch()
        
        audio_path = str(tmp_path / "audio.mp3")
        Path(audio_path).touch()
        
        output_path = str(tmp_path / "output.mp4")
        
        with patch("subprocess.run") as mock_run:
            video_service._create_video_with_ffmpeg(
                video_inputs, audio_path, output_path, None
            )
            
            mock_run.assert_called_once()
            call_args = mock_run.call_args[0][0]
            assert "ffmpeg" in call_args
            assert "-c:v" in call_args
            assert "libx264" in call_args
            assert "-c:a" in call_args
            assert "aac" in call_args
            assert "subtitles" not in " ".join(call_args)
    
    def test_create_video_with_ffmpeg_with_subtitles(self, video_service, tmp_path):
        video_inputs = [
            {"image_path": str(tmp_path / "img1.png"), "duration": 3.0}
        ]
        Path(video_inputs[0]["image_path"]).touch()
        
        audio_path = str(tmp_path / "audio.mp3")
        Path(audio_path).touch()
        
        subtitle_path = str(tmp_path / "subtitles.srt")
        Path(subtitle_path).write_text("1\n00:00:00,000 --> 00:00:03,000\nTest subtitle\n")
        
        output_path = str(tmp_path / "output.mp4")
        
        with patch("subprocess.run") as mock_run:
            video_service._create_video_with_ffmpeg(
                video_inputs, audio_path, output_path, subtitle_path
            )
            
            mock_run.assert_called_once()
            call_args = mock_run.call_args[0][0]
            assert any("subtitles" in str(arg) for arg in call_args)
    
    def test_format_srt_timestamp(self, video_service):
        assert video_service._format_srt_timestamp(0.0) == "00:00:00,000"
        assert video_service._format_srt_timestamp(1.5) == "00:00:01,500"
        assert video_service._format_srt_timestamp(65.234) == "00:01:05,234"
        assert video_service._format_srt_timestamp(3661.5) == "01:01:01,500"
    
    def test_generate_subtitle_file(self, video_service, tmp_path):
        scene_audio_data = [
            {
                "scene_id": "scene_001",
                "segments": [
                    {
                        "text": "第一句字幕",
                        "duration": 3.0
                    },
                    {
                        "text": "第二句字幕",
                        "duration": 2.5
                    }
                ]
            }
        ]
        
        output_path = str(tmp_path / "subtitles.srt")
        result_path = video_service.generate_subtitle_file(scene_audio_data, output_path)
        
        assert result_path == output_path
        assert os.path.exists(output_path)
        
        with open(output_path, "r", encoding="utf-8") as f:
            content = f.read()
            assert "1" in content
            assert "00:00:00,000 --> 00:00:03,000" in content
            assert "第一句字幕" in content
            assert "2" in content
            assert "00:00:03,000 --> 00:00:05,500" in content
            assert "第二句字幕" in content
    
    @pytest.mark.asyncio
    async def test_compose_video_integration(self, video_service, tmp_path):
        stage1_output = Stage1Output(
            metadata=Metadata(
                total_scenes=2,
                story_title="测试故事",
                total_characters=1
            ),
            characters=[
                Character(
                    id="char_001",
                    name="测试角色",
                    description="测试描述"
                )
            ],
            scenes=[
                Scene(
                    scene_id="scene_001",
                    order=1,
                    description="第一个场景",
                    composition="测试构图",
                    narration="这是旁白",
                    dialogues=[
                        Dialogue(character="char_001", text="你好")
                    ]
                ),
                Scene(
                    scene_id="scene_002",
                    order=2,
                    description="第二个场景",
                    composition="测试构图2",
                    narration="第二段旁白",
                    dialogues=[]
                )
            ]
        )
        
        img1 = str(tmp_path / "scene_001.png")
        img2 = str(tmp_path / "scene_002.png")
        Path(img1).touch()
        Path(img2).touch()
        
        stage3_outputs = [
            Stage3Output(
                scene_id="scene_001",
                image_path=img1,
                width=1024,
                height=768
            ),
            Stage3Output(
                scene_id="scene_002",
                image_path=img2,
                width=1024,
                height=768
            )
        ]
        
        with patch.object(video_service, "_merge_audio_files"):
            with patch.object(video_service, "_create_video_with_ffmpeg"):
                result = await video_service.compose_video(
                    stage1_output,
                    stage3_outputs,
                    "test_output.mp4"
                )
                
                assert "video_path" in result
                assert "subtitle_path" in result
                assert "total_duration" in result
                assert "scenes_count" in result
                assert result["scenes_count"] == 2
                assert result["total_duration"] == 12.0
    
    @pytest.mark.asyncio
    async def test_compose_video_without_subtitles(self, video_service, tmp_path):
        stage1_output = Stage1Output(
            metadata=Metadata(
                total_scenes=1,
                story_title="测试",
                total_characters=0
            ),
            characters=[],
            scenes=[
                Scene(
                    scene_id="scene_001",
                    order=1,
                    description="测试场景",
                    composition="测试",
                    narration="旁白",
                    dialogues=[]
                )
            ]
        )
        
        img = str(tmp_path / "scene_001.png")
        Path(img).touch()
        
        stage3_outputs = [
            Stage3Output(
                scene_id="scene_001",
                image_path=img,
                width=1024,
                height=768
            )
        ]
        
        with patch.object(video_service, "_merge_audio_files"):
            with patch.object(video_service, "_create_video_with_ffmpeg"):
                result = await video_service.compose_video(
                    stage1_output,
                    stage3_outputs,
                    "test_output.mp4",
                    include_subtitles=False
                )
                
                assert result["subtitle_path"] is None
