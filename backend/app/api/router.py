from fastapi import APIRouter
from . import (
    client_management,
    audio_video_config,
    model_config,
    prompt_management,
    novel_submission,
    storyboard_management,
    image_management,
    video_management
)

api_router = APIRouter(prefix="/api/v1/bigniu")

api_router.include_router(client_management.router)
api_router.include_router(audio_video_config.router)
api_router.include_router(model_config.router)
api_router.include_router(prompt_management.router)
api_router.include_router(novel_submission.router)
api_router.include_router(storyboard_management.router)
api_router.include_router(image_management.router)
api_router.include_router(video_management.router)
