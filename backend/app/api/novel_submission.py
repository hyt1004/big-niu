from fastapi import APIRouter, HTTPException
from .schemas import NovelTextData, NovelSubmissionResponse
from .client_session import session_manager
from .stub_func import StubFunctions
import json
from pathlib import Path

router = APIRouter(prefix="/novel", tags=["小说提交"])


def get_storyboard_file(client_id: str) -> Path:
    return Path(f"configs/clients/{client_id}/storyboard.json")


@router.post("/submit/{client_id}", response_model=NovelSubmissionResponse)
async def submit_novel(client_id: str, novel: NovelTextData):
    if not session_manager.is_client_online(client_id):
        raise HTTPException(status_code=410, detail="客户端已离线")
    
    try:
        text_length = len(novel.text)
        
        if text_length > 1000000:
            raise HTTPException(status_code=400, detail="文本长度超过限制（最大100万字）")
        
        processed = False
        
        if novel.storyboard_enabled:
            result = await StubFunctions.generate_storyboard_from_text(
                novel.text,
                client_id
            )
            
            if result.get("success"):
                storyboard_file = get_storyboard_file(client_id)
                storyboard_file.parent.mkdir(parents=True, exist_ok=True)
                
                with open(storyboard_file, 'w', encoding='utf-8') as f:
                    json.dump(result.get("data"), f, indent=2, ensure_ascii=False)
                
                processed = True
                
                StubFunctions.save_processing_log(
                    client_id,
                    "novel_submission",
                    "success",
                    {
                        "title": novel.title,
                        "text_length": text_length,
                        "storyboard_generated": True
                    }
                )
        
        return NovelSubmissionResponse(
            success=True,
            message="小说提交成功" + ("，分镜表已生成" if processed else ""),
            text_length=text_length,
            processed=processed
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"小说提交失败: {str(e)}")
