from typing import Optional
from app.config import settings
from app.models.schemas import Stage1Output, Character, Scene, Metadata, Dialogue
from app.services.openrouter_client import OpenRouterClient


class Stage1TextAnalysisService:
    def __init__(self, client: Optional[OpenRouterClient] = None):
        self.client = client or OpenRouterClient()
    
    def _build_analysis_prompt(self, story_text: str, scenes_count: int) -> str:
        prompt = f"""你是一个专业的故事分析和分镜设计专家。请分析以下故事文本，并将其拆分为 {scenes_count} 个分镜场景。

故事文本：
{story_text}

请按照以下JSON格式输出结构化数据：

{{
  "metadata": {{
    "total_scenes": {scenes_count},
    "story_title": "故事标题（根据内容推断）",
    "total_characters": 角色总数
  }},
  "characters": [
    {{
      "id": "char_001",
      "name": "角色名称",
      "description": "角色外貌特征描述（用于图像生成）",
      "personality": "性格特点"
    }}
  ],
  "scenes": [
    {{
      "scene_id": "scene_001",
      "order": 1,
      "description": "场景的视觉描述（环境、氛围、光线等）",
      "composition": "镜头构图（如：远景/中景/特写，俯视/平视/仰视）",
      "characters": ["char_001"],
      "narration": "旁白文字（叙述性文本）",
      "dialogues": [
        {{
          "character": "char_001",
          "text": "对话内容",
          "emotion": "情绪（如：愉悦、悲伤、愤怒等）"
        }}
      ]
    }}
  ]
}}

要求：
1. 将故事均匀拆分为 {scenes_count} 个场景
2. 详细描述每个角色的外貌特征，用于后续图像生成
3. 每个场景的描述要具体，包含视觉元素
4. 场景构图要符合电影分镜语言
5. 区分旁白和对话
6. 只返回JSON，不要包含其他解释文字"""
        
        return prompt
    
    async def analyze_text(
        self,
        story_text: str,
        scenes_count: Optional[int] = None,
    ) -> Stage1Output:
        if not story_text or not story_text.strip():
            raise ValueError("Story text cannot be empty")
        
        scenes_count = scenes_count or settings.default_scenes_count
        
        if scenes_count < 1 or scenes_count > 100:
            raise ValueError("Scenes count must be between 1 and 100")
        
        prompt = self._build_analysis_prompt(story_text, scenes_count)
        
        messages = [
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        result = await self.client.structured_completion(
            messages=messages,
            model=settings.text_analysis_model,
            temperature=0.7,
            max_tokens=4096,
        )
        
        return Stage1Output(**result)
    
    def validate_output(self, output: Stage1Output) -> bool:
        if not output.characters:
            return False
        
        if not output.scenes:
            return False
        
        if len(output.scenes) != output.metadata.total_scenes:
            return False
        
        character_ids = {char.id for char in output.characters}
        for scene in output.scenes:
            for char_id in scene.characters:
                if char_id not in character_ids:
                    return False
            
            for dialogue in scene.dialogues:
                if dialogue.character not in character_ids:
                    return False
        
        return True
