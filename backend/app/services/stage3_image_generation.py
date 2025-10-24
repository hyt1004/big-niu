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
        headers = {
            "Authorization": f"Bearer {self.client.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/hyt1004/big-niu",
            "X-Title": "Big Niu Text-to-Video",
        }
        
        payload = {
            "model": model,
            "prompt": prompt,
            "n": 1,
            "size": size,
            "quality": quality,
        }
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.client.base_url}/images/generations",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            result = response.json()
            
            image_url = result["data"][0]["url"]
            
            image_response = await client.get(image_url)
            image_response.raise_for_status()
            
            return image_response.content
    
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
