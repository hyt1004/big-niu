import json
import uuid
from pathlib import Path
from datetime import datetime
from fastapi import APIRouter, HTTPException
from .schemas import ModelConfig, ConfigResponse
from .client_session import session_manager
from .stub_func import StubFunctions

router = APIRouter(prefix="/config/model", tags=["模型配置"])


def get_default_model_config() -> dict:
    return {
        "anime_mode": "color",
        "era": "modern",
        "random_fine_tune": False,
        "random_composition": False,
        "random_shot": False,
        "shot_direction": "horizontal",
        "atmosphere": 50,
        "distance": 50,
        "realism": 50,
        "dynamic": 50,
        "characters": []
    }


def get_config_file(client_id: str) -> Path:
    return Path(f"configs/clients/{client_id}/model_config.json")


def get_generated_prompts_file(client_id: str) -> Path:
    return Path(f"configs/clients/{client_id}/generated_prompts.json")


@router.get("/{client_id}", response_model=ConfigResponse)
async def get_model_config(client_id: str):
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
        config_data = get_default_model_config()
    
    return ConfigResponse(
        success=True,
        message="获取模型配置成功",
        status_code=0,
        data=config_data
    )


@router.post("/{client_id}", response_model=ConfigResponse)
async def save_model_config(client_id: str, config: ModelConfig):
    if not session_manager.is_client_online(client_id):
        raise HTTPException(status_code=410, detail="客户端已离线")
    
    config_file = get_config_file(client_id)
    config_file.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        config_dict = config.model_dump()
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, indent=2, ensure_ascii=False)
        
        prompt_text = StubFunctions.generate_prompt_from_model_config(config_dict)
        
        prompts_file = get_generated_prompts_file(client_id)
        prompts = []
        if prompts_file.exists():
            try:
                with open(prompts_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    prompts = data.get("prompts", [])
            except:
                prompts = []
        
        new_prompt = {
            "id": str(uuid.uuid4()),
            "prompt_text": prompt_text,
            "source": "model_conversion",
            "category": "模型配置生成",
            "tags": ["自动生成", config_dict.get("anime_mode", ""), config_dict.get("era", "")],
            "config_data": config_dict,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        prompts.append(new_prompt)
        
        with open(prompts_file, 'w', encoding='utf-8') as f:
            json.dump({
                "prompts": prompts,
                "last_updated": datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
        
        return ConfigResponse(
            success=True,
            message="配置保存成功，提示词已自动生成",
            status_code=0,
            data=config_dict
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存配置失败: {str(e)}")
