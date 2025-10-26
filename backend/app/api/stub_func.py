import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import asyncio


class StubFunctions:
    
    @staticmethod
    async def generate_storyboard_from_text(text: str, client_id: str) -> Dict[str, Any]:
        """从test_data目录获取分镜表数据"""
        await asyncio.sleep(0.5)
        
        # 尝试从test_data目录获取分镜表数据
        test_data_dir = Path("test_data/storyboards")
        
        if test_data_dir.exists():
            # 随机选择一个示例文件
            storyboard_files = list(test_data_dir.glob("*.json"))
            if storyboard_files:
                import random
                selected_file = random.choice(storyboard_files)
                
                try:
                    with open(selected_file, 'r', encoding='utf-8') as f:
                        storyboard_data = json.load(f)
                    
                    # 将相对路径转换为绝对路径
                    for cell in storyboard_data.get("cells", []):
                        if cell.get("scene_image") and cell["scene_image"].startswith("/api/"):
                            cell["scene_image"] = f"http://localhost:8000{cell['scene_image']}"
                    
                    return {
                        "success": True,
                        "message": f"分镜表生成成功 (来自 {selected_file.name})",
                        "status_code": 0,
                        "data": storyboard_data
                    }
                except Exception as e:
                    print(f"Error loading storyboard from {selected_file}: {e}")
        
        # 如果无法从文件加载，使用默认数据
        storyboard = {
            "rows": 3,
            "columns": 6,
            "cells": [
                {
                    "shot_number": 1,
                    "scene_image": f"/api/v1/bigniu/images/test/scene_1.png",
                    "scene_description": "开场镜头：主角站在城市的高楼顶端，俯瞰整个城市的夜景",
                    "dialogue": "这座城市，终于要迎来改变了...",
                    "main_character": "主角",
                    "shooting_distance": 0.7,
                    "dynamic_intensity": 0.3,
                    "scene_atmosphere": 0.8
                },
                {
                    "shot_number": 2,
                    "scene_image": f"/api/v1/bigniu/images/test/scene_2.png",
                    "scene_description": "近景：主角的脸部特写，眼神坚定而深邃",
                    "dialogue": "为了所有人的未来，我必须前进",
                    "main_character": "主角",
                    "shooting_distance": 0.3,
                    "dynamic_intensity": 0.5,
                    "scene_atmosphere": 0.9
                },
                {
                    "shot_number": 3,
                    "scene_image": f"/api/v1/bigniu/images/test/scene_3.png",
                    "scene_description": "动作场景：主角从楼顶一跃而下，背景是璀璨的城市灯光",
                    "dialogue": "",
                    "main_character": "主角",
                    "shooting_distance": 0.5,
                    "dynamic_intensity": 0.9,
                    "scene_atmosphere": 0.7
                }
            ]
        }
        
        return {
            "success": True,
            "message": "分镜表生成成功",
            "status_code": 0,
            "data": storyboard
        }
    
    @staticmethod
    async def generate_images_from_storyboard(storyboard: Dict[str, Any], client_id: str) -> List[Dict[str, str]]:
        await asyncio.sleep(1.0)
        
        images = []
        for cell in storyboard.get("cells", []):
            images.append({
                "image_url": cell.get("scene_image", ""),
                "scene_description": cell.get("scene_description", ""),
                "shot_number": cell.get("shot_number", 0)
            })
        
        return images
    
    @staticmethod
    async def generate_audio_from_text(text: str, client_id: str, audio_config: Dict[str, Any]) -> str:
        """从test_data目录获取音频文件"""
        await asyncio.sleep(0.8)
        
        # 尝试从test_data目录获取音频文件
        test_data_dir = Path("test_data/audio")
        
        if test_data_dir.exists():
            audio_files = list(test_data_dir.glob("*.mp3"))
            if audio_files:
                # 复制测试音频到客户端目录
                client_audio_dir = Path(f"configs/clients/{client_id}/audio")
                client_audio_dir.mkdir(parents=True, exist_ok=True)
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                audio_filename = f"audio_{client_id}_{timestamp}.{audio_config.get('audio_format', 'mp3')}"
                target_path = client_audio_dir / audio_filename
                
                try:
                    import shutil
                    shutil.copy2(audio_files[0], target_path)
                    return audio_filename
                except Exception as e:
                    print(f"Error copying audio file: {e}")
        
        # 如果无法从文件获取，返回默认文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        audio_filename = f"audio_{client_id}_{timestamp}.{audio_config.get('audio_format', 'mp3')}"
        
        return audio_filename
    
    @staticmethod
    async def generate_video_from_images(
        images: List[Dict[str, str]], 
        client_id: str, 
        model_config: Dict[str, Any]
    ) -> str:
        """从test_data目录获取视频文件"""
        await asyncio.sleep(2.0)
        
        # 尝试从test_data目录获取视频文件
        test_data_dir = Path("test_data/videos")
        
        if test_data_dir.exists():
            video_files = list(test_data_dir.glob("*.mp4"))
            if video_files:
                # 复制测试视频到客户端目录
                client_videos_dir = Path(f"configs/clients/{client_id}/videos")
                client_videos_dir.mkdir(parents=True, exist_ok=True)
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                video_filename = f"video_{client_id}_{timestamp}.mp4"
                target_path = client_videos_dir / video_filename
                
                try:
                    import shutil
                    shutil.copy2(video_files[0], target_path)
                    return video_filename
                except Exception as e:
                    print(f"Error copying video file: {e}")
        
        # 如果无法从文件获取，返回默认文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        video_filename = f"video_{client_id}_{timestamp}.{model_config.get('video_format', 'mp4')}"
        
        return video_filename
    
    @staticmethod
    async def combine_video_audio(video_filename: str, audio_filename: str, client_id: str) -> str:
        await asyncio.sleep(1.5)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        final_video = f"final_video_{client_id}_{timestamp}.mp4"
        
        # 实际复制视频文件到最终位置
        client_videos_dir = Path(f"configs/clients/{client_id}/videos")
        source_video_path = client_videos_dir / video_filename
        final_video_path = client_videos_dir / final_video
        
        try:
            import shutil
            if source_video_path.exists():
                shutil.copy2(source_video_path, final_video_path)
                print(f"Combined video created: {final_video}")
            else:
                print(f"Source video not found: {source_video_path}")
        except Exception as e:
            print(f"Error creating final video: {e}")
        
        return final_video
    
    @staticmethod
    def generate_prompt_from_model_config(config: Dict[str, Any]) -> str:
        parts = []
        
        if "anime_mode" in config:
            parts.append(f"风格: {config['anime_mode']}风格")
        
        if "era" in config:
            parts.append(f"时代背景: {config['era']}")
        
        if config.get("random_fine_tune"):
            parts.append("启用随机微调")
        
        if config.get("random_composition"):
            parts.append("启用随机构图")
        
        if config.get("random_shot"):
            parts.append("启用随机镜头")
        
        if "shot_direction" in config:
            parts.append(f"拍摄方向: {config['shot_direction']}")
        
        if "atmosphere" in config:
            parts.append(f"氛围度: {config['atmosphere']}%")
        
        if "distance" in config:
            parts.append(f"距离感: {config['distance']}%")
        
        if "realism" in config:
            parts.append(f"真实感: {config['realism']}%")
        
        if "dynamic" in config:
            parts.append(f"动态感: {config['dynamic']}%")
        
        if config.get("characters"):
            characters_str = ", ".join(config["characters"])
            parts.append(f"角色: {characters_str}")
        
        return " | ".join(parts)
    
    @staticmethod
    def save_processing_log(
        client_id: str,
        operation: str,
        status: str,
        data: Any = None
    ) -> None:
        log_file = Path(f"configs/clients/{client_id}/processing_log.json")
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "status": status,
            "data": data
        }
        
        logs = []
        if log_file.exists():
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            except:
                logs = []
        
        logs.append(log_entry)
        
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)
