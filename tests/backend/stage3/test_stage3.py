#!/usr/bin/env python3
"""
Stage3 图像生成测试脚本
使用 Stage2 的输出生成实际图像
"""

import asyncio
import json
import sys
import os
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "backend"))

# 加载环境变量
from dotenv import load_dotenv
env_path = project_root / "backend" / ".env"
load_dotenv(env_path)

from app.services.stage3_image_generation import Stage3ImageGenerationService
from app.models.schemas import Stage2Output


async def test_stage3_from_stage2_output():
    """使用已有的 stage2_output.json 测试 Stage3"""
    
    print("=" * 60)
    print("Stage3 图像生成测试")
    print("=" * 60)
    
    # 读取 Stage2 的输出（从 fixtures 目录）
    stage2_file = Path(__file__).parent.parent / "fixtures" / "stage2_output.json"
    
    if not stage2_file.exists():
        print(f"❌ 找不到 Stage2 输出文件: {stage2_file}")
        print("请先运行 Stage1 和 Stage2 测试生成输出文件")
        print("或运行: python run_all_tests.py")
        return None
    
    with open(stage2_file, "r", encoding="utf-8") as f:
        stage2_data = json.load(f)
    
    # 转换为 Stage2Output 对象
    stage2_outputs = [Stage2Output(**prompt) for prompt in stage2_data["prompts"]]
    
    print(f"\n📖 读取 Stage2 输出: {len(stage2_outputs)} 个场景")
    print(f"场景 IDs: {[s.scene_id for s in stage2_outputs]}")
    
    # 创建 Stage3 服务（使用 fixtures 目录）
    output_dir = Path(__file__).parent.parent / "fixtures" / "output" / "images"
    stage3_service = Stage3ImageGenerationService(output_dir=str(output_dir))
    
    print(f"\n📁 图像保存目录: {output_dir}")
    print(f"\n⚠️  注意: 图像生成需要付费，每张图约需 10-30 秒")
    print(f"🚀 并发模式：{len(stage2_outputs)} 张图同时生成，预计耗时 ~30秒\n")
    
    # 生成所有场景
    print(f"🎨 开始生成 {len(stage2_outputs)} 个场景的图像\n")
    
    try:
        import time
        start_time = time.time()
        
        # 使用并发模式生成所有图像
        results = await stage3_service.generate_all_images(
            stage2_outputs=stage2_outputs,
            size="1024x1024",
            quality="standard",
            concurrent=True  # 启用并发，提升3倍速度
        )
        
        elapsed = time.time() - start_time
        
        print(f"\n✅ 所有图像生成成功!")
        print(f"⏱️  总耗时: {elapsed:.1f} 秒")
        print(f"📊 平均速度: {elapsed/len(results):.1f} 秒/张")
        print(f"\n生成的图像:")
        
        for result in results:
            print(f"  • {result.scene_id}: {result.image_path}")
        
        # 保存结果（到 fixtures 目录）
        output_file = Path(__file__).parent.parent / "fixtures" / "stage3_output.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump({
                "total_images": len(results),
                "elapsed_seconds": elapsed,
                "images": [
                    {
                        "scene_id": r.scene_id,
                        "image_path": r.image_path,
                        "width": r.width,
                        "height": r.height,
                        "generation_params": r.generation_params
                    }
                    for r in results
                ]
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n结果已保存到: {output_file}")
        
        return results
        
    except Exception as e:
        print(f"\n❌ 图像生成失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


async def test_stage3_full_pipeline():
    """完整测试 Stage1 -> Stage2 -> Stage3"""
    
    print("\n" + "=" * 60)
    print("完整流程测试: Stage1 -> Stage2 -> Stage3")
    print("=" * 60)
    
    from app.services.stage1_text_analysis import Stage1TextAnalysisService
    from app.services.stage2_image_prompt import Stage2ImagePromptService
    
    # 简短的测试故事
    story_text = """
    深夜，汪淼站在窗前，望着天空中闪烁的星星。
    "这到底是什么？"汪淼自言自语道。
    """
    
    print(f"\n📖 测试故事长度: {len(story_text)} 字符")
    print("目标场景数: 1 (测试模式)")
    
    # Stage1
    print("\n--- Stage1: 文本分析 ---")
    stage1_service = Stage1TextAnalysisService()
    stage1_output = await stage1_service.analyze_text(story_text, scenes_count=1)
    print(f"✅ 生成场景: {stage1_output.metadata.total_scenes}")
    print(f"✅ 角色数量: {stage1_output.metadata.total_characters}")
    
    # Stage2
    print("\n--- Stage2: 提示词生成 ---")
    stage2_service = Stage2ImagePromptService()
    stage2_outputs = await stage2_service.generate_all_prompts(stage1_output)
    print(f"✅ 生成提示词: {len(stage2_outputs)}")
    
    # Stage3
    print("\n--- Stage3: 图像生成 ---")
    output_dir = Path(__file__).parent.parent / "fixtures" / "output" / "images"
    stage3_service = Stage3ImageGenerationService(output_dir=str(output_dir))
    
    result = await stage3_service.generate_scene_image(
        stage2_output=stage2_outputs[0],
        size="1024x1024",
        quality="standard"
    )
    
    print(f"✅ 图像已生成: {result.image_path}")
    
    return result


if __name__ == "__main__":
    print("""
╔═══════════════════════════════════════════════════════════╗
║          Big Niu - Stage3 图像生成测试工具                ║
╚═══════════════════════════════════════════════════════════╝

选择测试模式:
1. 使用现有 Stage2 输出测试 (推荐，节省成本)
2. 完整流程测试 (Stage1 -> Stage2 -> Stage3)
""")
    
    # 默认使用模式1
    mode = 1
    
    if mode == 1:
        result = asyncio.run(test_stage3_from_stage2_output())
    else:
        result = asyncio.run(test_stage3_full_pipeline())
    
    print("\n" + "=" * 60)
    if result:
        print("✅ Stage3 测试完成!")
        if isinstance(result, list):
            print(f"生成了 {len(result)} 张图像:")
            for r in result:
                print(f"  • {r.image_path}")
        else:
            print(f"查看生成的图像: {result.image_path}")
    else:
        print("❌ Stage3 测试失败")
    print("=" * 60)
