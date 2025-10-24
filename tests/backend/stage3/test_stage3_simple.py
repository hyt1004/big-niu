#!/usr/bin/env python3
"""
简化的 Stage3 测试 - 使用短提示词
"""

import asyncio
from pathlib import Path
from app.services.stage3_image_generation import Stage3ImageGenerationService
from app.models.schemas import Stage2Output


async def test_simple():
    """使用简短提示词测试"""
    
    print("=" * 60)
    print("Stage3 简化测试 - 使用短提示词")
    print("=" * 60)
    
    # 创建一个简单的 Stage2Output
    stage2_output = Stage2Output(
        scene_id="test_scene_001",
        image_prompt="A cute cat sitting on a red chair, anime style, high quality",
        negative_prompt="blurry, low quality",
        style_tags=["anime", "high_quality"],
        characters_in_scene=[]
    )
    
    output_dir = Path(__file__).parent / "output" / "images"
    stage3_service = Stage3ImageGenerationService(output_dir=str(output_dir))
    
    print(f"\n📁 图像保存目录: {output_dir}")
    print(f"🎨 场景 ID: {stage2_output.scene_id}")
    print(f"📝 提示词: {stage2_output.image_prompt}")
    print(f"\n⏳ 正在生成图像...")
    
    try:
        result = await stage3_service.generate_scene_image(
            stage2_output=stage2_output,
            size="1024x1024",
            quality="standard"
        )
        
        print(f"\n✅ 图像生成成功!")
        print(f"场景 ID: {result.scene_id}")
        print(f"图像路径: {result.image_path}")
        print(f"图像尺寸: {result.width}x{result.height}")
        print(f"生成模型: {result.generation_params['model']}")
        
        return result
        
    except Exception as e:
        print(f"\n❌ 图像生成失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    result = asyncio.run(test_simple())
    
    print("\n" + "=" * 60)
    if result:
        print("✅ 测试成功!")
        print(f"查看图像: {result.image_path}")
    else:
        print("❌ 测试失败")
    print("=" * 60)
