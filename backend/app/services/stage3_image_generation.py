import os
import httpx
from io import BytesIO
from typing import Optional, List
from PIL import Image
from app.config import settings
from app.models.schemas import Stage2Output, Stage3Output
from app.services.openrouter_client import OpenRouterClient


class Stage3ImageGenerationService:
    def __init__(self, client: Optional[OpenRouterClient] = None, output_dir: str = "./output/images"):
        self.client = client or OpenRouterClient()
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
    
    async def generate_image_from_prompt(
        self,
        prompt: str,
        size: str = "1024x1024",
        quality: str = "standard",
        model: str = "openai/dall-e-3",
    ) -> bytes:
        """
        通过 OpenRouter 聊天完成接口生成图像
        适用于 GPT-5 Image Mini 等多模态模型
        """
        headers = {
            "Authorization": f"Bearer {self.client.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/hyt1004/big-niu",
            "X-Title": "Big Niu Text-to-Video",
        }
        
        # 使用聊天完成接口，而不是图像生成接口
        # 直接使用字符串格式的 content
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": f"Generate an image: {prompt}"
                }
            ],
            "max_tokens": 4000,
        }
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.client.base_url}/chat/completions",
                headers=headers,
                json=payload,
            )
            
            if response.status_code != 200:
                error_detail = response.text
                raise ValueError(f"API Error {response.status_code}: {error_detail}")
            
            result = response.json()
            
            # 从响应中提取图像
            # GPT-5 Image 模型会在 message.images 中返回图像
            message = result["choices"][0]["message"]
            
            # 检查是否有图像数据
            if "images" in message and len(message["images"]) > 0:
                image_data = message["images"][0]
                image_url = image_data["image_url"]["url"]
                
                # 如果是 base64 编码的图像
                if image_url.startswith("data:image"):
                    import base64
                    # 提取 base64 数据部分
                    base64_data = image_url.split(",")[1]
                    return base64.b64decode(base64_data)
                else:
                    # 如果是 URL，下载图像
                    image_response = await client.get(image_url)
                    image_response.raise_for_status()
                    return image_response.content
            
            # 如果没有找到图像，抛出错误
            raise ValueError(f"No image found in response. Message keys: {message.keys()}")
    
    def save_image(self, image_data: bytes, filename: str) -> str:
        filepath = os.path.join(self.output_dir, filename)
        
        image = Image.open(BytesIO(image_data))
        image.save(filepath, format='PNG')
        
        return filepath
    
    async def generate_scene_image(
        self,
        stage2_output: Stage2Output,
        size: str = "1024x1024",
        quality: str = "standard",
        model: Optional[str] = None,
    ) -> Stage3Output:
        prompt = stage2_output.image_prompt
        
        if stage2_output.negative_prompt:
            prompt = f"{prompt}. Avoid: {stage2_output.negative_prompt}"
        
        model_to_use = model or settings.image_generation_model
        
        image_data = await self.generate_image_from_prompt(
            prompt=prompt,
            size=size,
            quality=quality,
            model=model_to_use,
        )
        
        filename = f"{stage2_output.scene_id}.png"
        image_path = self.save_image(image_data, filename)
        
        image = Image.open(image_path)
        width, height = image.size
        
        return Stage3Output(
            scene_id=stage2_output.scene_id,
            image_path=image_path,
            image_url=None,
            width=width,
            height=height,
            generation_params={
                "model": model_to_use,
                "size": size,
                "quality": quality,
                "prompt": prompt,
            }
        )
    
    async def generate_all_images(
        self,
        stage2_outputs: List[Stage2Output],
        size: str = "1024x1024",
        quality: str = "standard",
        model: Optional[str] = None,
    ) -> List[Stage3Output]:
        results = []
        
        for stage2_output in stage2_outputs:
            try:
                result = await self.generate_scene_image(
                    stage2_output=stage2_output,
                    size=size,
                    quality=quality,
                    model=model,
                )
                results.append(result)
            except Exception as e:
                print(f"Failed to generate image for {stage2_output.scene_id}: {e}")
                raise
        
        return results
