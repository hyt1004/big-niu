#!/usr/bin/env python3
"""调试图像生成 API"""

import asyncio
import httpx
import json

async def test_image_generation():
    api_key = "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"
    base_url = "https://openrouter.ai/api/v1"
    model = "openai/gpt-5-image-mini"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/hyt1004/big-niu",
        "X-Title": "Big Niu Debug",
    }
    
    # 测试1: 简单文本请求
    payload1 = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": "Generate an image of a cat"
            }
        ],
        "max_tokens": 1000,
    }
    
    print("测试 1: 简单文本请求")
    print(f"Payload: {json.dumps(payload1, indent=2)}")
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            response = await client.post(
                f"{base_url}/chat/completions",
                headers=headers,
                json=payload1,
            )
            print(f"状态码: {response.status_code}")
            print(f"响应: {response.text[:500]}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"\n完整响应结构:")
                print(json.dumps(result, indent=2)[:1000])
            
        except Exception as e:
            print(f"错误: {e}")
    
    print("\n" + "="*60)
    
    # 测试2: 结构化 content
    payload2 = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Generate an image of a beautiful sunset"
                    }
                ]
            }
        ],
        "max_tokens": 1000,
    }
    
    print("\n测试 2: 结构化 content")
    print(f"Payload: {json.dumps(payload2, indent=2)}")
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            response = await client.post(
                f"{base_url}/chat/completions",
                headers=headers,
                json=payload2,
            )
            print(f"状态码: {response.status_code}")
            print(f"响应: {response.text[:500]}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"\n完整响应结构:")
                print(json.dumps(result, indent=2)[:1000])
            
        except Exception as e:
            print(f"错误: {e}")

if __name__ == "__main__":
    asyncio.run(test_image_generation())
