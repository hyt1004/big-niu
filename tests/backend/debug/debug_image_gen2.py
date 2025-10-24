#!/usr/bin/env python3
"""调试图像生成 API - 查看完整响应"""

import asyncio
import httpx
import json

async def test_simple():
    api_key = "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"
    base_url = "https://openrouter.ai/api/v1"
    model = "openai/gpt-5-image-mini"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/hyt1004/big-niu",
        "X-Title": "Big Niu Debug",
    }
    
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": "Generate an image of a cute cat sitting on a chair"
            }
        ],
        "max_tokens": 4000,
    }
    
    print("发送请求...")
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{base_url}/chat/completions",
            headers=headers,
            json=payload,
        )
        
        print(f"状态码: {response.status_code}\n")
        
        if response.status_code == 200:
            result = response.json()
            
            # 保存完整响应到文件
            with open("full_response.json", "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            print("完整响应已保存到 full_response.json")
            print("\n响应结构:")
            print(f"- ID: {result.get('id')}")
            print(f"- Model: {result.get('model')}")
            print(f"- Choices: {len(result.get('choices', []))}")
            
            if result.get('choices'):
                choice = result['choices'][0]
                message = choice.get('message', {})
                print(f"\nMessage 结构:")
                print(f"- Role: {message.get('role')}")
                print(f"- Content type: {type(message.get('content'))}")
                print(f"- Content: {message.get('content')[:200] if message.get('content') else 'Empty'}")
                
                # 检查所有可能的字段
                print(f"\nMessage 所有字段: {list(message.keys())}")
                
                # 检查是否有 image 相关字段
                for key, value in message.items():
                    if 'image' in key.lower() or 'url' in key.lower():
                        print(f"\n发现图像相关字段: {key}")
                        print(f"值: {value}")
        else:
            print(f"错误响应: {response.text}")

if __name__ == "__main__":
    asyncio.run(test_simple())
