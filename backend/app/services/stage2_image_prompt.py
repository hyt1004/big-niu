from typing import Optional, List
from app.config import settings
from app.models.schemas import Stage1Output, Scene, Character, Stage2Output
from app.services.openrouter_client import OpenRouterClient


class Stage2ImagePromptService:
    def __init__(self, client: Optional[OpenRouterClient] = None):
        self.client = client or OpenRouterClient()
    
    def _build_character_reference(self, characters: List[Character], character_ids: List[str]) -> str:
        character_descs = []
        for char in characters:
            if char.id in character_ids:
                character_descs.append(f"{char.name}: {char.description}")
        
        return ", ".join(character_descs) if character_descs else "无角色"
    
    def _build_prompt_generation_request(
        self,
        scene: Scene,
        characters: List[Character],
    ) -> str:
        character_ref = self._build_character_reference(characters, scene.characters)
        
        prompt = f"""你是一个专业的AI图像生成提示词工程师。请根据以下场景信息，生成适合Stable Diffusion或DALL-E的高质量图像生成提示词。

场景信息：
- 场景描述：{scene.description}
- 构图：{scene.composition}
- 出场角色：{character_ref}
- 旁白：{scene.narration}

请生成以下JSON格式的输出：

{{
  "scene_id": "{scene.scene_id}",
  "image_prompt": "详细的英文图像生成提示词（包含场景、角色、构图、风格、质量标签）",
  "negative_prompt": "负向提示词（要避免的元素）",
  "style_tags": ["anime", "high_quality", "4k"],
  "characters_in_scene": {scene.characters}
}}

要求：
1. 提示词要用英文，详细具体
2. 包含场景环境、光线、氛围、角色特征、构图角度
3. 添加质量提升标签（如：masterpiece, best quality, highly detailed, 4k, ultra sharp）
4. 添加风格标签（如：anime style, illustration, cinematic lighting）
5. 负向提示词要避免低质量、变形、多余元素
6. 只返回JSON，不要包含其他解释"""
        
        return prompt
    
    async def generate_image_prompt(
        self,
        scene: Scene,
        characters: List[Character],
    ) -> Stage2Output:
        prompt = self._build_prompt_generation_request(scene, characters)
        
        messages = [
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        result = await self.client.structured_completion(
            messages=messages,
            model=settings.image_prompt_model,
            temperature=0.7,
            max_tokens=1024,
        )
        
        return Stage2Output(**result)
    
    async def generate_all_prompts(
        self,
        stage1_output: Stage1Output,
    ) -> List[Stage2Output]:
        prompts = []
        
        for scene in stage1_output.scenes:
            prompt_output = await self.generate_image_prompt(
                scene=scene,
                characters=stage1_output.characters,
            )
            prompts.append(prompt_output)
        
        return prompts
    
    def build_simple_prompt(
        self,
        scene: Scene,
        characters: List[Character],
        style: str = "anime",
    ) -> str:
        character_ref = self._build_character_reference(characters, scene.characters)
        
        base_prompt = f"{scene.description}, {scene.composition}"
        
        if character_ref and character_ref != "无角色":
            base_prompt = f"{character_ref}, {base_prompt}"
        
        style_tags = f"{style} style, masterpiece, best quality, highly detailed, 4k, cinematic lighting"
        
        full_prompt = f"{base_prompt}, {style_tags}"
        
        return full_prompt
