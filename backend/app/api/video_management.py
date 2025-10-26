import json
import time
from pathlib import Path
from datetime import datetime
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from .schemas import (
    VideoGenerationRequest,
    VideoGenerationResponse,
    VideoStatusResponse
)
from .client_session import session_manager
from .stub_func import StubFunctions

router = APIRouter(prefix="/video", tags=["视频管理"])


def get_storyboard_file(client_id: str) -> Path:
    return Path(f"configs/clients/{client_id}/storyboard.json")


def get_video_info_file(client_id: str) -> Path:
    return Path(f"configs/clients/{client_id}/video_info.json")


def get_model_config_file(client_id: str) -> Path:
    return Path(f"configs/clients/{client_id}/model_config.json")


def get_audio_video_config_file(client_id: str) -> Path:
    return Path(f"configs/clients/{client_id}/audio_video_config.json")


def get_videos_dir(client_id: str) -> Path:
    return Path(f"configs/clients/{client_id}/videos")


@router.post("/generate/{client_id}", response_model=VideoGenerationResponse)
async def generate_video(client_id: str, request: VideoGenerationRequest):
    if not session_manager.is_client_online(client_id):
        raise HTTPException(status_code=410, detail="客户端已离线")
    
    try:
        start_time = time.time()
        
        if request.storyboard_enabled:
            storyboard_file = get_storyboard_file(client_id)
            if not storyboard_file.exists():
                raise HTTPException(status_code=400, detail="分镜表未生成，请先提交小说或创建分镜表")
            
            with open(storyboard_file, 'r', encoding='utf-8') as f:
                storyboard = json.load(f)
        else:
            raise HTTPException(status_code=400, detail="必须启用分镜表才能生成视频")
        
        model_config = {}
        model_config_file = get_model_config_file(client_id)
        if model_config_file.exists():
            with open(model_config_file, 'r', encoding='utf-8') as f:
                model_config = json.load(f)
        
        audio_video_config = {}
        audio_config_file = get_audio_video_config_file(client_id)
        if audio_config_file.exists():
            with open(audio_config_file, 'r', encoding='utf-8') as f:
                audio_video_config = json.load(f)
        
        images = await StubFunctions.generate_images_from_storyboard(storyboard, client_id)
        
        dialogues = " ".join([cell.get("dialogue", "") for cell in storyboard.get("cells", [])])
        audio_filename = await StubFunctions.generate_audio_from_text(
            dialogues,
            client_id,
            audio_video_config
        )
        
        video_filename = await StubFunctions.generate_video_from_images(
            images,
            client_id,
            model_config
        )
        
        # 确定最终视频文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        final_video = f"final_video_{client_id}_{timestamp}.mp4"
        
        # 复制视频文件到最终位置
        client_videos_dir = get_videos_dir(client_id)
        source_video_path = client_videos_dir / video_filename
        final_video_path = client_videos_dir / final_video
        
        try:
            import shutil
            if source_video_path.exists():
                shutil.copy2(source_video_path, final_video_path)
                print(f"Final video created: {final_video}")
            else:
                print(f"Source video not found: {source_video_path}")
        except Exception as e:
            print(f"Error creating final video: {e}")
        
        # 调用combine_video_audio（现在只是模拟音频合并）
        await StubFunctions.combine_video_audio(
            video_filename,
            audio_filename,
            client_id
        )
        
        processing_time = time.time() - start_time
        
        video_info = {
            "video_filename": final_video,
            "images_count": len(images),
            "audio_included": True,
            "processing_time": processing_time,
            "status": "completed",
            "quality": request.quality,
            "created_at": time.time()
        }
        
        video_info_file = get_video_info_file(client_id)
        with open(video_info_file, 'w', encoding='utf-8') as f:
            json.dump(video_info, f, indent=2, ensure_ascii=False)
        
        StubFunctions.save_processing_log(
            client_id,
            "video_generation",
            "success",
            video_info
        )
        
        return VideoGenerationResponse(
            success=True,
            message="视频生成成功（功能开发中，使用测试数据）",
            status_code=0,
            video_filename=final_video,
            images_count=len(images),
            audio_included=True,
            processing_time=processing_time
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"视频生成失败: {str(e)}")


@router.get("/status/{client_id}", response_model=VideoStatusResponse)
async def get_video_status(client_id: str):
    if not session_manager.is_client_online(client_id):
        raise HTTPException(status_code=410, detail="客户端已离线")
    
    video_info_file = get_video_info_file(client_id)
    
    if not video_info_file.exists():
        return VideoStatusResponse(
            success=True,
            status="not_started",
            progress=0,
            url=None,
            video_info=None
        )
    
    try:
        with open(video_info_file, 'r', encoding='utf-8') as f:
            video_info = json.load(f)
        
        status = video_info.get("status", "unknown")
        
        video_url = None
        if status == "completed":
            video_url = f"/api/v1/bigniu/video/download/{client_id}"
        
        return VideoStatusResponse(
            success=True,
            status=status,
            progress=100 if status == "completed" else 0,
            url=video_url,
            video_info=video_info
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取视频状态失败: {str(e)}")


@router.get("/download/{client_id}")
async def download_video(client_id: str):
    if not session_manager.is_client_online(client_id):
        raise HTTPException(status_code=410, detail="客户端已离线")
    
    video_info_file = get_video_info_file(client_id)
    
    if not video_info_file.exists():
        raise HTTPException(status_code=404, detail="视频未生成")
    
    try:
        with open(video_info_file, 'r', encoding='utf-8') as f:
            video_info = json.load(f)
        
        video_filename = video_info.get("video_filename")
        if not video_filename:
            raise HTTPException(status_code=404, detail="视频文件名未找到")
        
        videos_dir = get_videos_dir(client_id)
        video_path = videos_dir / video_filename
        
        if not video_path.exists():
            raise HTTPException(status_code=404, detail="视频文件不存在")
        
        return FileResponse(
            video_path,
            media_type="video/mp4",
            filename=video_filename
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"下载视频失败: {str(e)}")
