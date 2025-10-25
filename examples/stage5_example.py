#!/usr/bin/env python3
import json
from pathlib import Path
from app.services.stage5_video_composition import Stage5VideoCompositionService


def main():
    print("=" * 60)
    print("Stage5 Video Composition Service Example")
    print("=" * 60)
    
    stage3_output_path = Path("tests/backend/stage4/mockdata/stage3_output.json")
    stage4_output_path = Path("tests/backend/stage4/mockdata/stage4_expected_output.json")
    
    if not stage3_output_path.exists():
        print(f"Error: Stage3 output file not found at {stage3_output_path}")
        return
    
    if not stage4_output_path.exists():
        print(f"Error: Stage4 output file not found at {stage4_output_path}")
        return
    
    with open(stage3_output_path, "r", encoding="utf-8") as f:
        stage3_data = json.load(f)
    
    with open(stage4_output_path, "r", encoding="utf-8") as f:
        stage4_data = json.load(f)
    
    print(f"\nLoaded Stage3 output: {len(stage3_data)} scenes")
    print(f"Loaded Stage4 output: {stage4_data['total_video_duration']:.2f}s total duration")
    
    service = Stage5VideoCompositionService(
        output_dir="./output/videos",
        temp_dir="./output/temp"
    )
    
    print("\n" + "=" * 60)
    print("Note: This example requires FFmpeg to be installed")
    print("and actual image/audio files to be present.")
    print("=" * 60)
    
    print("\nThe service would perform the following steps:")
    print("1. Create individual scene videos from images")
    print("2. Merge audio segments into a single audio track")
    print("3. Generate SRT subtitle file")
    print("4. Combine video, audio, and subtitles")
    
    print("\nExpected output:")
    print(f"  Video ID: video_example_001")
    print(f"  Duration: {stage4_data['total_video_duration']:.2f}s")
    print(f"  Resolution: 1920x1080")
    print(f"  Format: MP4")
    print(f"  Scenes: {len(stage4_data['scenes'])}")
    
    print("\n" + "=" * 60)
    print("Stage5 example structure demonstrated!")
    print("=" * 60)


if __name__ == "__main__":
    main()
