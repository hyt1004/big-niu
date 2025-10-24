from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.services.stage1_text_analysis import Stage1TextAnalysisService
from app.services.stage2_image_prompt import Stage2ImagePromptService
from app.services.stage4_video_composition import VideoCompositionService
from app.models.schemas import Stage1Output, Stage2Output, Stage3Output

app = FastAPI(
    title="Big Niu - Text to Video API",
    description="智能文字生成视频系统",
    version="0.1.0"
)


class TextAnalysisRequest(BaseModel):
    story_text: str
    scenes_count: Optional[int] = 10


class ImagePromptRequest(BaseModel):
    stage1_output: Stage1Output


class VideoCompositionRequest(BaseModel):
    stage1_output: Stage1Output
    stage3_outputs: List[Stage3Output]
    output_filename: Optional[str] = "final_video.mp4"


@app.get("/")
async def root():
    return {
        "message": "Big Niu Text-to-Video API",
        "version": "0.1.0",
        "status": "running"
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/api/v1/stage1/analyze", response_model=Stage1Output)
async def stage1_analyze_text(request: TextAnalysisRequest):
    try:
        service = Stage1TextAnalysisService()
        result = await service.analyze_text(
            story_text=request.story_text,
            scenes_count=request.scenes_count
        )
        
        if not service.validate_output(result):
            raise HTTPException(
                status_code=500,
                detail="Generated output validation failed"
            )
        
        return result
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/api/v1/stage2/generate-prompts")
async def stage2_generate_prompts(request: ImagePromptRequest):
    try:
        service = Stage2ImagePromptService()
        prompts = await service.generate_all_prompts(request.stage1_output)
        
        return {
            "total_prompts": len(prompts),
            "prompts": prompts
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/api/v1/stage4/compose-video")
async def stage4_compose_video(request: VideoCompositionRequest):
    try:
        service = VideoCompositionService()
        result = await service.compose_video(
            stage1_output=request.stage1_output,
            stage3_outputs=request.stage3_outputs,
            output_filename=request.output_filename
        )
        
        return {
            "success": True,
            "video_path": result["video_path"],
            "total_duration": result["total_duration"],
            "scenes_count": result["scenes_count"]
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
