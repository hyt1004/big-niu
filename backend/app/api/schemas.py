from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ClientStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    EXPIRED = "expired"
    CLEANING = "cleaning"


class ClientRegisterRequest(BaseModel):
    client_name: Optional[str] = None


class ClientResponse(BaseModel):
    success: bool
    client_id: str
    client_name: str
    created_at: str
    message: Optional[str] = None


class HeartbeatResponse(BaseModel):
    success: bool
    client_id: str
    last_heartbeat: str
    message: Optional[str] = "心跳更新成功"


class ClientStatusResponse(BaseModel):
    success: bool
    client_id: str
    status: str
    is_online: bool
    last_heartbeat: Optional[str] = None
    offline_duration: Optional[str] = None


class SessionListResponse(BaseModel):
    success: bool
    sessions: Dict[str, Any]
    total_count: int


class SessionStatsResponse(BaseModel):
    success: bool
    stats: Dict[str, Any]


class OnlineClientsResponse(BaseModel):
    success: bool
    online_clients: Dict[str, Any]
    count: int


class OfflineClientsResponse(BaseModel):
    success: bool
    offline_clients: Dict[str, Any]
    count: int


class CleanupResponse(BaseModel):
    success: bool
    message: str


class ModelConfig(BaseModel):
    anime_mode: str = Field(default="color", description="动漫模式: color/black_white/sepia")
    era: str = Field(default="modern", description="时代背景: ancient/modern/future")
    random_fine_tune: bool = Field(default=False, description="随机微调开关")
    random_composition: bool = Field(default=False, description="随机构图开关")
    random_shot: bool = Field(default=False, description="随机镜头开关")
    shot_direction: str = Field(default="horizontal", description="拍摄方向: horizontal/vertical")
    atmosphere: float = Field(default=0.5, ge=0.0, le=1.0, description="氛围度 0-1")
    distance: float = Field(default=0.5, ge=0.0, le=1.0, description="距离感 0-1")
    realism: float = Field(default=0.5, ge=0.0, le=1.0, description="真实感 0-1")
    dynamic: float = Field(default=0.5, ge=0.0, le=1.0, description="动态感 0-1")
    characters: List[str] = Field(default_factory=list, description="角色列表")


class AudioVideoConfig(BaseModel):
    audio_format: str = Field(default="mp3", description="音频格式: mp3/aac/wav")
    sample_rate: int = Field(default=44100, description="采样率: 22050/44100/48000")
    channels: str = Field(default="stereo", description="声道: mono/stereo")
    audio_bitrate: int = Field(default=128, description="音频比特率: 64/128/256")
    video_format: str = Field(default="mp4", description="视频格式: mp4/avi/mov")
    resolution: str = Field(default="1080p", description="分辨率: 720p/1080p/4k")
    frame_rate: int = Field(default=30, description="帧率: 24/30/60")
    video_bitrate: int = Field(default=5000, description="视频比特率 1000-10000")


class UserPrompt(BaseModel):
    prompt_text: str
    category: Optional[str] = None
    tags: List[str] = Field(default_factory=list)


class GeneratedPrompt(BaseModel):
    id: str
    prompt_text: str
    source: str = Field(description="来源: user_input/model_conversion")
    category: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    config_data: Optional[Dict[str, Any]] = None
    created_at: str
    updated_at: str


class NovelTextData(BaseModel):
    text: str = Field(..., max_length=1000000, description="小说文本内容")
    title: Optional[str] = None
    author: Optional[str] = None
    genre: Optional[str] = None
    storyboard_enabled: bool = Field(default=True, description="是否启用分镜表")


class StoryboardCell(BaseModel):
    shot_number: int
    scene_image: str
    scene_description: str
    dialogue: str
    main_character: str
    shooting_distance: float = Field(ge=0.0, le=1.0)
    dynamic_intensity: float = Field(ge=0.0, le=1.0)
    scene_atmosphere: float = Field(ge=0.0, le=1.0)


class StoryboardTable(BaseModel):
    rows: int
    columns: int
    cells: List[StoryboardCell]


class VideoGenerationRequest(BaseModel):
    storyboard_enabled: bool = Field(default=True)
    quality: str = Field(default="high", description="质量等级: high/medium/low")
    duration: Optional[int] = Field(default=None, description="视频时长(秒)")


class ConfigResponse(BaseModel):
    success: bool
    message: str
    status_code: int = 0
    data: Optional[Dict[str, Any]] = None


class PromptResponse(BaseModel):
    success: bool
    message: str
    prompts: List[GeneratedPrompt]


class NovelSubmissionResponse(BaseModel):
    success: bool
    message: str
    text_length: int
    processed: bool


class StoryboardResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None


class VideoGenerationResponse(BaseModel):
    success: bool
    message: str
    status_code: int = 0
    video_filename: Optional[str] = None
    images_count: int = 0
    audio_included: bool = False
    processing_time: float = 0.0


class VideoStatusResponse(BaseModel):
    success: bool
    status: str
    progress: int = 0
    url: Optional[str] = None
    video_info: Optional[Dict[str, Any]] = None


class ImageUploadResponse(BaseModel):
    success: bool
    image_url: str


class ImageListResponse(BaseModel):
    success: bool
    images: List[Dict[str, Any]]
