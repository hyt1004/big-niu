import os
import subprocess
import tempfile
from typing import List, Optional, Dict
from pathlib import Path
import httpx
from app.models.schemas import Stage1Output, Stage3Output


class TTSService:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.base_url = "https://openrouter.ai/api/v1"
    
    async def generate_audio(
        self,
        text: str,
        output_path: str,
        voice: str = "alloy",
        model: str = "openai/tts-1"
    ) -> Dict[str, float]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/hyt1004/big-niu",
            "X-Title": "Big Niu Text-to-Video",
        }
        
        payload = {
            "model": model,
            "input": text,
            "voice": voice,
        }
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.base_url}/audio/speech",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            
            audio_data = response.content
            
            with open(output_path, "wb") as f:
                f.write(audio_data)
            
            duration = self._get_audio_duration(output_path)
            
            return {
                "audio_path": output_path,
                "duration": duration
            }
    
    def _get_audio_duration(self, audio_path: str) -> float:
        try:
            result = subprocess.run(
                [
                    "ffprobe",
                    "-v", "error",
                    "-show_entries", "format=duration",
                    "-of", "default=noprint_wrappers=1:nokey=1",
                    audio_path
                ],
                capture_output=True,
                text=True,
                check=True
            )
            return float(result.stdout.strip())
        except (subprocess.CalledProcessError, ValueError):
            return 3.0


class VideoCompositionService:
    def __init__(
        self,
        output_dir: str = "./output",
        tts_service: Optional[TTSService] = None
    ):
        self.output_dir = output_dir
        self.audio_dir = os.path.join(output_dir, "audio")
        self.video_dir = os.path.join(output_dir, "videos")
        self.tts_service = tts_service or TTSService()
        
        os.makedirs(self.audio_dir, exist_ok=True)
        os.makedirs(self.video_dir, exist_ok=True)
    
    async def generate_scene_audio(
        self,
        scene_id: str,
        narration: str,
        dialogues: List[Dict]
    ) -> Dict:
        audio_segments = []
        total_duration = 0.0
        
        if narration:
            narration_path = os.path.join(
                self.audio_dir,
                f"{scene_id}_narration.mp3"
            )
            narration_result = await self.tts_service.generate_audio(
                text=narration,
                output_path=narration_path,
                voice="onyx"
            )
            audio_segments.append({
                "type": "narration",
                "path": narration_path,
                "duration": narration_result["duration"]
            })
            total_duration += narration_result["duration"]
        
        for idx, dialogue in enumerate(dialogues):
            dialogue_path = os.path.join(
                self.audio_dir,
                f"{scene_id}_dialogue_{idx}.mp3"
            )
            dialogue_result = await self.tts_service.generate_audio(
                text=dialogue["text"],
                output_path=dialogue_path,
                voice="nova"
            )
            audio_segments.append({
                "type": "dialogue",
                "character": dialogue.get("character"),
                "path": dialogue_path,
                "duration": dialogue_result["duration"]
            })
            total_duration += dialogue_result["duration"]
        
        if audio_segments:
            merged_path = os.path.join(
                self.audio_dir,
                f"{scene_id}_merged.mp3"
            )
            self._merge_audio_files(
                [seg["path"] for seg in audio_segments],
                merged_path
            )
            
            return {
                "scene_id": scene_id,
                "audio_path": merged_path,
                "duration": total_duration,
                "segments": audio_segments
            }
        
        return {
            "scene_id": scene_id,
            "audio_path": None,
            "duration": 0.0,
            "segments": []
        }
    
    def _merge_audio_files(self, audio_files: List[str], output_path: str):
        if len(audio_files) == 1:
            import shutil
            shutil.copy(audio_files[0], output_path)
            return
        
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.txt',
            delete=False
        ) as f:
            for audio_file in audio_files:
                f.write(f"file '{os.path.abspath(audio_file)}'\n")
            concat_file = f.name
        
        try:
            subprocess.run(
                [
                    "ffmpeg",
                    "-f", "concat",
                    "-safe", "0",
                    "-i", concat_file,
                    "-c", "copy",
                    "-y",
                    output_path
                ],
                check=True,
                capture_output=True
            )
        finally:
            os.unlink(concat_file)
    
    async def compose_video(
        self,
        stage1_output: Stage1Output,
        stage3_outputs: List[Stage3Output],
        output_filename: str = "final_video.mp4"
    ) -> Dict:
        scene_audio_data = []
        
        for scene in stage1_output.scenes:
            audio_data = await self.generate_scene_audio(
                scene_id=scene.scene_id,
                narration=scene.narration,
                dialogues=[d.dict() for d in scene.dialogues]
            )
            scene_audio_data.append(audio_data)
        
        scene_map = {s.scene_id: s for s in stage3_outputs}
        
        video_inputs = []
        for audio_data in scene_audio_data:
            scene_id = audio_data["scene_id"]
            if scene_id in scene_map:
                stage3 = scene_map[scene_id]
                video_inputs.append({
                    "image_path": stage3.image_path,
                    "duration": audio_data["duration"]
                })
        
        final_audio_path = os.path.join(
            self.audio_dir,
            "final_merged_audio.mp3"
        )
        self._merge_audio_files(
            [a["audio_path"] for a in scene_audio_data if a["audio_path"]],
            final_audio_path
        )
        
        output_path = os.path.join(self.video_dir, output_filename)
        self._create_video_with_ffmpeg(
            video_inputs,
            final_audio_path,
            output_path
        )
        
        return {
            "video_path": output_path,
            "total_duration": sum(v["duration"] for v in video_inputs),
            "scenes_count": len(video_inputs)
        }
    
    def _create_video_with_ffmpeg(
        self,
        video_inputs: List[Dict],
        audio_path: str,
        output_path: str
    ):
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.txt',
            delete=False
        ) as f:
            for video_input in video_inputs:
                f.write(f"file '{os.path.abspath(video_input['image_path'])}'\n")
                f.write(f"duration {video_input['duration']}\n")
            
            if video_inputs:
                f.write(f"file '{os.path.abspath(video_inputs[-1]['image_path'])}'\n")
            
            concat_file = f.name
        
        try:
            cmd = [
                "ffmpeg",
                "-f", "concat",
                "-safe", "0",
                "-i", concat_file,
                "-i", audio_path,
                "-c:v", "libx264",
                "-tune", "stillimage",
                "-c:a", "aac",
                "-b:a", "192k",
                "-pix_fmt", "yuv420p",
                "-shortest",
                "-y",
                output_path
            ]
            
            subprocess.run(
                cmd,
                check=True,
                capture_output=True
            )
        finally:
            os.unlink(concat_file)
