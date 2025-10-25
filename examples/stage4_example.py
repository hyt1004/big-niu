#!/usr/bin/env python3
import asyncio
import json
from pathlib import Path
from app.services.stage4_tts import Stage4TTSService
from app.models.schemas import Stage1Output


async def main():
    print("=" * 60)
    print("Stage4 TTS Service Example")
    print("=" * 60)
    
    stage1_output_path = Path("tests/backend/stage4/mockdata/stage1_output.json")
    
    if not stage1_output_path.exists():
        print(f"Error: Stage1 output file not found at {stage1_output_path}")
        return
    
    with open(stage1_output_path, "r", encoding="utf-8") as f:
        stage1_data = json.load(f)
    
    stage1_output = Stage1Output(**stage1_data)
    
    print(f"\nLoaded Stage1 output:")
    print(f"  Story: {stage1_output.metadata.story_title}")
    print(f"  Scenes: {stage1_output.metadata.total_scenes}")
    print(f"  Characters: {stage1_output.metadata.total_characters}")
    
    service = Stage4TTSService(output_dir="./output/audio")
    
    print("\n" + "=" * 60)
    print("Generating audio (mock mode)...")
    print("=" * 60)
    
    result = await service.generate_all_audio(
        stage1_output=stage1_output,
        use_real_tts=False,
        concurrent=True,
    )
    
    print(f"\nAudio generation complete!")
    print(f"Total video duration: {result.total_video_duration:.2f} seconds")
    print(f"\nCharacter voice assignments:")
    for char_id, voice in result.character_voices.items():
        print(f"  {char_id}: {voice}")
    
    print(f"\nScene breakdown:")
    for scene in result.scenes:
        print(f"\n  {scene.scene_id}:")
        print(f"    Duration: {scene.total_duration:.2f}s")
        print(f"    Segments: {len(scene.audio_segments)}")
        for seg in scene.audio_segments:
            print(f"      - {seg.type}: {seg.text[:30]}... ({seg.duration:.2f}s)")
    
    output_path = Path("./output/stage4_output.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result.to_dict(), f, ensure_ascii=False, indent=2)
    
    print(f"\nFull output saved to: {output_path}")
    
    print("\n" + "=" * 60)
    print("Stage4 example completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
