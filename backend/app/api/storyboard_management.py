import json
from pathlib import Path
from fastapi import APIRouter, HTTPException
from .schemas import StoryboardTable, StoryboardResponse
from .client_session import session_manager

router = APIRouter(prefix="/storyboard", tags=["分镜表管理"])


def get_storyboard_file(client_id: str) -> Path:
    return Path(f"configs/clients/{client_id}/storyboard.json")


def get_example_storyboards() -> list:
    return [
        {
            "name": "动作场景示例",
            "description": "快节奏的动作场景分镜表",
            "data": {
                "rows": 2,
                "columns": 3,
                "cells": [
                    {
                        "shot_number": 1,
                        "scene_image": "/api/v1/bigniu/images/test/action_1.png",
                        "scene_description": "主角快速奔跑",
                        "dialogue": "必须赶在他们之前到达！",
                        "main_character": "主角",
                        "shooting_distance": 0.5,
                        "dynamic_intensity": 0.9,
                        "scene_atmosphere": 0.8
                    },
                    {
                        "shot_number": 2,
                        "scene_image": "/api/v1/bigniu/images/test/action_2.png",
                        "scene_description": "敌人追击场景",
                        "dialogue": "别让他跑了！",
                        "main_character": "敌人",
                        "shooting_distance": 0.6,
                        "dynamic_intensity": 0.85,
                        "scene_atmosphere": 0.7
                    }
                ]
            }
        },
        {
            "name": "情感场景示例",
            "description": "温馨的情感交流场景",
            "data": {
                "rows": 1,
                "columns": 2,
                "cells": [
                    {
                        "shot_number": 1,
                        "scene_image": "/api/v1/bigniu/images/test/emotion_1.png",
                        "scene_description": "两人深情对望",
                        "dialogue": "谢谢你一直陪伴着我",
                        "main_character": "主角",
                        "shooting_distance": 0.3,
                        "dynamic_intensity": 0.2,
                        "scene_atmosphere": 0.9
                    }
                ]
            }
        }
    ]


@router.get("/{client_id}", response_model=StoryboardResponse)
async def get_storyboard(client_id: str):
    if not session_manager.is_client_online(client_id):
        raise HTTPException(status_code=410, detail="客户端已离线")
    
    storyboard_file = get_storyboard_file(client_id)
    
    if not storyboard_file.exists():
        return StoryboardResponse(
            success=True,
            message="分镜表未生成",
            data=None
        )
    
    try:
        with open(storyboard_file, 'r', encoding='utf-8') as f:
            storyboard_data = json.load(f)
        
        return StoryboardResponse(
            success=True,
            message="获取分镜表成功",
            data=storyboard_data
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取分镜表失败: {str(e)}")


@router.post("/{client_id}", response_model=StoryboardResponse)
async def save_storyboard(client_id: str, storyboard: StoryboardTable):
    if not session_manager.is_client_online(client_id):
        raise HTTPException(status_code=410, detail="客户端已离线")
    
    storyboard_file = get_storyboard_file(client_id)
    storyboard_file.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        storyboard_dict = storyboard.model_dump()
        
        with open(storyboard_file, 'w', encoding='utf-8') as f:
            json.dump(storyboard_dict, f, indent=2, ensure_ascii=False)
        
        return StoryboardResponse(
            success=True,
            message="分镜表保存成功",
            data=storyboard_dict
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存分镜表失败: {str(e)}")


@router.get("/examples", response_model=dict)
async def get_storyboard_examples():
    return {
        "success": True,
        "message": "获取示例成功",
        "examples": get_example_storyboards()
    }
