import json
from pathlib import Path
from fastapi import APIRouter, HTTPException
from .schemas import StoryboardTable, StoryboardResponse
from .client_session import session_manager
import asyncio

router = APIRouter(prefix="/storyboard", tags=["分镜表管理"])


def get_storyboard_file(client_id: str) -> Path:
    return Path(f"configs/clients/{client_id}/storyboard.json")


async def trigger_video_generation(client_id: str):
    """异步触发视频生成"""
    try:
        from .video_management import generate_video
        from .schemas import VideoGenerationRequest
        
        request = VideoGenerationRequest(storyboard_enabled=True)
        await generate_video(client_id, request)
        
        print(f"Video generation triggered for client {client_id}")
    except Exception as e:
        print(f"Failed to trigger video generation for client {client_id}: {e}")


def get_example_storyboards() -> list:
    """从test_data目录获取分镜表示例数据"""
    test_data_dir = Path("test_data/storyboards")
    
    if not test_data_dir.exists():
        return []
    
    examples = []
    for i, storyboard_file in enumerate(sorted(test_data_dir.glob("*.json")), 1):
        try:
            with open(storyboard_file, 'r', encoding='utf-8') as f:
                storyboard_data = json.load(f)
            
            # 将相对路径转换为绝对路径
            for cell in storyboard_data.get("cells", []):
                if cell.get("scene_image") and cell["scene_image"].startswith("/api/"):
                    cell["scene_image"] = f"http://localhost:8000{cell['scene_image']}"
            
            examples.append({
                "name": f"分镜表示例 {i}",
                "description": f"来自 {storyboard_file.name} 的分镜表数据",
                "data": storyboard_data
            })
        except Exception as e:
            print(f"Error loading {storyboard_file}: {e}")
            continue
    
    return examples


@router.get("/examples", response_model=dict)
async def get_storyboard_examples():
    return {
        "success": True,
        "message": "获取示例成功",
        "examples": get_example_storyboards()
    }


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
        
        # 异步触发视频生成
        asyncio.create_task(trigger_video_generation(client_id))
        
        return StoryboardResponse(
            success=True,
            message="分镜表保存成功,视频生成已开始",
            data=storyboard_dict
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存分镜表失败: {str(e)}")
