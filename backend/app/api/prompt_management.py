import json
import uuid
from pathlib import Path
from datetime import datetime
from fastapi import APIRouter, HTTPException
from .schemas import UserPrompt, PromptResponse, GeneratedPrompt
from .client_session import session_manager

router = APIRouter(prefix="/prompts", tags=["提示词管理"])


def get_user_prompts_file(client_id: str) -> Path:
    return Path(f"configs/clients/{client_id}/user_prompts.json")


def get_generated_prompts_file(client_id: str) -> Path:
    return Path(f"configs/clients/{client_id}/generated_prompts.json")


@router.get("/{client_id}", response_model=PromptResponse)
async def get_prompts(client_id: str):
    if not session_manager.is_client_online(client_id):
        raise HTTPException(status_code=410, detail="客户端已离线")
    
    all_prompts = []
    
    user_prompts_file = get_user_prompts_file(client_id)
    if user_prompts_file.exists():
        try:
            with open(user_prompts_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                all_prompts.extend(data.get("prompts", []))
        except Exception as e:
            print(f"Error loading user prompts: {e}")
    
    generated_prompts_file = get_generated_prompts_file(client_id)
    if generated_prompts_file.exists():
        try:
            with open(generated_prompts_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                all_prompts.extend(data.get("prompts", []))
        except Exception as e:
            print(f"Error loading generated prompts: {e}")
    
    all_prompts.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    
    prompts_obj = [GeneratedPrompt(**p) for p in all_prompts]
    
    return PromptResponse(
        success=True,
        message="获取提示词成功",
        prompts=prompts_obj
    )


@router.post("/{client_id}", response_model=PromptResponse)
async def save_prompt(client_id: str, prompt: UserPrompt):
    if not session_manager.is_client_online(client_id):
        raise HTTPException(status_code=410, detail="客户端已离线")
    
    user_prompts_file = get_user_prompts_file(client_id)
    user_prompts_file.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        prompts = []
        if user_prompts_file.exists():
            with open(user_prompts_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                prompts = data.get("prompts", [])
        
        new_prompt = {
            "id": str(uuid.uuid4()),
            "prompt_text": prompt.prompt_text,
            "source": "user_input",
            "category": prompt.category or "用户输入",
            "tags": prompt.tags,
            "config_data": None,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        prompts.append(new_prompt)
        
        with open(user_prompts_file, 'w', encoding='utf-8') as f:
            json.dump({
                "prompts": prompts,
                "last_updated": datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
        
        all_prompts = []
        all_prompts.extend(prompts)
        
        generated_prompts_file = get_generated_prompts_file(client_id)
        if generated_prompts_file.exists():
            with open(generated_prompts_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                all_prompts.extend(data.get("prompts", []))
        
        all_prompts.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        prompts_obj = [GeneratedPrompt(**p) for p in all_prompts]
        
        return PromptResponse(
            success=True,
            message="提示词保存成功",
            prompts=prompts_obj
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存提示词失败: {str(e)}")
