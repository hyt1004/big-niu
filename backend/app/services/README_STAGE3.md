# 阶段三：图像生成服务

## 概述

阶段三服务负责根据阶段二生成的图像提示词，调用 DALL-E 3 模型生成实际的图像文件，并保存到本地。

## 功能特性

- 调用 OpenRouter API 访问 DALL-E 3 模型
- 根据 Stage2Output 提示词生成图像
- 自动下载生成的图像并保存为 PNG 格式
- 支持批量生成多个场景图像
- 记录图像生成参数便于复现

## 使用方法

### 基本用法

```python
from app.services.stage3_image_generation import Stage3ImageGenerationService
from app.models.schemas import Stage2Output

service = Stage3ImageGenerationService(output_dir="./output/images")

stage2_output = Stage2Output(
    scene_id="scene_001",
    image_prompt="A beautiful morning cityscape...",
    negative_prompt="low quality, blurry",
    style_tags=["anime"],
    characters_in_scene=["char_001"]
)

result = await service.generate_scene_image(stage2_output)

print(f"Image saved to: {result.image_path}")
print(f"Dimensions: {result.width}x{result.height}")
```

### 批量生成

```python
stage2_outputs = [...]  # List of Stage2Output

results = await service.generate_all_images(stage2_outputs)

for result in results:
    print(f"{result.scene_id}: {result.image_path}")
```

### 自定义参数

```python
result = await service.generate_scene_image(
    stage2_output=stage2_output,
    size="1792x1024",  # 支持: 1024x1024, 1792x1024, 1024x1792
    quality="hd"       # 支持: standard, hd
)
```

## 输出格式

### Stage3Output

```python
{
    "scene_id": "scene_001",
    "image_path": "./output/images/scene_001.png",
    "image_url": None,  # 可选，如果上传到 CDN
    "width": 1024,
    "height": 1024,
    "generation_params": {
        "model": "dall-e-3",
        "size": "1024x1024",
        "quality": "standard",
        "prompt": "完整的提示词..."
    }
}
```

## 配置要求

### 环境变量

在 `.env` 文件中设置：

```env
OPENROUTER_API_KEY=your_api_key_here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
```

### 依赖包

```yaml
- pillow==11.0.0
- httpx==0.28.1
```

## 完整流程示例

```python
from app.services.stage1_text_analysis import Stage1TextAnalysisService
from app.services.stage2_image_prompt import Stage2ImagePromptService
from app.services.stage3_image_generation import Stage3ImageGenerationService

async def generate_story_images(story_text: str):
    stage1_service = Stage1TextAnalysisService()
    stage1_output = await stage1_service.analyze_text(story_text, scenes_count=5)
    
    stage2_service = Stage2ImagePromptService()
    stage2_outputs = await stage2_service.generate_all_prompts(stage1_output)
    
    stage3_service = Stage3ImageGenerationService(output_dir="./output/images")
    stage3_outputs = await stage3_service.generate_all_images(stage2_outputs)
    
    print(f"Generated {len(stage3_outputs)} images")
    for output in stage3_outputs:
        print(f"  - {output.scene_id}: {output.image_path}")
    
    return stage3_outputs
```

## 注意事项

1. **API 限制**: DALL-E 3 每次请求生成一张图片，批量生成时注意 API 速率限制
2. **成本控制**: DALL-E 3 调用需要付费，建议在测试时使用较小的场景数量
3. **存储空间**: 每张 1024x1024 的 PNG 图片约 1-3 MB，请确保有足够的磁盘空间
4. **超时设置**: 图像生成通常需要 10-30 秒，已设置 120 秒超时
5. **错误处理**: 如果生成失败，会抛出异常，建议在生产环境中添加重试逻辑

## 测试

运行单元测试：
```bash
pytest tests/backend/stage3/test_unit_image_generation.py -v
```

运行功能测试：
```bash
pytest tests/backend/stage3/test_functional_image_generation.py -v
```

## 未来扩展

- [ ] 支持 Stable Diffusion XL 作为备选模型
- [ ] 实现图像缓存，避免重复生成
- [ ] 添加角色一致性支持（ControlNet/LoRA）
- [ ] 自动上传到七牛云 CDN
- [ ] 支持并行生成以提高速度
- [ ] 添加图像质量验证和自动重试
