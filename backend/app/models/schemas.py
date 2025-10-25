from typing import List, Optional
from pydantic import BaseModel, Field


class Character(BaseModel):
    id: str = Field(..., description="角色ID")
    name: str = Field(..., description="角色名称")
    description: str = Field(..., description="外貌特征描述")
    personality: Optional[str] = Field(None, description="性格特点")


class Dialogue(BaseModel):
    character: str = Field(..., description="角色ID")
    text: str = Field(..., description="对话文本")
    emotion: Optional[str] = Field(None, description="情绪")


class Scene(BaseModel):
    scene_id: str = Field(..., description="场景ID")
    order: int = Field(..., description="场景顺序")
    description: str = Field(..., description="场景描述")
    composition: str = Field(..., description="构图说明")
    characters: List[str] = Field(default_factory=list, description="涉及角色ID列表")
    narration: str = Field(..., description="旁白文字")
    dialogues: List[Dialogue] = Field(default_factory=list, description="对话列表")


class Metadata(BaseModel):
    total_scenes: int = Field(..., description="总场景数")
    story_title: str = Field(..., description="故事标题")
    total_characters: int = Field(..., description="角色总数")


class Stage1Output(BaseModel):
    metadata: Metadata
    characters: List[Character]
    scenes: List[Scene]


class ImagePrompt(BaseModel):
    scene_id: str = Field(..., description="场景ID")
    prompt: str = Field(..., description="图像生成提示词")
    negative_prompt: Optional[str] = Field(None, description="负向提示词")
    style_tags: List[str] = Field(default_factory=list, description="风格标签")


class Stage2Output(BaseModel):
    scene_id: str
    image_prompt: str
    negative_prompt: Optional[str] = None
    style_tags: List[str] = Field(default_factory=list)
    characters_in_scene: List[str] = Field(default_factory=list)


class Stage3Output(BaseModel):
    scene_id: str = Field(..., description="场景ID")
    image_path: str = Field(..., description="本地图片路径")
    image_url: Optional[str] = Field(None, description="图片URL(如有)")
    width: int = Field(..., description="图片宽度")
    height: int = Field(..., description="图片高度")
    generation_params: dict = Field(default_factory=dict, description="生成参数")


class AudioSegment(BaseModel):
    type: str = Field(..., description="音频类型: narration/dialogue")
    text: str = Field(..., description="文本内容")
    audio_path: str = Field(..., description="音频文件路径")
    duration: float = Field(..., description="音频时长(秒)")
    start_time: float = Field(..., description="开始时间(秒)")
    character: Optional[str] = Field(None, description="角色ID")
    character_name: Optional[str] = Field(None, description="角色名称")
    emotion: Optional[str] = Field(None, description="情绪")
    voice: Optional[str] = Field(None, description="音色ID")


class SceneAudio(BaseModel):
    scene_id: str = Field(..., description="场景ID")
    audio_segments: List[AudioSegment] = Field(..., description="音频段列表")
    total_duration: float = Field(..., description="场景总时长(秒)")


class Stage4Output(BaseModel):
    scenes: List[SceneAudio] = Field(..., description="场景音频列表")
    total_video_duration: float = Field(..., description="视频总时长(秒)")
    character_voices: dict = Field(..., description="角色音色映射")


class Stage5Output(BaseModel):
    video_id: str = Field(..., description="视频ID")
    video_path: str = Field(..., description="视频文件路径")
    video_url: Optional[str] = Field(None, description="视频URL(如有)")
    duration: float = Field(..., description="视频时长(秒)")
    resolution: str = Field(..., description="分辨率")
    file_size: int = Field(..., description="文件大小(字节)")
    format: str = Field(..., description="视频格式")
    scenes_count: int = Field(..., description="场景数量")
