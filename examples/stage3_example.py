import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app.services.stage1_text_analysis import Stage1TextAnalysisService
from backend.app.services.stage2_image_prompt import Stage2ImagePromptService
from backend.app.services.stage3_image_generation import Stage3ImageGenerationService


async def main():
    story_text = """
    这是一个平凡的早晨,张三走在上班的路上。
    阳光洒在高楼之间,他心想:"今天会是美好的一天。"
    突然,他遇到了老朋友李四。
    李四兴奋地说:"张三!好久不见!"他们决定去附近的咖啡店叙旧。
    """
    
    print("=== 阶段一：文本分析与分镜设计 ===")
    stage1_service = Stage1TextAnalysisService()
    stage1_output = await stage1_service.analyze_text(story_text, scenes_count=3)
    
    print(f"故事标题: {stage1_output.metadata.story_title}")
    print(f"角色数量: {stage1_output.metadata.total_characters}")
    print(f"场景数量: {stage1_output.metadata.total_scenes}")
    print()
    
    for character in stage1_output.characters:
        print(f"角色: {character.name} - {character.description}")
    print()
    
    print("=== 阶段二：图像提示词生成 ===")
    stage2_service = Stage2ImagePromptService()
    stage2_outputs = await stage2_service.generate_all_prompts(stage1_output)
    
    for i, output in enumerate(stage2_outputs, 1):
        print(f"\n场景 {i} ({output.scene_id}):")
        print(f"提示词: {output.image_prompt[:100]}...")
        print(f"负向提示词: {output.negative_prompt}")
    print()
    
    print("=== 阶段三：图像生成 ===")
    stage3_service = Stage3ImageGenerationService(output_dir="./output/images")
    
    print("开始生成图像...")
    stage3_outputs = await stage3_service.generate_all_images(
        stage2_outputs,
        size="1024x1024",
        quality="standard"
    )
    
    print(f"\n成功生成 {len(stage3_outputs)} 张图像:")
    for output in stage3_outputs:
        print(f"  - {output.scene_id}")
        print(f"    路径: {output.image_path}")
        print(f"    尺寸: {output.width}x{output.height}")
        print(f"    模型: {output.generation_params['model']}")
        print()
    
    print("=== 完成 ===")
    print(f"所有图像已保存到: ./output/images/")
    
    return stage3_outputs


if __name__ == "__main__":
    try:
        results = asyncio.run(main())
        print(f"\n总共生成了 {len(results)} 张图像")
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
