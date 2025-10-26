"""
任务编排器 - 管理完整的 Stage1->5 视频生成流程
"""

import os
import json
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import uuid4

from app.services.stage1_text_analysis import Stage1TextAnalysisService
from app.services.stage2_image_prompt import Stage2ImagePromptService
from app.services.stage3_image_generation import Stage3ImageGenerationService
from app.services.stage4_tts import Stage4TTSService
from app.services.stage5_video_composition import Stage5VideoCompositionService


class TaskOrchestrator:
    """
    任务编排器 - 协调整个视频生成流程
    
    完整流程：
    原始文本 → Stage1 → Stage2 → Stage3 → Stage4 → Stage5 → 最终视频
    """
    
    def __init__(self, output_base_dir: str = "./output/tasks"):
        """
        初始化任务编排器
        
        Args:
            output_base_dir: 任务输出的基础目录
        """
        self.output_base_dir = Path(output_base_dir)
        self.output_base_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化各个阶段的服务
        self.stage1_service = Stage1TextAnalysisService()
        self.stage2_service = Stage2ImagePromptService()
        # stage3, stage4, stage5 会在任务执行时初始化（需要指定输出目录）
    
    def create_task(self, task_name: Optional[str] = None) -> str:
        """
        创建新任务，生成唯一的 task_id 和目录结构
        
        Args:
            task_name: 任务名称（可选）
            
        Returns:
            task_id: 任务唯一标识符
        """
        # 生成唯一的 task_id
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid4())[:8]
        task_id = f"task_{timestamp}_{unique_id}"
        
        # 创建任务目录结构
        task_dir = self.output_base_dir / task_id
        task_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建子目录
        (task_dir / "stage1").mkdir(exist_ok=True)
        (task_dir / "stage2").mkdir(exist_ok=True)
        (task_dir / "stage3" / "images").mkdir(parents=True, exist_ok=True)
        (task_dir / "stage4" / "audio").mkdir(parents=True, exist_ok=True)
        (task_dir / "stage5" / "subtitles").mkdir(parents=True, exist_ok=True)
        (task_dir / "stage5" / "video").mkdir(parents=True, exist_ok=True)
        
        # 保存任务元数据
        metadata = {
            "task_id": task_id,
            "task_name": task_name or task_id,
            "created_at": datetime.now().isoformat(),
            "status": "created",
            "stages": {}
        }
        
        self._save_metadata(task_id, metadata)
        
        print(f"✅ 任务创建成功: {task_id}")
        print(f"📁 输出目录: {task_dir}")
        
        return task_id
    
    def _get_task_dir(self, task_id: str) -> Path:
        """获取任务目录"""
        return self.output_base_dir / task_id
    
    def _save_metadata(self, task_id: str, metadata: Dict[str, Any]):
        """保存任务元数据"""
        task_dir = self._get_task_dir(task_id)
        metadata_file = task_dir / "task_metadata.json"
        
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    def _load_metadata(self, task_id: str) -> Dict[str, Any]:
        """加载任务元数据"""
        task_dir = self._get_task_dir(task_id)
        metadata_file = task_dir / "task_metadata.json"
        
        with open(metadata_file, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def _update_stage_status(self, task_id: str, stage: str, status: str, **kwargs):
        """更新阶段状态"""
        metadata = self._load_metadata(task_id)
        metadata["stages"][stage] = {
            "status": status,
            "updated_at": datetime.now().isoformat(),
            **kwargs
        }
        self._save_metadata(task_id, metadata)
    
    async def run_task(
        self,
        text: str,
        scenes_count: int = 3,
        task_name: Optional[str] = None,
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        运行完整的视频生成任务
        
        Args:
            text: 原始故事文本
            scenes_count: 要生成的场景数量
            task_name: 任务名称
            task_id: 已有的任务ID（可选，如果不提供则创建新任务）
            
        Returns:
            任务结果字典，包含所有阶段的输出路径和元数据
        """
        # 创建或使用已有任务
        if task_id is None:
            task_id = self.create_task(task_name)
        
        task_dir = self._get_task_dir(task_id)
        
        print(f"\n{'='*60}")
        print(f"🚀 开始执行任务: {task_id}")
        print(f"{'='*60}\n")
        
        try:
            # ========== Stage 1: 文本分析与场景分镜 ==========
            print("📖 Stage 1: 文本分析与场景分镜")
            self._update_stage_status(task_id, "stage1", "running")
            
            # 保存原始输入
            input_file = task_dir / "stage1" / "input.txt"
            with open(input_file, "w", encoding="utf-8") as f:
                f.write(text)
            
            stage1_output = await self.stage1_service.analyze_text(text, scenes_count)
            
            # 保存 Stage1 输出
            stage1_output_file = task_dir / "stage1" / "output.json"
            with open(stage1_output_file, "w", encoding="utf-8") as f:
                json.dump(stage1_output.model_dump(), f, ensure_ascii=False, indent=2)
            
            self._update_stage_status(
                task_id, "stage1", "completed",
                output_file=str(stage1_output_file),
                scenes_count=stage1_output.metadata.total_scenes,
                characters_count=stage1_output.metadata.total_characters
            )
            
            print(f"✅ Stage 1 完成: {stage1_output.metadata.total_scenes} 个场景, "
                  f"{stage1_output.metadata.total_characters} 个角色")
            
            # ========== Stage 2: 图像提示词生成 ==========
            print("\n🎨 Stage 2: 图像提示词生成")
            self._update_stage_status(task_id, "stage2", "running")
            
            stage2_outputs = await self.stage2_service.generate_all_prompts(stage1_output)
            
            # 保存 Stage2 输出
            stage2_output_file = task_dir / "stage2" / "output.json"
            with open(stage2_output_file, "w", encoding="utf-8") as f:
                json.dump({
                    "prompts": [p.model_dump() for p in stage2_outputs]
                }, f, ensure_ascii=False, indent=2)
            
            self._update_stage_status(
                task_id, "stage2", "completed",
                output_file=str(stage2_output_file),
                prompts_count=len(stage2_outputs)
            )
            
            print(f"✅ Stage 2 完成: {len(stage2_outputs)} 个图像提示词")
            
            # ========== Stage 3: 图像生成 ==========
            print("\n🖼️  Stage 3: 图像生成（并发模式）")
            self._update_stage_status(task_id, "stage3", "running")
            
            import time
            start_time = time.time()
            
            # 初始化 Stage3 服务（指定输出目录）
            images_dir = task_dir / "stage3" / "images"
            stage3_service = Stage3ImageGenerationService(output_dir=str(images_dir))
            
            # 并发生成所有图像
            # 从环境变量读取图像生成模型（如果未设置则使用默认值）
            import os
            image_model = os.getenv("IMAGE_GENERATION_MODEL", "openai/gpt-5-image-mini")
            
            stage3_outputs = await stage3_service.generate_all_images(
                stage2_outputs=stage2_outputs,
                concurrent=True,  # 并发模式
                model=image_model  # 使用配置的模型
            )
            
            elapsed = time.time() - start_time
            
            # 保存 Stage3 输出
            stage3_output_file = task_dir / "stage3" / "output.json"
            with open(stage3_output_file, "w", encoding="utf-8") as f:
                json.dump({
                    "total_images": len(stage3_outputs),
                    "elapsed_seconds": elapsed,
                    "images": [img.model_dump() for img in stage3_outputs]
                }, f, ensure_ascii=False, indent=2)
            
            self._update_stage_status(
                task_id, "stage3", "completed",
                output_file=str(stage3_output_file),
                images_count=len(stage3_outputs),
                elapsed_seconds=elapsed
            )
            
            print(f"✅ Stage 3 完成: {len(stage3_outputs)} 张图像, 耗时 {elapsed:.1f} 秒")
            
            # ========== Stage 4: 语音合成（TTS） ==========
            print("\n🎤 Stage 4: 语音合成（TTS）")
            self._update_stage_status(task_id, "stage4", "running")
            
            start_time = time.time()
            
            # 初始化 Stage4 服务
            audio_dir = task_dir / "stage4" / "audio"
            stage4_service = Stage4TTSService(output_dir=str(audio_dir))
            
            # 生成所有场景的音频
            stage4_outputs = await stage4_service.generate_all_scenes_audio(
                scenes=stage1_output.scenes,
                characters=stage1_output.characters
            )
            
            elapsed = time.time() - start_time
            
            # 保存 Stage4 输出
            stage4_output_file = task_dir / "stage4" / "output.json"
            with open(stage4_output_file, "w", encoding="utf-8") as f:
                json.dump({
                    "scenes": [s.model_dump() for s in stage4_outputs],
                    "total_duration": sum(s.total_duration for s in stage4_outputs),
                    "elapsed_seconds": elapsed
                }, f, ensure_ascii=False, indent=2)
            
            total_audio_duration = sum(s.total_duration for s in stage4_outputs)
            
            self._update_stage_status(
                task_id, "stage4", "completed",
                output_file=str(stage4_output_file),
                scenes_count=len(stage4_outputs),
                total_duration=total_audio_duration,
                elapsed_seconds=elapsed
            )
            
            print(f"✅ Stage 4 完成: {len(stage4_outputs)} 个场景音频, "
                  f"总时长 {total_audio_duration:.1f} 秒, 耗时 {elapsed:.1f} 秒")
            
            # ========== Stage 5: 视频合成 ==========
            print("\n🎬 Stage 5: 视频合成")
            self._update_stage_status(task_id, "stage5", "running")
            
            start_time = time.time()
            
            # 初始化 Stage5 服务
            subtitles_dir = task_dir / "stage5" / "subtitles"
            video_dir = task_dir / "stage5" / "video"
            stage5_service = Stage5VideoCompositionService(
                subtitles_dir=str(subtitles_dir),
                video_dir=str(video_dir)
            )
            
            # 准备视频合成输入
            video_input = {
                "scenes": []
            }
            
            for i, (scene, stage3_img, stage4_audio) in enumerate(
                zip(stage1_output.scenes, stage3_outputs, stage4_outputs)
            ):
                video_input["scenes"].append({
                    "scene_id": scene.scene_id,
                    "image_path": stage3_img.image_path,
                    "audio_segments": [seg.model_dump() for seg in stage4_audio.audio_segments],
                    "total_duration": stage4_audio.total_duration
                })
            
            # 生成视频
            stage5_output = await stage5_service.compose_video(video_input)
            
            elapsed = time.time() - start_time
            
            # 保存 Stage5 输出
            stage5_output_file = task_dir / "stage5" / "output.json"
            with open(stage5_output_file, "w", encoding="utf-8") as f:
                json.dump({
                    **stage5_output.model_dump(),
                    "elapsed_seconds": elapsed
                }, f, ensure_ascii=False, indent=2)
            
            self._update_stage_status(
                task_id, "stage5", "completed",
                output_file=str(stage5_output_file),
                video_path=stage5_output.video_path,
                duration=stage5_output.duration,
                elapsed_seconds=elapsed
            )
            
            print(f"✅ Stage 5 完成: 视频已生成, 时长 {stage5_output.duration:.1f} 秒, "
                  f"耗时 {elapsed:.1f} 秒")
            
            # ========== 任务完成 ==========
            metadata = self._load_metadata(task_id)
            metadata["status"] = "completed"
            metadata["completed_at"] = datetime.now().isoformat()
            metadata["final_output"] = {
                "video_path": stage5_output.video_path,
                "subtitle_path": stage5_output.subtitle_path,
                "duration": stage5_output.duration
            }
            self._save_metadata(task_id, metadata)
            
            print(f"\n{'='*60}")
            print(f"🎉 任务完成: {task_id}")
            print(f"📹 视频路径: {stage5_output.video_path}")
            print(f"📄 字幕路径: {stage5_output.subtitle_path}")
            print(f"⏱️  视频时长: {stage5_output.duration:.1f} 秒")
            print(f"{'='*60}\n")
            
            return {
                "task_id": task_id,
                "status": "completed",
                "task_dir": str(task_dir),
                "stages": {
                    "stage1": {
                        "output_file": str(stage1_output_file),
                        "scenes_count": stage1_output.metadata.total_scenes
                    },
                    "stage2": {
                        "output_file": str(stage2_output_file),
                        "prompts_count": len(stage2_outputs)
                    },
                    "stage3": {
                        "output_file": str(stage3_output_file),
                        "images_count": len(stage3_outputs)
                    },
                    "stage4": {
                        "output_file": str(stage4_output_file),
                        "total_duration": total_audio_duration
                    },
                    "stage5": {
                        "output_file": str(stage5_output_file),
                        "video_path": stage5_output.video_path,
                        "subtitle_path": stage5_output.subtitle_path
                    }
                },
                "final_output": {
                    "video_path": stage5_output.video_path,
                    "subtitle_path": stage5_output.subtitle_path,
                    "duration": stage5_output.duration
                }
            }
            
        except Exception as e:
            # 任务失败
            print(f"\n❌ 任务失败: {str(e)}")
            
            metadata = self._load_metadata(task_id)
            metadata["status"] = "failed"
            metadata["error"] = str(e)
            metadata["failed_at"] = datetime.now().isoformat()
            self._save_metadata(task_id, metadata)
            
            raise
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        获取任务状态
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务状态信息
        """
        return self._load_metadata(task_id)
    
    def list_tasks(self) -> list:
        """
        列出所有任务
        
        Returns:
            任务列表
        """
        tasks = []
        for task_dir in self.output_base_dir.iterdir():
            if task_dir.is_dir() and task_dir.name.startswith("task_"):
                try:
                    metadata = self._load_metadata(task_dir.name)
                    tasks.append({
                        "task_id": task_dir.name,
                        "task_name": metadata.get("task_name"),
                        "status": metadata.get("status"),
                        "created_at": metadata.get("created_at")
                    })
                except:
                    pass
        
        return sorted(tasks, key=lambda x: x["created_at"], reverse=True)
