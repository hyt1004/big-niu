import json
from pathlib import Path
from fastapi import APIRouter, HTTPException
from .schemas import AudioVideoConfig, ConfigResponse
from .client_session import session_manager

router = APIRouter(prefix="/config/audio-video", tags=["音视频配置"])


def get_default_audio_video_config() -> dict:
    return {
        "audio_format": "mp3",
        "sample_rate": 44100,
        "channels": "stereo",
        "audio_bitrate": 128,
        "video_format": "mp4",
        "resolution": "1080p",
        "frame_rate": 30,
        "video_bitrate": 5000
    }


def get_config_file(client_id: str) -> Path:
    return Path(f"configs/clients/{client_id}/audio_video_config.json")


@router.get("/{client_id}", response_model=ConfigResponse)
async def get_audio_video_config(client_id: str):
    if not session_manager.is_client_online(client_id):
        raise HTTPException(status_code=410, detail="客户端已离线")
    
    config_file = get_config_file(client_id)
    
    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"读取配置失败: {str(e)}")
    else:
        config_data = get_default_audio_video_config()
    
    return ConfigResponse(
        success=True,
        message="获取音视频配置成功",
        status_code=0,
        data=config_data
    )


@router.post("/{client_id}", response_model=ConfigResponse)
async def save_audio_video_config(client_id: str, config: AudioVideoConfig):
    if not session_manager.is_client_online(client_id):
        raise HTTPException(status_code=410, detail="客户端已离线")
    
    config_file = get_config_file(client_id)
    config_file.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        config_dict = config.model_dump()
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, indent=2, ensure_ascii=False)
        
        return ConfigResponse(
            success=True,
            message="音视频配置保存成功",
            status_code=0,
            data=config_dict
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存配置失败: {str(e)}")
