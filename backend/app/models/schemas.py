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
