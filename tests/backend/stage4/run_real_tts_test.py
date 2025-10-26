#!/usr/bin/env python3
"""
运行真实TTS生成测试脚本
"""

import os
import sys
import asyncio
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# 添加 backend 目录到 Python 路径
backend_path = project_root / "backend"
sys.path.insert(0, str(backend_path))

def main():
    """运行真实TTS生成测试"""
    print("开始运行真实TTS音频生成测试...")
    
    # 检查环境变量
    required_vars = ["VOLCENGINE_APPID", "VOLCENGINE_ACCESS_TOKEN"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ 缺少必需的环境变量:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n请设置以下环境变量:")
        print("export VOLCENGINE_APPID='your_appid'")
        print("export VOLCENGINE_ACCESS_TOKEN='your_access_token'")
        print("export VOLCENGINE_CLUSTER='volcano_tts'  # 可选，默认为volcano_tts")
        return
    
    print("✅ 环境变量检查通过")
    print(f"   APPID: {os.getenv('VOLCENGINE_APPID')[:10]}...")
    print(f"   CLUSTER: {os.getenv('VOLCENGINE_CLUSTER', 'volcano_tts')}")
    
    try:
        # 导入并运行测试
        from test_real_tts_generation import RealTTSGenerationTest
        
        tester = RealTTSGenerationTest()
        asyncio.run(tester.run_all_tests())
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保已安装所需依赖")
    except Exception as e:
        print(f"❌ 运行测试时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
