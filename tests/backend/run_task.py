#!/usr/bin/env python3
"""
快速运行任务脚本 - 最简单的使用方式
"""

import asyncio
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "backend"))

# 加载环境变量（强制覆盖）
from dotenv import load_dotenv
import os
env_path = project_root / "backend" / ".env"
load_dotenv(env_path, override=True)

# 验证环境变量加载
if not os.getenv("OPENROUTER_API_KEY"):
    print("❌ 警告: OPENROUTER_API_KEY 未设置")
    print(f"📁 .env 路径: {env_path}")
    print(f"📂 .env 存在: {env_path.exists()}")
else:
    print(f"✅ OPENROUTER_API_KEY 已加载: {os.getenv('OPENROUTER_API_KEY')[:20]}...")

from app.services.task_orchestrator import TaskOrchestrator


async def run_task_from_file(text_file: str, scenes_count: int = 3):
    """从文本文件运行任务"""
    
    # 读取文本
    with open(text_file, "r", encoding="utf-8") as f:
        text = f.read()
    
    print(f"📖 从文件读取: {text_file}")
    print(f"📏 文本长度: {len(text)} 字符")
    print(f"🎬 场景数量: {scenes_count}")
    
    # 创建任务编排器
    orchestrator = TaskOrchestrator(output_base_dir="./output/tasks")
    
    # 运行任务
    result = await orchestrator.run_task(
        text=text,
        scenes_count=scenes_count,
        task_name=Path(text_file).stem
    )
    
    return result


async def run_task_from_text(text: str, scenes_count: int = 3, task_name: str = None):
    """从文本字符串运行任务"""
    
    print(f"📝 文本长度: {len(text)} 字符")
    print(f"🎬 场景数量: {scenes_count}")
    
    # 创建任务编排器
    orchestrator = TaskOrchestrator(output_base_dir="./output/tasks")
    
    # 运行任务
    result = await orchestrator.run_task(
        text=text,
        scenes_count=scenes_count,
        task_name=task_name
    )
    
    return result


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Big Niu 任务运行器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 从文件运行
  python run_task.py --file tests/backend/stage1/mock_input_threebody.txt
  
  # 从文件运行并指定场景数
  python run_task.py --file story.txt --scenes 5
  
  # 直接提供文本
  python run_task.py --text "深夜，汪淼站在窗前..." --scenes 3
        """
    )
    
    parser.add_argument(
        "--file",
        type=str,
        help="输入文本文件路径"
    )
    
    parser.add_argument(
        "--text",
        type=str,
        help="直接提供文本内容"
    )
    
    parser.add_argument(
        "--scenes",
        type=int,
        default=3,
        help="场景数量（默认3）"
    )
    
    parser.add_argument(
        "--name",
        type=str,
        help="任务名称"
    )
    
    args = parser.parse_args()
    
    # 验证输入
    if not args.file and not args.text:
        parser.error("必须提供 --file 或 --text 参数之一")
    
    if args.file and args.text:
        parser.error("--file 和 --text 不能同时使用")
    
    # 运行任务
    try:
        if args.file:
            result = asyncio.run(run_task_from_file(args.file, args.scenes))
        else:
            result = asyncio.run(run_task_from_text(args.text, args.scenes, args.name))
        
        if result:
            print("\n" + "="*60)
            print("🎉 任务完成!")
            print("="*60)
            print(f"\n📹 视频: {result['final_output']['video_path']}")
            print(f"📄 字幕: {result['final_output']['subtitle_path']}")
            print(f"\n💡 播放视频: open {result['final_output']['video_path']}")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  任务被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
