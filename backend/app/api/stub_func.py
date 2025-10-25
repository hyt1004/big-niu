import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import asyncio


class StubFunctions:
    
    @staticmethod
    async def generate_storyboard_from_text(text: str, client_id: str) -> Dict[str, Any]:
        await asyncio.sleep(0.5)
        
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
        await asyncio.sleep(0.8)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        audio_filename = f"audio_{client_id}_{timestamp}.{audio_config.get('audio_format', 'mp3')}"
        
        return audio_filename
    
    @staticmethod
    async def generate_video_from_images(
        images: List[Dict[str, str]], 
        client_id: str, 
        model_config: Dict[str, Any]
    ) -> str:
        await asyncio.sleep(2.0)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        video_filename = f"video_{client_id}_{timestamp}.{model_config.get('video_format', 'mp4')}"
        
        return video_filename
    
    @staticmethod
    async def combine_video_audio(video_filename: str, audio_filename: str, client_id: str) -> str:
        await asyncio.sleep(1.5)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        final_video = f"final_video_{client_id}_{timestamp}.mp4"
        
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
