#!/usr/bin/env python3
"""
Big Niu 完整测试流程运行器
运行所有 Stage 的测试
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent
backend_dir = project_root / "backend"
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(backend_dir))

from colorama import init, Fore, Style

# 初始化 colorama
init(autoreset=True)


def print_header(text: str):
    """打印标题"""
    print("\n" + "=" * 70)
    print(f"{Fore.CYAN}{Style.BRIGHT}{text}")
    print("=" * 70 + "\n")


def print_success(text: str):
    """打印成功信息"""
    print(f"{Fore.GREEN}✅ {text}")


def print_error(text: str):
    """打印错误信息"""
    print(f"{Fore.RED}❌ {text}")


def print_info(text: str):
    """打印信息"""
    print(f"{Fore.YELLOW}ℹ️  {text}")


async def run_stage1_tests():
    """运行 Stage1 测试"""
    print_header("Stage 1: 文本分析与场景分镜")
    
    from backend.app.services.stage1_text_analysis import Stage1TextAnalysisService
    
    try:
        service = Stage1TextAnalysisService()
        
        # 读取测试文本
        test_file = Path(__file__).parent / "stage1" / "mock_input_threebody.txt"
        with open(test_file, "r", encoding="utf-8") as f:
            story_text = f.read()
        
        print_info(f"测试文本长度: {len(story_text)} 字符")
        print_info("目标场景数: 3")
        
        # 运行分析
        result = await service.analyze_text(story_text, scenes_count=3)
        
        print_success(f"故事标题: {result.metadata.story_title}")
        print_success(f"角色数量: {result.metadata.total_characters}")
        print_success(f"场景数量: {result.metadata.total_scenes}")
        
        # 保存输出
        import json
        output_file = Path(__file__).parent / "fixtures" / "stage1_output.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result.model_dump(), f, ensure_ascii=False, indent=2)
        
        print_info(f"输出已保存: {output_file}")
        
        return result
        
    except Exception as e:
        print_error(f"Stage1 测试失败: {str(e)}")
        raise


async def run_stage2_tests(stage1_output):
    """运行 Stage2 测试"""
    print_header("Stage 2: 图像提示词生成")
    
    from backend.app.services.stage2_image_prompt import Stage2ImagePromptService
    
    try:
        service = Stage2ImagePromptService()
        
        print_info(f"处理 {len(stage1_output.scenes)} 个场景")
        
        # 生成提示词
        results = await service.generate_all_prompts(stage1_output)
        
        print_success(f"生成提示词数量: {len(results)}")
        
        for i, prompt in enumerate(results, 1):
            print_info(f"场景 {i} ({prompt.scene_id}): {prompt.image_prompt[:60]}...")
        
        # 保存输出
        import json
        output_file = Path(__file__).parent / "fixtures" / "stage2_output.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump({
                "prompts": [p.model_dump() for p in results]
            }, f, ensure_ascii=False, indent=2)
        
        print_info(f"输出已保存: {output_file}")
        
        return results
        
    except Exception as e:
        print_error(f"Stage2 测试失败: {str(e)}")
        raise


async def run_stage3_tests(stage2_outputs):
    """运行 Stage3 测试"""
    print_header("Stage 3: 图像生成（并发模式）")
    
    from backend.app.services.stage3_image_generation import Stage3ImageGenerationService
    
    try:
        output_dir = Path(__file__).parent / "fixtures" / "output" / "images"
        service = Stage3ImageGenerationService(output_dir=str(output_dir))
        
        print_info(f"输出目录: {output_dir}")
        print_info(f"将生成 {len(stage2_outputs)} 张图像")
        print_info("🚀 并发模式：所有图像同时生成，预计耗时 ~30秒")
        
        import time
        start_time = time.time()
        
        # 使用并发模式生成所有图像
        results = await service.generate_all_images(
            stage2_outputs=stage2_outputs,
            size="1024x1024",
            quality="standard",
            concurrent=True  # 启用并发，提升N倍速度
        )
        
        elapsed = time.time() - start_time
        
        print_success(f"生成了 {len(results)} 张图像")
        print_success(f"总耗时: {elapsed:.1f} 秒")
        print_success(f"平均速度: {elapsed/len(results):.1f} 秒/张")
        
        for result in results:
            print_info(f"  • {result.scene_id}: {result.image_path}")
        
        # 保存输出
        import json
        output_file = Path(__file__).parent / "fixtures" / "stage3_output.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump({
                "total_images": len(results),
                "elapsed_seconds": elapsed,
                "images": [r.model_dump() for r in results]
            }, f, ensure_ascii=False, indent=2)
        
        print_info(f"输出已保存: {output_file}")
        
        return results
        
    except Exception as e:
        print_error(f"Stage3 测试失败: {str(e)}")
        raise


async def main():
    """主测试流程"""
    print_header("🚀 Big Niu 完整测试流程")
    
    print(f"{Fore.CYAN}测试流程:")
    print("  1️⃣  Stage1: 文本分析与场景分镜")
    print("  2️⃣  Stage2: 图像提示词生成")
    print("  3️⃣  Stage3: 图像生成（仅第一个场景）\n")
    
    try:
        # Stage 1
        stage1_output = await run_stage1_tests()
        
        # Stage 2
        stage2_outputs = await run_stage2_tests(stage1_output)
        
        # Stage 3
        stage3_outputs = await run_stage3_tests(stage2_outputs)
        
        # 总结
        print_header("✅ 测试完成总结")
        print_success(f"Stage1: 分析了 {stage1_output.metadata.total_scenes} 个场景")
        print_success(f"Stage2: 生成了 {len(stage2_outputs)} 个提示词")
        print_success(f"Stage3: 生成了 {len(stage3_outputs)} 张图像")
        
        print(f"\n{Fore.GREEN}{Style.BRIGHT}🎉 所有测试通过！")
        
        return True
        
    except Exception as e:
        print_header("❌ 测试失败")
        print_error(f"错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    try:
        # 检查是否安装 colorama
        try:
            import colorama
        except ImportError:
            print("警告: colorama 未安装，输出将没有颜色")
            # 定义空的颜色类
            class Fore:
                CYAN = GREEN = RED = YELLOW = ""
            class Style:
                BRIGHT = ""
        
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
        sys.exit(1)
