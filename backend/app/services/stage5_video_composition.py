import os
import subprocess
from typing import List, Optional
from pathlib import Path


class SubtitleEntry:
    def __init__(
        self,
        index: int,
        start_time: float,
        end_time: float,
        text: str,
    ):
        self.index = index
        self.start_time = start_time
        self.end_time = end_time
        self.text = text

    def to_srt_format(self) -> str:
        def format_timestamp(seconds: float) -> str:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            millis = int((seconds % 1) * 1000)
            return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
        
        start_str = format_timestamp(self.start_time)
        end_str = format_timestamp(self.end_time)
        
        return f"{self.index}\n{start_str} --> {end_str}\n{self.text}\n"


class Stage5Output:
    def __init__(
        self,
        video_id: str,
        video_path: str,
        video_url: Optional[str],
        duration: float,
        resolution: str,
        file_size: int,
        format: str,
        scenes_count: int,
    ):
        self.video_id = video_id
        self.video_path = video_path
        self.video_url = video_url
        self.duration = duration
        self.resolution = resolution
        self.file_size = file_size
        self.format = format
        self.scenes_count = scenes_count

    def to_dict(self) -> dict:
        return {
            "video_id": self.video_id,
            "video_path": self.video_path,
            "video_url": self.video_url,
            "duration": self.duration,
            "resolution": self.resolution,
            "file_size": self.file_size,
            "format": self.format,
            "scenes_count": self.scenes_count,
        }


class Stage5VideoCompositionService:
    def __init__(
        self,
        output_dir: str = "./output/videos",
        temp_dir: str = "./output/temp",
    ):
        self.output_dir = output_dir
        self.temp_dir = temp_dir
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)

    def _generate_subtitles(
        self,
        stage4_data: dict,
        output_path: str,
    ) -> str:
        subtitle_entries = []
        subtitle_index = 1
        
        # 生成字幕文件
        screen_start_time = 0.0
        for idx, scene in enumerate(stage4_data["scenes"]):
            if idx > 0:
                screen_start_time += stage4_data["scenes"][idx - 1]["total_duration"]
            for segment in enumerate(scene["audio_segments"]):
                start_time = screen_start_time + segment["start_time"]
                end_time = start_time + segment["duration"]
                text = segment["text"]
                
                entry = SubtitleEntry(
                    index=subtitle_index,
                    start_time=start_time,
                    end_time=end_time,
                    text=text,
                )
                subtitle_entries.append(entry)
                subtitle_index += 1
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            for entry in subtitle_entries:
                f.write(entry.to_srt_format())
                f.write("\n")
        
        return output_path

    def _create_scene_video(
        self,
        image_path: str,
        duration: float,
        output_path: str,
    ) -> str:
        cmd = [
            "ffmpeg",
            "-y",
            "-loop", "1",
            "-t", str(duration),
            "-i", image_path,
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-vf", "scale=1920:1080",
            output_path,
        ]
        
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        
        if result.returncode != 0:
            raise ValueError(f"FFmpeg failed: {result.stderr}")
        
        return output_path

    def _merge_audio_segments(
        self,
        audio_paths: List[str],
        output_path: str,
    ) -> str:
        concat_list_path = os.path.join(self.temp_dir, "audio_concat_list.txt")
        
        with open(concat_list_path, "w", encoding="utf-8") as f:
            for audio_path in audio_paths:
                abs_path = os.path.abspath(audio_path)
                f.write(f"file '{abs_path}'\n")
        
        cmd = [
            "ffmpeg",
            "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", concat_list_path,
            "-c", "copy",
            output_path,
        ]
        
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        
        if result.returncode != 0:
            raise ValueError(f"Audio merge failed: {result.stderr}")
        
        return output_path

    def _merge_videos(
        self,
        video_paths: List[str],
        output_path: str,
    ) -> str:
        concat_list_path = os.path.join(self.temp_dir, "video_concat_list.txt")
        
        with open(concat_list_path, "w", encoding="utf-8") as f:
            for video_path in video_paths:
                abs_path = os.path.abspath(video_path)
                f.write(f"file '{abs_path}'\n")
        
        cmd = [
            "ffmpeg",
            "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", concat_list_path,
            "-c", "copy",
            output_path,
        ]
        
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        
        if result.returncode != 0:
            raise ValueError(f"Video merge failed: {result.stderr}")
        
        return output_path

    def _add_audio_and_subtitles(
        self,
        video_path: str,
        audio_path: str,
        subtitle_path: str,
        output_path: str,
    ) -> str:
        cmd = [
            "ffmpeg",
            "-y",
            "-i", video_path,
            "-i", audio_path,
            "-vf", f"subtitles={subtitle_path}:force_style='FontSize=24,PrimaryColour=&HFFFFFF&,OutlineColour=&H000000&,Outline=2'",
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "23",
            "-c:a", "aac",
            "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            output_path,
        ]
        
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        print(result)
        
        if result.returncode != 0:
            raise ValueError(f"Adding audio/subtitles failed: {result.stderr}")
        
        return output_path

    def compose_video(
        self,
        stage3_data: List[dict],
        stage4_data: dict,
        video_id: str,
    ) -> Stage5Output:
        scene_videos = []
        
        for idx, scene in enumerate(stage4_data["scenes"]):
            scene_id = scene["scene_id"]
            duration = scene["total_duration"]
            
            image_info = next(
                (s for s in stage3_data if s["scene_id"] == scene_id),
                None
            )
            
            if not image_info:
                raise ValueError(f"Image not found for scene {scene_id}")
            
            image_path = image_info["image_path"]
            
            scene_video_path = os.path.join(
                self.temp_dir,
                f"scene_{idx+1:03d}_video.mp4"
            )
            
            self._create_scene_video(
                image_path=image_path,
                duration=duration,
                output_path=scene_video_path,
            )
            
            scene_videos.append(scene_video_path)
        
        merged_video_path = os.path.join(self.temp_dir, f"{video_id}_no_audio.mp4")
        self._merge_videos(scene_videos, merged_video_path)
        
        audio_paths = []
        for scene in stage4_data["scenes"]:
            for segment in scene["audio_segments"]:
                audio_paths.append(segment["audio_path"])
        
        merged_audio_path = os.path.join(self.temp_dir, f"{video_id}_audio.mp3")
        self._merge_audio_segments(audio_paths, merged_audio_path)
        
        subtitle_path = os.path.join(self.temp_dir, f"{video_id}_subtitles.srt")
        self._generate_subtitles(stage4_data, subtitle_path)
        
        final_video_path = os.path.join(self.output_dir, f"{video_id}.mp4")
        self._add_audio_and_subtitles(
            video_path=merged_video_path,
            audio_path=merged_audio_path,
            subtitle_path=subtitle_path,
            output_path=final_video_path,
        )
        
        file_size = os.path.getsize(final_video_path)
        
        return Stage5Output(
            video_id=video_id,
            video_path=final_video_path,
            video_url=None,
            duration=stage4_data["total_video_duration"],
            resolution="1920x1080",
            file_size=file_size,
            format="mp4",
            scenes_count=len(stage4_data["scenes"]),
        )

    def compose_video_simple(
        self,
        image_paths: List[str],
        audio_paths: List[str],
        durations: List[float],
        subtitle_texts: List[tuple],
        video_id: str,
    ) -> Stage5Output:
        if len(image_paths) != len(durations):
            raise ValueError("Image paths and durations must have the same length")
        
        scene_videos = []
        for idx, (image_path, duration) in enumerate(zip(image_paths, durations)):
            scene_video_path = os.path.join(
                self.temp_dir,
                f"scene_{idx+1:03d}_video.mp4"
            )
            
            self._create_scene_video(
                image_path=image_path,
                duration=duration,
                output_path=scene_video_path,
            )
            
            scene_videos.append(scene_video_path)
        
        merged_video_path = os.path.join(self.temp_dir, f"{video_id}_no_audio.mp4")
        self._merge_videos(scene_videos, merged_video_path)
        
        merged_audio_path = os.path.join(self.temp_dir, f"{video_id}_audio.mp3")
        self._merge_audio_segments(audio_paths, merged_audio_path)
        
        subtitle_path = os.path.join(self.temp_dir, f"{video_id}_subtitles.srt")
        with open(subtitle_path, "w", encoding="utf-8") as f:
            for idx, (start, end, text) in enumerate(subtitle_texts, 1):
                entry = SubtitleEntry(idx, start, end, text)
                f.write(entry.to_srt_format())
                f.write("\n")
        
        final_video_path = os.path.join(self.output_dir, f"{video_id}.mp4")
        self._add_audio_and_subtitles(
            video_path=merged_video_path,
            audio_path=merged_audio_path,
            subtitle_path=subtitle_path,
            output_path=final_video_path,
        )
        
        file_size = os.path.getsize(final_video_path)
        total_duration = sum(durations)
        
        return Stage5Output(
            video_id=video_id,
            video_path=final_video_path,
            video_url=None,
            duration=total_duration,
            resolution="1920x1080",
            file_size=file_size,
            format="mp4",
            scenes_count=len(image_paths),
        )
