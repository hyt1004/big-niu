import os
import re
from typing import List, Dict, Optional
from pathlib import Path
import logging

from ..models.schemas import (
    Stage1Output,
    Scene,
    Character,
    AudioSegment,
    Stage4Output,
)
from ..config import settings

logger = logging.getLogger(__name__)


class Stage4TTSGenerationService:
    
    VOICE_MAPPING = {
        "narrator": "narrator",
        "middle_aged_male": "male_middle_aged",
        "young_male": "male_young",
        "elderly_female": "female_elderly",
        "young_female": "female_young",
        "middle_aged_female": "female_middle_aged",
        "elderly_male": "male_elderly",
    }
    
    def __init__(self, volcengine_config: Optional[Dict] = None):
        self.config = volcengine_config or {
            "access_key": settings.volcengine_access_key,
            "secret_key": settings.volcengine_secret_key,
            "region": settings.volcengine_region,
            "model": settings.volcengine_tts_model,
        }
        self.audio_output_dir = Path("tests/backend/stage4/mockdata/audio")
        self.audio_output_dir.mkdir(parents=True, exist_ok=True)
    
    def _clean_text(self, text: str) -> str:
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        return text
    
    def _estimate_duration(self, text: str, speech_rate: float = 4.0) -> float:
        chinese_chars = len([c for c in text if '\u4e00' <= c <= '\u9fff'])
        other_chars = len(text) - chinese_chars
        estimated_seconds = (chinese_chars * 0.4) + (other_chars * 0.1)
        return round(max(estimated_seconds, 0.5), 1)
    
    def _map_character_to_voice(self, character: Character) -> str:
        description = character.description.lower()
        
        if "中年" in description or "middle-aged" in description or "40s" in description:
            if "男" in description or "male" in description:
                return "male_middle_aged"
            else:
                return "female_middle_aged"
        
        if "年轻" in description or "young" in description or "20s" in description:
            if "男" in description or "male" in description:
                return "male_young"
            else:
                return "female_young"
        
        if "老年" in description or "elderly" in description or "70s" in description:
            if "女" in description or "female" in description:
                return "female_elderly"
            else:
                return "male_elderly"
        
        if "男" in description or "male" in description:
            return "male_middle_aged"
        else:
            return "female_middle_aged"
    
    def generate_narration_audio(
        self, 
        text: str, 
        scene_id: str,
        voice: str = "narrator"
    ) -> AudioSegment:
        cleaned_text = self._clean_text(text)
        duration = self._estimate_duration(cleaned_text)
        
        audio_filename = f"{scene_id}_narration.mp3"
        audio_path = str(self.audio_output_dir / audio_filename)
        
        logger.info(f"Generating narration audio for {scene_id}: {cleaned_text[:50]}...")
        
        return AudioSegment(
            type="narration",
            text=cleaned_text,
            audio_path=audio_path,
            duration=duration,
            start_time=0.0,
            voice=voice,
        )
    
    def generate_dialogue_audio(
        self,
        text: str,
        scene_id: str,
        dialogue_index: int,
        character: Character,
        emotion: Optional[str] = None,
    ) -> AudioSegment:
        cleaned_text = self._clean_text(text)
        duration = self._estimate_duration(cleaned_text)
        
        voice = self._map_character_to_voice(character)
        
        audio_filename = f"{scene_id}_dialogue_{dialogue_index:03d}.mp3"
        audio_path = str(self.audio_output_dir / audio_filename)
        
        logger.info(
            f"Generating dialogue audio for {scene_id} - {character.name}: "
            f"{cleaned_text[:50]}..."
        )
        
        return AudioSegment(
            type="dialogue",
            text=cleaned_text,
            audio_path=audio_path,
            duration=duration,
            start_time=0.0,
            voice=voice,
            character=character.id,
            character_name=character.name,
            emotion=emotion,
        )
    
    def process_scene_audio(
        self, 
        scene: Scene, 
        characters: List[Character]
    ) -> Stage4Output:
        char_map = {char.id: char for char in characters}
        audio_segments = []
        current_time = 0.0
        
        if scene.narration:
            narration_segment = self.generate_narration_audio(
                text=scene.narration,
                scene_id=scene.scene_id,
                voice="narrator"
            )
            narration_segment.start_time = current_time
            audio_segments.append(narration_segment)
            current_time += narration_segment.duration
        
        for idx, dialogue in enumerate(scene.dialogues, start=1):
            character = char_map.get(dialogue.character)
            if not character:
                logger.warning(
                    f"Character {dialogue.character} not found for scene {scene.scene_id}"
                )
                continue
            
            dialogue_segment = self.generate_dialogue_audio(
                text=dialogue.text,
                scene_id=scene.scene_id,
                dialogue_index=idx,
                character=character,
                emotion=dialogue.emotion,
            )
            dialogue_segment.start_time = current_time
            audio_segments.append(dialogue_segment)
            current_time += dialogue_segment.duration
        
        return Stage4Output(
            scene_id=scene.scene_id,
            audio_segments=audio_segments,
            total_duration=round(current_time, 1),
        )
    
    def generate_all_audio(self, stage1_output: Stage1Output) -> List[Stage4Output]:
        results = []
        
        for scene in stage1_output.scenes:
            logger.info(f"Processing audio for scene {scene.scene_id}")
            stage4_output = self.process_scene_audio(
                scene=scene,
                characters=stage1_output.characters,
            )
            results.append(stage4_output)
        
        total_duration = sum(output.total_duration for output in results)
        logger.info(
            f"Completed audio generation for {len(results)} scenes. "
            f"Total duration: {total_duration:.1f}s"
        )
        
        return results
