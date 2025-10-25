#!/usr/bin/env python3
"""
测试脚本：图片和声音整合成视频
基于Stage5VideoCompositionService实现视频合成功能
"""

import os
import sys
import json
import tempfile
import shutil
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.app.services.stage5_video_composition import Stage5VideoCompositionService


class VideoCompositionTest:
    def __init__(self):
        self.mockdata_dir = Path(__file__).parent / "mockdata"
        self.stage4_data = None
        self.stage3_data = None
        self.service = None
        
    def setup(self):
        """初始化测试环境"""
        print("🔧 初始化测试环境...")
        
        # 创建临时输出目录
        self.temp_output_dir = tempfile.mkdtemp(prefix="video_test_")
        self.temp_dir = os.path.join(self.temp_output_dir, "temp")
        
        # 初始化服务
        self.service = Stage5VideoCompositionService(
            output_dir=os.path.join(self.temp_output_dir, "videos"),
            temp_dir=self.temp_dir
        )
        
        # 加载测试数据
        self.load_test_data()
        
        print(f"✅ 测试环境初始化完成，输出目录: {self.temp_output_dir}")
        
    def load_test_data(self):
        """加载测试数据"""
        print("📁 加载测试数据...")
        
        # 加载stage4数据
        stage4_file = self.mockdata_dir / "stage4_output.json"
        with open(stage4_file, 'r', encoding='utf-8') as f:
            self.stage4_data = json.load(f)
        
        # 构建stage3数据（图片信息）
        self.stage3_data = []
        for scene in self.stage4_data["scenes"]:
            scene_id = scene["scene_id"]
            image_path = self.mockdata_dir / "images" / f"{scene_id}.png"
            
            if image_path.exists():
                self.stage3_data.append({
                    "scene_id": scene_id,
                    "image_path": str(image_path)
                })
            else:
                print(f"⚠️  警告: 图片文件不存在 {image_path}")
        
        print(f"✅ 加载了 {len(self.stage3_data)} 个场景的图片数据")
        
    def test_compose_video(self):
        """测试compose_video方法"""
        print("\n🎬 测试compose_video方法...")
        
        try:
            video_id = "test_video_compose"
            result = self.service.compose_video(
                stage3_data=self.stage3_data,
                stage4_data=self.stage4_data,
                video_id=video_id
            )
            
            print(f"✅ 视频合成成功!")
            print(f"   视频ID: {result.video_id}")
            print(f"   视频路径: {result.video_path}")
            print(f"   时长: {result.duration}秒")
            print(f"   分辨率: {result.resolution}")
            print(f"   文件大小: {result.file_size}字节")
            print(f"   格式: {result.format}")
            print(f"   场景数量: {result.scenes_count}")
            
            # 验证文件是否存在
            if os.path.exists(result.video_path):
                print(f"✅ 视频文件已生成: {result.video_path}")
            else:
                print(f"❌ 视频文件未找到: {result.video_path}")
                
            return result
            
        except Exception as e:
            print(f"❌ 视频合成失败: {str(e)}")
            return None
            
    def test_compose_video_simple(self):
        """测试compose_video_simple方法"""
        print("\n🎬 测试compose_video_simple方法...")
        
        try:
            # 准备简单测试数据
            image_paths = []
            audio_paths = []
            durations = []
            subtitle_texts = []
            
            current_time = 0.0
            
            for scene in self.stage4_data["scenes"]:
                scene_id = scene["scene_id"]
                image_path = self.mockdata_dir / "images" / f"{scene_id}.png"
                
                if image_path.exists():
                    image_paths.append(str(image_path))
                    durations.append(scene["total_duration"])
                    
                    # 收集音频路径
                    for segment in scene["audio_segments"]:
                        audio_path = self.mockdata_dir / "audio" / Path(segment["audio_path"]).name
                        if audio_path.exists():
                            audio_paths.append(str(audio_path))
                            
                            # 构建字幕数据
                            start_time = current_time + segment["start_time"]
                            end_time = start_time + segment["duration"]
                            subtitle_texts.append((start_time, end_time, segment["text"]))
                    
                    current_time += scene["total_duration"]
            
            video_id = "test_video_simple"
            result = self.service.compose_video_simple(
                image_paths=image_paths,
                audio_paths=audio_paths,
                durations=durations,
                subtitle_texts=subtitle_texts,
                video_id=video_id
            )
            
            print(f"✅ 简单视频合成成功!")
            print(f"   视频ID: {result.video_id}")
            print(f"   视频路径: {result.video_path}")
            print(f"   时长: {result.duration}秒")
            print(f"   分辨率: {result.resolution}")
            print(f"   文件大小: {result.file_size}字节")
            print(f"   格式: {result.format}")
            print(f"   场景数量: {result.scenes_count}")
            
            # 验证文件是否存在
            if os.path.exists(result.video_path):
                print(f"✅ 视频文件已生成: {result.video_path}")
            else:
                print(f"❌ 视频文件未找到: {result.video_path}")
                
            return result
            
        except Exception as e:
            print(f"❌ 简单视频合成失败: {str(e)}")
            return None
            
    def verify_subtitles(self, video_id):
        """验证生成的字幕文件"""
        print(f"\n📝 验证字幕文件...")
        
        subtitle_path = os.path.join(self.service.temp_dir, f"{video_id}_subtitles.srt")
        
        if os.path.exists(subtitle_path):
            print(f"✅ 字幕文件已生成: {subtitle_path}")
            
            # 读取并显示字幕内容
            with open(subtitle_path, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"   字幕文件大小: {len(content)} 字符")
                print("   前几行字幕内容:")
                lines = content.split('\n')[:10]
                for line in lines:
                    if line.strip():
                        print(f"     {line}")
        else:
            print(f"❌ 字幕文件未找到: {subtitle_path}")
            
    def cleanup(self):
        """清理测试环境"""
        print(f"\n🧹 清理测试环境...")
        
        if hasattr(self, 'temp_output_dir') and os.path.exists(self.temp_output_dir):
            shutil.rmtree(self.temp_output_dir)
            print(f"✅ 已清理临时目录: {self.temp_output_dir}")
            
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始视频合成测试")
        print("=" * 50)
        
        try:
            # 初始化
            self.setup()
            
            # 测试compose_video方法
            result1 = self.test_compose_video()
            if result1:
                self.verify_subtitles(result1.video_id)
            
            # 测试compose_video_simple方法
            result2 = self.test_compose_video_simple()
            if result2:
                self.verify_subtitles(result2.video_id)
            
            print("\n" + "=" * 50)
            print("🎉 测试完成!")
            
            if result1 and result2:
                print("✅ 所有测试通过!")
                print(f"📁 输出目录: {self.temp_output_dir}")
                print("💡 提示: 可以查看生成的视频文件来验证效果")
            else:
                print("❌ 部分测试失败，请检查错误信息")
                
        except Exception as e:
            print(f"❌ 测试过程中发生错误: {str(e)}")
        finally:
            # 询问是否清理
            response = input("\n是否清理临时文件? (y/n): ").lower().strip()
            if response in ['y', 'yes', '是']:
                self.cleanup()
            else:
                print(f"💾 临时文件保留在: {self.temp_output_dir}")


def main():
    """主函数"""
    print("🎬 视频合成测试脚本")
    print("基于Stage5VideoCompositionService实现图片和声音整合成视频")
    print()
    
    # 检查FFmpeg是否安装
    import subprocess
    try:
        subprocess.run(['ffmpeg', '-version'], 
                      stdout=subprocess.PIPE, 
                      stderr=subprocess.PIPE, 
                      check=True)
        print("✅ FFmpeg已安装")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ 错误: 未找到FFmpeg，请先安装FFmpeg")
        print("   安装方法: https://ffmpeg.org/download.html")
        return
    
    # 运行测试
    tester = VideoCompositionTest()
    tester.run_all_tests()


if __name__ == "__main__":
    main()