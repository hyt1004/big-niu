#!/usr/bin/env python3
"""
快速测试 - 简单的 Stage1 测试，用于验证 API 是否工作
"""

import httpx
import asyncio


async def quick_test():
    # 一个简单的短文本测试
    story = """
深夜，汪淼站在窗前，望着天空中闪烁的星星。最近几天，他总是被一些奇怪的现象困扰着。

"这到底是什么？"汪淼自言自语道。
"""
    
    print("🚀 开始快速测试...")
    print(f"测试文本长度: {len(story)} 字符")
    print(f"目标场景数: 2")
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            print("\n📡 发送请求到 Stage1 API...")
            response = await client.post(
                "http://localhost:8000/api/v1/stage1/analyze",
                json={
                    "story_text": story,
                    "scenes_count": 2
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ 请求成功!")
                print(f"\n📊 结果概览:")
                print(f"  - 故事标题: {result['metadata']['story_title']}")
                print(f"  - 场景数: {result['metadata']['total_scenes']}")
                print(f"  - 角色数: {result['metadata']['total_characters']}")
                print(f"\n✨ Stage1 API 工作正常!")
            else:
                print(f"❌ 请求失败: HTTP {response.status_code}")
                print(f"错误信息: {response.text}")
                
        except httpx.ConnectError:
            print("❌ 无法连接到服务器，请确保后端服务已启动")
        except httpx.TimeoutException:
            print("⏱️ 请求超时，请检查 API Key 配置或网络连接")
        except Exception as e:
            print(f"❌ 发生错误: {str(e)}")


if __name__ == "__main__":
    print("""
╔═══════════════════════════════════════════╗
║    Big Niu Backend - 快速测试工具         ║
╚═══════════════════════════════════════════╝
    """)
    asyncio.run(quick_test())
    print("\n" + "="*45)
    print("💡 提示: 使用 'python test_stages.py' 进行完整测试")
    print("="*45)
