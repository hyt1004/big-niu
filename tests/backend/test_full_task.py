#!/usr/bin/env python3
"""
完整任务测试脚本
测试从原始文本到最终视频的完整流程
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "backend"))

# 加载环境变量
from dotenv import load_dotenv
env_path = project_root / "backend" / ".env"
load_dotenv(env_path)

from app.services.task_orchestrator import TaskOrchestrator


# 测试文本：三体故事片段
TEST_TEXT = """
深夜，汪淼站在窗前，望着天空中闪烁的星星。最近几天，他总是被一些奇怪的现象困扰着。每当他闭上眼睛，就会看到一串神秘的数字在眼前跳动。

"这到底是什么？"汪淼喃喃自语。

第二天，汪淼来到实验室，决定用科学的方法来解开这个谜团。他打开了显微镜，但令他震惊的是，在镜头里，那串数字再次出现了。

"不可能！"汪淼惊呼。

就在这时，他的助手小李走了进来。

"汪教授，您今天看起来不太好。"小李关切地说。

"我遇到了一些奇怪的事情。"汪淼坦白道。

"汪教授，我建议您去见一个人。她叫叶文洁，是红岸基地的前工程师。"小李说。

几天后，汪淼驱车来到了郊外的一座老房子前。门开了，一位满头银发但目光深邃的老人站在门口。

"叶文洁教授，我是汪淼。"汪淼自我介绍道。

"我知道你会来。进来吧，有些事情，是时候让你知道了。"叶文洁说。

房间里，叶文洁给汪淼倒了一杯茶，然后缓缓开口。

"这个宇宙，远比你想象的要复杂。"

"所以，那串数字是..."汪淼的声音有些颤抖。

"是倒计时。三体文明正在接近地球。"叶文洁的话语如同惊雷。
"""


async def test_full_task():
    """测试完整任务流程"""
    
    print("""
╔═══════════════════════════════════════════════════════════╗
║              Big Niu - 完整任务测试                        ║
║          文本 → 场景 → 图像 → 音频 → 视频                  ║
╚═══════════════════════════════════════════════════════════╝
""")
    
    # 创建任务编排器
    orchestrator = TaskOrchestrator(output_base_dir="./output/tasks")
    
    print("📝 测试文本:")
    print("-" * 60)
    print(TEST_TEXT[:200] + "...")
    print("-" * 60)
    
    # 运行完整任务
    try:
        result = await orchestrator.run_task(
            text=TEST_TEXT,
            scenes_count=3,
            task_name="三体数字倒计时"
        )
        
        print("\n" + "="*60)
        print("✅ 任务执行成功!")
        print("="*60)
        
        print(f"\n📁 任务目录: {result['task_dir']}")
        print(f"\n📊 各阶段输出:")
        
        for stage, info in result['stages'].items():
            print(f"\n  {stage.upper()}:")
            for key, value in info.items():
                print(f"    • {key}: {value}")
        
        print(f"\n🎬 最终输出:")
        print(f"  • 视频: {result['final_output']['video_path']}")
        print(f"  • 字幕: {result['final_output']['subtitle_path']}")
        print(f"  • 时长: {result['final_output']['duration']:.1f} 秒")
        
        print(f"\n💡 提示:")
        print(f"  查看视频: open {result['final_output']['video_path']}")
        print(f"  查看任务详情: cat {result['task_dir']}/task_metadata.json")
        
        return result
        
    except Exception as e:
        print(f"\n❌ 任务执行失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


async def test_task_management():
    """测试任务管理功能"""
    
    print("\n" + "="*60)
    print("🔍 测试任务管理功能")
    print("="*60)
    
    orchestrator = TaskOrchestrator(output_base_dir="./output/tasks")
    
    # 列出所有任务
    tasks = orchestrator.list_tasks()
    
    print(f"\n📋 任务列表 (共 {len(tasks)} 个):")
    for task in tasks:
        print(f"\n  • Task ID: {task['task_id']}")
        print(f"    名称: {task['task_name']}")
        print(f"    状态: {task['status']}")
        print(f"    创建时间: {task['created_at']}")


async def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Big Niu 完整任务测试")
    parser.add_argument(
        "--mode",
        choices=["run", "list"],
        default="run",
        help="运行模式: run=运行新任务, list=列出所有任务"
    )
    
    args = parser.parse_args()
    
    if args.mode == "run":
        await test_full_task()
    elif args.mode == "list":
        await test_task_management()


if __name__ == "__main__":
    asyncio.run(main())
