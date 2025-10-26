#!/usr/bin/env python3
"""
真实TTS生成测试脚本
基于Stage4TTSService实现真实的音频生成功能
读取stage1输出数据，调用火山引擎TTS接口生成真实音频文件
"""

import os
import sys
import json
import tempfile
import shutil
import asyncio
from pathlib import Path
from typing import Dict, List, Any

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# 添加backend目录到Python路径
backend_path = project_root / "backend"
sys.path.insert(0, str(backend_path))

from backend.app.services.stage4_tts import Stage4TTSService, Stage4Output, SceneAudio, AudioSegment
from backend.app.models.schemas import Character, Scene, Dialogue, Stage1Output


class RealTTSGenerationTest:
    def __init__(self):
        self.mockdata_dir = Path(__file__).parent / "mockdata"
        self.stage1_data = None
        self.service = None
        self.output_dir = None
        
    def setup(self):
        """初始化测试环境"""
        print("🔧 初始化TTS生成测试环境...")
        
        # 检查环境变量
        if not self._check_environment():
            return False
            
        # 创建输出目录
        self.output_dir = Path(tempfile.mkdtemp(prefix="tts_generation_"))
        print(f"📁 输出目录: {self.output_dir}")
        
        # 创建音频输出目录
        self.audio_dir = self.output_dir / "audio"
        self.audio_dir.mkdir(exist_ok=True)
        
        # 初始化TTS服务
        self.service = Stage4TTSService(
            output_dir=str(self.audio_dir)
        )
        
        # 加载测试数据
        self.load_stage1_data()
        
        print("✅ TTS生成测试环境初始化完成")
        return True
        
    def _check_environment(self):
        """检查环境变量"""
        required_vars = ["VOLCENGINE_APPID", "VOLCENGINE_ACCESS_TOKEN"]
        
        for var in required_vars:
            if not os.getenv(var):
                print(f"❌ 环境变量 {var} 未设置")
                return False
                
        cluster = os.getenv("VOLCENGINE_CLUSTER", "volcano_tts")
        print(f"✅ 环境变量检查通过")
        print(f"   APPID: {os.getenv('VOLCENGINE_APPID')[:10]}...")
        print(f"   CLUSTER: {cluster}")
        return True
        
    def load_stage1_data(self):
        """加载stage1输出数据"""
        print("📁 加载Stage1输出数据...")
        
        stage1_file = self.mockdata_dir / "stage1_output.json"
        if not stage1_file.exists():
            raise FileNotFoundError(f"Stage1数据文件不存在: {stage1_file}")
            
        with open(stage1_file, 'r', encoding='utf-8') as f:
            self.stage1_data = json.load(f)
            
        print(f"✅ 加载了 {len(self.stage1_data['scenes'])} 个场景的数据")
        print(f"   故事标题: {self.stage1_data['metadata']['story_title']}")
        print(f"   角色数量: {len(self.stage1_data['characters'])}")
        
    def assign_voice_mapping(self):
        """分配音色映射 - 使用 Stage4TTSService 的音色分配逻辑"""
        print("🎭 分配音色映射...")
        
        # 创建 Stage4TTSService 实例来使用其音色分配逻辑
        tts_service = Stage4TTSService()
        
        # 构建角色列表
        characters = []
        for char_data in self.stage1_data["characters"]:
            character = Character(
                id=char_data["id"],
                name=char_data["name"],
                description=char_data["description"],
                personality=char_data.get("personality", "")
            )
            characters.append(character)
        
        voice_mapping = {}
        
        # 使用 Stage4TTSService 的 _assign_voice 方法为每个角色分配音色
        for character in characters:
            voice = tts_service._assign_voice(character.id, characters, is_narration=False)
            voice_mapping[character.id] = voice
            print(f"   {character.name} ({character.id}) -> {voice}")
        
        # 添加旁白音色
        narrator_voice = tts_service._assign_voice(None, characters, is_narration=True)
        voice_mapping["narrator"] = narrator_voice
        print(f"   narrator -> {narrator_voice}")
        
        return voice_mapping
        
    async def generate_tts_audio(self):
        """生成TTS音频"""
        print("\n🎵 开始生成TTS音频...")
        
        # 分配音色
        voice_mapping = self.assign_voice_mapping()
        
        # 构建Stage1Output对象
        stage1_output = self._build_stage1_output()
        
        try:
            # 调用TTS服务生成音频
            result = await self.service.generate_all_audio(stage1_output, use_real_tts=True)
            
            print(f"✅ TTS音频生成成功!")
            print(f"   总时长: {result.total_video_duration}秒")
            print(f"   场景数量: {len(result.scenes)}")
            
            # 保存结果到文件
            self._save_stage4_output(result)
            
            return result
            
        except Exception as e:
            print(f"❌ TTS音频生成失败: {str(e)}")
            raise
            
    def _build_stage1_output(self):
        """构建Stage1Output对象"""
        # 构建角色列表
        characters = []
        for char_data in self.stage1_data["characters"]:
            character = Character(
                id=char_data["id"],
                name=char_data["name"],
                description=char_data["description"],
                personality=char_data.get("personality", "")
            )
            characters.append(character)
            
        # 构建场景列表
        scenes = []
        for scene_data in self.stage1_data["scenes"]:
            # 构建对话列表
            dialogues = []
            for dialogue_data in scene_data["dialogues"]:
                dialogue = Dialogue(
                    character=dialogue_data["character"],
                    text=dialogue_data["text"],
                    emotion=dialogue_data["emotion"]
                )
                dialogues.append(dialogue)
                
            scene = Scene(
                scene_id=scene_data["scene_id"],
                order=scene_data["order"],
                description=scene_data["description"],
                composition=scene_data["composition"],
                characters=scene_data["characters"],
                narration=scene_data["narration"],
                dialogues=dialogues
            )
            scenes.append(scene)
            
        return Stage1Output(
            metadata=self.stage1_data["metadata"],
            characters=characters,
            scenes=scenes
        )
        
    def _save_stage4_output(self, result: Stage4Output):
        """保存Stage4输出结果"""
        print("\n💾 保存Stage4输出结果...")
        
        # 转换为字典格式
        output_data = {
            "scenes": [],
            "total_video_duration": result.total_video_duration,
            "character_voices": result.character_voices
        }
        
        for scene in result.scenes:
            scene_data = {
                "scene_id": scene.scene_id,
                "audio_segments": [],
                "total_duration": scene.total_duration
            }
            
            for segment in scene.audio_segments:
                segment_data = {
                    "type": segment.type,
                    "text": segment.text,
                    "audio_path": segment.audio_path,
                    "duration": segment.duration,
                    "start_time": segment.start_time,
                    "voice": segment.voice
                }
                
                # 添加角色相关字段
                if segment.type == "dialogue":
                    segment_data["character"] = segment.character
                    segment_data["character_name"] = segment.character_name
                    segment_data["emotion"] = segment.emotion
                    
                scene_data["audio_segments"].append(segment_data)
                
            output_data["scenes"].append(scene_data)
            
        # 保存到文件
        output_file = self.output_dir / "stage4_output.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
            
        print(f"✅ Stage4输出已保存: {output_file}")
        
        # 显示统计信息
        self._show_generation_stats(output_data)
        
    def _show_generation_stats(self, output_data):
        """显示生成统计信息"""
        print("\n📊 生成统计信息:")
        
        total_segments = 0
        total_duration = 0
        narration_count = 0
        dialogue_count = 0
        
        for scene in output_data["scenes"]:
            total_duration += scene["total_duration"]
            for segment in scene["audio_segments"]:
                total_segments += 1
                if segment["type"] == "narration":
                    narration_count += 1
                elif segment["type"] == "dialogue":
                    dialogue_count += 1
                    
        print(f"   总场景数: {len(output_data['scenes'])}")
        print(f"   总音频段数: {total_segments}")
        print(f"   旁白段数: {narration_count}")
        print(f"   对话段数: {dialogue_count}")
        print(f"   总时长: {total_duration:.1f}秒")
        print(f"   音频文件目录: {self.audio_dir}")
        
    def verify_audio_files(self):
        """验证生成的音频文件"""
        print("\n🔍 验证生成的音频文件...")
        
        audio_files = list(self.audio_dir.glob("*.mp3"))
        print(f"   找到 {len(audio_files)} 个音频文件")
        
        total_size = 0
        for audio_file in audio_files:
            size = audio_file.stat().st_size
            total_size += size
            print(f"   {audio_file.name}: {size:,} bytes")
            
        print(f"   总文件大小: {total_size:,} bytes ({total_size/1024/1024:.2f} MB)")
        
    def cleanup(self):
        """清理测试环境"""
        print(f"\n🧹 清理测试环境...")
        
        if self.output_dir and self.output_dir.exists():
            response = input(f"是否删除输出目录 {self.output_dir}? (y/n): ").lower().strip()
            if response in ['y', 'yes', '是']:
                shutil.rmtree(self.output_dir)
                print(f"✅ 已清理输出目录: {self.output_dir}")
            else:
                print(f"💾 输出目录保留: {self.output_dir}")
                
    async def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始真实TTS音频生成测试")
        print("=" * 60)
        
        try:
            # 初始化
            if not self.setup():
                return
                
            # 生成TTS音频
            result = await self.generate_tts_audio()
            
            if result:
                # 验证音频文件
                self.verify_audio_files()
                
                print("\n" + "=" * 60)
                print("🎉 TTS音频生成测试完成!")
                print("✅ 所有音频文件生成成功!")
                print(f"📁 输出目录: {self.output_dir}")
                print("💡 提示: 可以播放生成的音频文件来验证效果")
            else:
                print("❌ TTS音频生成失败")
                
        except Exception as e:
            print(f"❌ 测试过程中发生错误: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            # 询问是否清理
            self.cleanup()


def main():
    """主函数"""
    print("🎵 真实TTS音频生成测试脚本")
    print("基于Stage4TTSService实现真实的音频生成功能")
    print("读取stage1输出数据，调用火山引擎TTS接口生成真实音频文件")
    print()
    
    # 运行测试
    tester = RealTTSGenerationTest()
    asyncio.run(tester.run_all_tests())


if __name__ == "__main__":
    main()
