import httpx
import json
from typing import Optional
from app.config import settings


class OpenRouterClient:
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or settings.openrouter_api_key
        self.base_url = base_url or settings.openrouter_base_url
        
        if not self.api_key:
            raise ValueError("OpenRouter API key is required. Set OPENROUTER_API_KEY in .env file")
    
    async def chat_completion(
        self,
        messages: list,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            result = response.json()
            
            return result["choices"][0]["message"]["content"]
    
    async def structured_completion(
        self,
        messages: list,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> dict:
        content = await self.chat_completion(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
        
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON response: {e}\nContent: {content}")
