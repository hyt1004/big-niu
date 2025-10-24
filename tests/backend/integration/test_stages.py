#!/usr/bin/env python3
"""
测试 Stage1 和 Stage2 API 的脚本
使用方法: python test_stages.py [threebody|journey]
"""

import httpx
import asyncio
import json
import sys
from pathlib import Path


async def test_stage1(story_text: str, scenes_count: int = 5):
    """测试 Stage1 API - 文本分析与分镜设计"""
    print("=" * 60)
    print("开始测试 Stage1: 文本分析与分镜设计")
    print("=" * 60)
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            response = await client.post(
                "http://localhost:8000/api/v1/stage1/analyze",
                json={
                    "story_text": story_text,
                    "scenes_count": scenes_count
                }
            )
            response.raise_for_status()
            result = response.json()
            
            # 打印结果概览
            print(f"\n✅ Stage1 完成!")
            print(f"故事标题: {result['metadata']['story_title']}")
            print(f"总场景数: {result['metadata']['total_scenes']}")
            print(f"角色数量: {result['metadata']['total_characters']}")
            
            print("\n角色列表:")
            for char in result['characters']:
                print(f"  - {char['name']} (ID: {char['id']})")
                print(f"    描述: {char['description'][:50]}...")
            
            print(f"\n场景列表 (共 {len(result['scenes'])} 个):")
            for scene in result['scenes'][:3]:  # 只显示前3个场景
                print(f"  - Scene {scene['order']}: {scene['description'][:60]}...")
            
            # 保存完整结果
            output_file = Path(__file__).parent / "stage1_output.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"\n完整结果已保存到: {output_file}")
            
            return result
            
        except httpx.HTTPStatusError as e:
            print(f"\n❌ Stage1 请求失败 (HTTP {e.response.status_code})")
            print(f"错误信息: {e.response.text}")
            return None
        except Exception as e:
            print(f"\n❌ Stage1 发生错误: {str(e)}")
            return None


async def test_stage2(stage1_output: dict):
    """测试 Stage2 API - 图像生成提示词"""
    if not stage1_output:
        print("\n⚠️  跳过 Stage2 测试 (Stage1 失败)")
        return None
        
    print("\n" + "=" * 60)
    print("开始测试 Stage2: 图像生成提示词")
    print("=" * 60)
    
    async with httpx.AsyncClient(timeout=180.0) as client:
        try:
            response = await client.post(
                "http://localhost:8000/api/v1/stage2/generate-prompts",
                json={"stage1_output": stage1_output}
            )
            response.raise_for_status()
            result = response.json()
            
            # 打印结果概览
            print(f"\n✅ Stage2 完成!")
            print(f"生成提示词数量: {result['total_prompts']}")
            
            print(f"\n提示词示例 (前2个):")
            for prompt in result['prompts'][:2]:
                print(f"\n  Scene ID: {prompt['scene_id']}")
                print(f"  Image Prompt: {prompt['image_prompt'][:100]}...")
                print(f"  Style Tags: {', '.join(prompt['style_tags'])}")
            
            # 保存完整结果
            output_file = Path(__file__).parent / "stage2_output.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"\n完整结果已保存到: {output_file}")
            
            return result
            
        except httpx.HTTPStatusError as e:
            print(f"\n❌ Stage2 请求失败 (HTTP {e.response.status_code})")
            print(f"错误信息: {e.response.text}")
            return None
        except Exception as e:
            print(f"\n❌ Stage2 发生错误: {str(e)}")
            return None


async def main():
    # 确定测试文件
    test_type = sys.argv[1] if len(sys.argv) > 1 else "threebody"
    scenes_count = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    
    if test_type == "journey":
        test_file = Path(__file__).parent.parent / "tests/backend/stage1/mock_input_journey.txt"
        story_name = "西游记"
    else:
        test_file = Path(__file__).parent.parent / "tests/backend/stage1/mock_input_threebody.txt"
        story_name = "三体"
    
    # 读取测试文本
    if not test_file.exists():
        print(f"❌ 测试文件不存在: {test_file}")
        return
    
    with open(test_file, "r", encoding="utf-8") as f:
        story_text = f.read()
    
    print(f"\n📖 使用测试文本: {story_name}")
    print(f"文本长度: {len(story_text)} 字符")
    print(f"目标场景数: {scenes_count}")
    
    # 测试 Stage1
    stage1_result = await test_stage1(story_text, scenes_count)
    
    # 测试 Stage2
    stage2_result = await test_stage2(stage1_result)
    
    # 总结
    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)
    if stage1_result and stage2_result:
        print("✅ Stage1 和 Stage2 都成功完成")
    elif stage1_result:
        print("⚠️  Stage1 完成, Stage2 失败")
    else:
        print("❌ Stage1 失败")


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════╗
║         Big Niu Backend - Stage1 & Stage2 测试工具       ║
╚══════════════════════════════════════════════════════════╝

使用方法:
  python test_stages.py [threebody|journey] [scenes_count]

示例:
  python test_stages.py threebody 5    # 测试三体故事，生成5个场景
  python test_stages.py journey 8      # 测试西游记故事，生成8个场景
  python test_stages.py                # 默认使用三体故事，5个场景
""")
    asyncio.run(main())
