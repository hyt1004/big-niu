import os
import asyncio
import httpx
import requests
import base64
import json
import uuid
from typing import Optional, List, Dict
from app.config import settings
from app.models.schemas import Stage1Output, Character, Scene, Dialogue


class AudioSegment:
    def __init__(
        self,
        segment_type: str,
        text: str,
        audio_path: str,
        duration: float,
        start_time: float,
        character: Optional[str] = None,
        character_name: Optional[str] = None,
        emotion: Optional[str] = None,
        voice: Optional[str] = None,
    ):
        self.type = segment_type
        self.text = text
        self.audio_path = audio_path
        self.duration = duration
        self.start_time = start_time
        self.character = character
        self.character_name = character_name
        self.emotion = emotion
        self.voice = voice

    def to_dict(self) -> dict:
        result = {
            "type": self.type,
            "text": self.text,
            "audio_path": self.audio_path,
            "duration": self.duration,
            "start_time": self.start_time,
        }
        if self.character:
            result["character"] = self.character
        if self.character_name:
            result["character_name"] = self.character_name
        if self.emotion:
            result["emotion"] = self.emotion
        if self.voice:
            result["voice"] = self.voice
        return result


class SceneAudio:
    def __init__(
        self,
        scene_id: str,
        audio_segments: List[AudioSegment],
        total_duration: float,
    ):
        self.scene_id = scene_id
        self.audio_segments = audio_segments
        self.total_duration = total_duration

    def to_dict(self) -> dict:
        return {
            "scene_id": self.scene_id,
            "audio_segments": [seg.to_dict() for seg in self.audio_segments],
            "total_duration": self.total_duration,
        }


class Stage4Output:
    def __init__(
        self,
        scenes: List[SceneAudio],
        total_video_duration: float,
        character_voices: Dict[str, str],
    ):
        self.scenes = scenes
        self.total_video_duration = total_video_duration
        self.character_voices = character_voices

    def to_dict(self) -> dict:
        return {
            "scenes": [scene.to_dict() for scene in self.scenes],
            "total_video_duration": self.total_video_duration,
            "character_voices": self.character_voices,
        }


class Stage4TTSService:
    # 火山引擎 TTS 语音类型映射
    VOICE_MAPPING = {
        "narrator": "BV001_streaming",  # 标准女声
        "male_middle_aged": "BV700_streaming",  # 标准男声
        "male_young": "BV701_streaming",  # 年轻男声
        "female_elderly": "BV002_streaming",  # 成熟女声
        "female_young": "BV001_streaming",  # 标准女声
        "male_elderly": "BV700_streaming",  # 标准男声
    }

    def __init__(self, output_dir: str = "./output/audio"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def _estimate_duration(self, text: str) -> float:
        chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        english_words = len([w for w in text.split() if w.isascii()])
        
        chinese_duration = chinese_chars * 0.3
        english_duration = english_words * 0.35
        
        return max(1.0, chinese_duration + english_duration)

    def _assign_voice(
        self,
        character_id: Optional[str],
        characters: List[Character],
        is_narration: bool = False,
    ) -> str:
        if is_narration:
            return self.VOICE_MAPPING["narrator"]
        
        if not character_id:
            return self.VOICE_MAPPING["narrator"]
        
        character = next((c for c in characters if c.id == character_id), None)
        if not character:
            return self.VOICE_MAPPING["narrator"]
        
        name_lower = character.name.lower()
        desc_lower = character.description.lower() if character.description else ""
        
        if "老" in name_lower or "elderly" in desc_lower or "old" in desc_lower:
            if "女" in name_lower or "female" in desc_lower or "woman" in desc_lower:
                return self.VOICE_MAPPING["female_elderly"]
            return self.VOICE_MAPPING["male_elderly"]
        
        if "年轻" in desc_lower or "young" in desc_lower:
            if "女" in name_lower or "female" in desc_lower or "woman" in desc_lower:
                return self.VOICE_MAPPING["female_young"]
            return self.VOICE_MAPPING["male_young"]
        
        if "女" in name_lower or "female" in desc_lower or "woman" in desc_lower:
            return self.VOICE_MAPPING["female_young"]
        
        return self.VOICE_MAPPING["male_middle_aged"]

    def _map_emotion_to_params(self, emotion: Optional[str]) -> dict:
        if not emotion:
            return {"speed": 1.0, "pitch": 1.0, "volume": 1.0}
        
        emotion_lower = emotion.lower()
        params = {}
        
        # 语速调整
        if "angry" in emotion_lower or "anxious" in emotion_lower or "愤怒" in emotion_lower or "焦虑" in emotion_lower:
            params["speed"] = 1.1
            params["pitch"] = 1.1  # 愤怒时音调稍高
        elif "sad" in emotion_lower or "depressed" in emotion_lower or "悲伤" in emotion_lower:
            params["speed"] = 0.9
            params["pitch"] = 0.9  # 悲伤时音调稍低
        elif "excited" in emotion_lower or "happy" in emotion_lower or "兴奋" in emotion_lower:
            params["speed"] = 1.05
            params["pitch"] = 1.05  # 快乐时音调稍高
        elif "calm" in emotion_lower or "peaceful" in emotion_lower or "平静" in emotion_lower:
            params["speed"] = 0.95
            params["pitch"] = 1.0
        else:
            params["speed"] = 1.0
            params["pitch"] = 1.0
        
        # 设置默认音量
        params["volume"] = 1.0
        
        return params

    async def _generate_audio_volcengine(
        self,
        text: str,
        voice: str,
        output_path: str,
        emotion_params: dict = None,
    ) -> str:
        try:
            # 获取火山引擎 TTS API 配置
            appid = os.getenv("VOLCENGINE_APPID")
            access_token = os.getenv("VOLCENGINE_ACCESS_TOKEN")
            cluster = os.getenv("VOLCENGINE_CLUSTER", "volcano_tts")
            
            if not appid or not access_token:
                raise ValueError("VOLCENGINE_APPID and VOLCENGINE_ACCESS_TOKEN must be set")
            
            # 构建请求参数
            request_json = {
                "app": {
                    "appid": appid,
                    "token": access_token,
                    "cluster": cluster
                },
                "user": {
                    "uid": "tts_user"
                },
                "audio": {
                    "voice_type": voice,
                    "encoding": "mp3",
                    "speed_ratio": emotion_params.get("speed", 1.0) if emotion_params else 1.0,
                    "volume_ratio": emotion_params.get("volume", 1.0) if emotion_params else 1.0,
                    "pitch_ratio": emotion_params.get("pitch", 1.0) if emotion_params else 1.0,
                },
                "request": {
                    "reqid": str(uuid.uuid4()),
                    "text": text,
                    "text_type": "plain",
                    "operation": "query",
                    "with_frontend": 1,
                    "frontend_type": "unitTson"
                }
            }
            
            # 设置请求头
            headers = {
                "Authorization": f"Bearer;{access_token}",
                "Content-Type": "application/json"
            }
            
            api_url = "https://openspeech.bytedance.com/api/v1/tts"
            
        api_url = "https://openspeech.bytedance.com/api/v1/tts"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(api_url, json=request_json, headers=headers)
            response.raise_for_status()
            result = response.json()
            result = response.json()
            if "data" in result:
                # 解码 base64 音频数据
                audio_data = base64.b64decode(result["data"])
                
                # 确保输出目录存在
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                # 保存音频文件
                with open(output_path, "wb") as f:
                    f.write(audio_data)
                
                return output_path
            else:
                raise ValueError(f"Invalid response from Volcengine TTS: {result}")
                                    
        except Exception as e:
            raise ValueError(f"Failed to generate audio with Volcengine TTS: {e}")

    async def _generate_audio_mock(
        self,
        text: str,
        voice: str,
        output_path: str,
    ) -> str:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, "wb") as f:
            f.write(b"MOCK_AUDIO_DATA")
        
        return output_path

    def _process_scene(
        self,
        scene: Scene,
        characters: List[Character],
        scene_index: int,
    ) -> SceneAudio:
        audio_segments = []
        current_time = 0.0
        
        if scene.narration and scene.narration.strip():
            duration = self._estimate_duration(scene.narration)
            voice = self._assign_voice(None, characters, is_narration=True)
            audio_path = f"{self.output_dir}/scene_{scene_index:03d}_narration.mp3"
            
            segment = AudioSegment(
                segment_type="narration",
                text=scene.narration,
                audio_path=audio_path,
                duration=duration,
                start_time=current_time,
                voice=voice,
            )
            audio_segments.append(segment)
            current_time += duration
        
        for dialogue_idx, dialogue in enumerate(scene.dialogues, 1):
            duration = self._estimate_duration(dialogue.text)
            voice = self._assign_voice(dialogue.character, characters, is_narration=False)
            
            character = next((c for c in characters if c.id == dialogue.character), None)
            character_name = character.name if character else "Unknown"
            
            audio_path = f"{self.output_dir}/scene_{scene_index:03d}_dialogue_{dialogue_idx:03d}.mp3"
            
            segment = AudioSegment(
                segment_type="dialogue",
                text=dialogue.text,
                audio_path=audio_path,
                duration=duration,
                start_time=current_time,
                character=dialogue.character,
                character_name=character_name,
                emotion=dialogue.emotion,
                voice=voice,
            )
            audio_segments.append(segment)
            current_time += duration
        
        return SceneAudio(
            scene_id=scene.scene_id,
            audio_segments=audio_segments,
            total_duration=current_time,
        )

    async def generate_scene_audio(
        self,
        scene: Scene,
        characters: List[Character],
        scene_index: int,
        use_real_tts: bool = False,
    ) -> SceneAudio:
        scene_audio = self._process_scene(scene, characters, scene_index)
        
        if use_real_tts:
            for segment in scene_audio.audio_segments:
                # 获取情绪参数
                emotion_params = self._map_emotion_to_params(segment.emotion)
                
                await self._generate_audio_volcengine(
                    text=segment.text,
                    voice=segment.voice,
                    output_path=segment.audio_path,
                    emotion_params=emotion_params,
                )
        else:
            for segment in scene_audio.audio_segments:
                await self._generate_audio_mock(
                    text=segment.text,
                    voice=segment.voice,
                    output_path=segment.audio_path,
                )
        
        return scene_audio

    async def generate_all_audio(
        self,
        stage1_output: Stage1Output,
        use_real_tts: bool = False,
        concurrent: bool = True,
    ) -> Stage4Output:
        character_voices = {}
        for character in stage1_output.characters:
            voice = self._assign_voice(character.id, stage1_output.characters)
            character_voices[character.id] = voice
        character_voices["narrator"] = self.VOICE_MAPPING["narrator"]
        
        if concurrent:
            tasks = [
                self.generate_scene_audio(
                    scene=scene,
                    characters=stage1_output.characters,
                    scene_index=idx + 1,
                    use_real_tts=use_real_tts,
                )
                for idx, scene in enumerate(stage1_output.scenes)
            ]
            
            scene_audios = await asyncio.gather(*tasks, return_exceptions=True)
            
            final_scenes = []
            for i, result in enumerate(scene_audios):
                if isinstance(result, Exception):
                    raise result
                final_scenes.append(result)
        else:
            final_scenes = []
            for idx, scene in enumerate(stage1_output.scenes):
                scene_audio = await self.generate_scene_audio(
                    scene=scene,
                    characters=stage1_output.characters,
                    scene_index=idx + 1,
                    use_real_tts=use_real_tts,
                )
                final_scenes.append(scene_audio)
        
        total_duration = sum(scene.total_duration for scene in final_scenes)
        
        return Stage4Output(
            scenes=final_scenes,
            total_video_duration=total_duration,
            character_voices=character_voices,
        )
