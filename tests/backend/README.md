# Backend 测试文档

Big Niu 后端服务的完整测试套件。

---

## 📁 目录结构

```
tests/backend/
├── stage1/                          # Stage1 文本分析测试
│   ├── __init__.py
│   ├── test_unit_text_analysis.py        # 单元测试
│   ├── test_functional_text_analysis.py  # 功能测试
│   ├── mock_input_threebody.txt          # 测试数据：三体
│   └── mock_input_journey.txt            # 测试数据：西游记
│
├── stage2/                          # Stage2 提示词生成测试
│   ├── __init__.py
│   ├── test_unit_image_generation.py     # 单元测试
│   └── test_functional_image_generation.py # 功能测试
│
├── stage3/                          # Stage3 图像生成测试
│   ├── __init__.py
│   ├── test_unit_image_generation.py         # 单元测试
│   ├── test_functional_image_generation.py   # 功能测试
│   ├── test_stage3.py                        # 完整测试
│   ├── test_stage3_simple.py                 # 简化测试
│   ├── test_unit_video_composition.py        # 视频合成单元测试
│   └── test_functional_video_composition.py  # 视频合成功能测试
│
├── integration/                     # 集成测试
│   ├── test_stages.py                   # Stage1-3 集成测试
│   └── quick_test.py                    # 快速测试
│
├── fixtures/                        # 测试固件和输出
│   ├── stage1_output.json           # Stage1 输出示例
│   ├── stage2_output.json           # Stage2 输出示例
│   ├── stage3_output.json           # Stage3 输出示例
│   ├── full_response.json           # 完整 API 响应
│   └── output/                      # 生成的图像文件
│       └── images/
│           ├── scene_001.png
│           └── test_scene_001.png
│
├── debug/                           # 调试工具
│   ├── debug_image_gen.py           # 图像生成 API 调试
│   └── debug_image_gen2.py          # 图像生成响应调试
│
├── docs/                            # 测试文档
│   ├── TEST_GUIDE.md                # 测试指南
│   └── STAGE3_TEST_SUMMARY.md       # Stage3 测试总结
│
├── run_all_tests.py                 # 🚀 主测试运行器
├── conftest.py                      # Pytest 配置
└── README.md                        # 本文件
```

---

## 🚀 快速开始

### 运行完整测试流程

```bash
# 激活环境
conda activate big-niu-backend

# 运行所有 Stage 测试（推荐）
cd tests/backend
python run_all_tests.py
```

### 运行单个 Stage 测试

```bash
# Stage1: 文本分析
pytest stage1/test_functional_text_analysis.py -v

# Stage2: 提示词生成
pytest stage2/test_functional_image_generation.py -v

# Stage3: 图像生成
pytest stage3/test_functional_image_generation.py -v

# 或使用自定义测试脚本
python stage3/test_stage3_simple.py
```

### 运行集成测试

```bash
# 完整流程测试
python integration/test_stages.py

# 快速测试
python integration/quick_test.py
```

---

## 📋 测试流程说明

### Stage 1: 文本分析与场景分镜

**功能**: 将故事文本分析成结构化的场景、角色和对话

**输入**:
```python
story_text = "这是一个平凡的早晨..."
scenes_count = 3
```

**输出**: `stage1_output.json`
```json
{
  "metadata": {
    "story_title": "故事标题",
    "total_scenes": 3,
    "total_characters": 2
  },
  "characters": [...],
  "scenes": [...]
}
```

**测试文件**:
- `stage1/test_unit_text_analysis.py` - 单元测试
- `stage1/test_functional_text_analysis.py` - 功能测试

---

### Stage 2: 图像提示词生成

**功能**: 为每个场景生成详细的英文图像提示词

**输入**: Stage1 的输出
**输出**: `stage2_output.json`

```json
{
  "prompts": [
    {
      "scene_id": "scene_001",
      "image_prompt": "A detailed description...",
      "negative_prompt": "low quality, blurry...",
      "style_tags": ["anime", "high_quality"],
      "characters_in_scene": ["char_001"]
    }
  ]
}
```

**测试文件**:
- `stage2/test_unit_image_generation.py` - 单元测试
- `stage2/test_functional_image_generation.py` - 功能测试

---

### Stage 3: 图像生成

**功能**: 使用 GPT-5 Image Mini 从提示词生成实际图像

**输入**: Stage2 的输出
**输出**: 
- PNG 图像文件
- `stage3_output.json` (元数据)

```json
{
  "scene_id": "scene_001",
  "image_path": "/path/to/scene_001.png",
  "width": 1024,
  "height": 1024,
  "generation_params": {...}
}
```

**测试文件**:
- `stage3/test_unit_image_generation.py` - 单元测试
- `stage3/test_functional_image_generation.py` - 功能测试
- `stage3/test_stage3.py` - 完整测试（使用 Stage2 输出）
- `stage3/test_stage3_simple.py` - 简化测试（独立运行）

---

## 🧪 测试类型

### 1. 单元测试 (Unit Tests)

测试单个函数和类的功能。

```bash
# 运行所有单元测试
pytest -k "test_unit" -v
```

### 2. 功能测试 (Functional Tests)

测试完整的功能流程。

```bash
# 运行所有功能测试
pytest -k "test_functional" -v
```

### 3. 集成测试 (Integration Tests)

测试多个 Stage 的集成。

```bash
# 运行集成测试
pytest integration/ -v
```

---

## 🔧 调试工具

### 图像生成 API 调试

```bash
# 调试图像生成 API
python debug/debug_image_gen.py

# 查看完整响应结构
python debug/debug_image_gen2.py
```

这些工具用于：
- 测试 OpenRouter API 连接
- 查看 API 响应格式
- 调试图像提取逻辑

---

## 📊 测试输出

### Fixtures 目录

所有测试输出都保存在 `fixtures/` 目录下：

- **JSON 文件**: 各 Stage 的结构化输出
- **images/**: 生成的图像文件
- **full_response.json**: 完整的 API 响应（用于调试）

### 清理输出

```bash
# 清理所有生成的文件
rm -rf fixtures/output/
rm fixtures/*.json
```

---

## 📝 编写新测试

### 1. 创建测试文件

```python
# tests/backend/stageX/test_my_feature.py

import pytest
from backend.app.services.my_service import MyService


@pytest.mark.asyncio
async def test_my_feature():
    """测试我的功能"""
    service = MyService()
    result = await service.do_something()
    
    assert result is not None
    assert result.success == True
```

### 2. 使用 Fixtures

```python
@pytest.fixture
async def stage1_output():
    """Stage1 输出 fixture"""
    # 读取或生成 stage1 输出
    ...
    return output


async def test_with_fixture(stage1_output):
    """使用 fixture 的测试"""
    assert stage1_output is not None
```

### 3. 运行新测试

```bash
pytest tests/backend/stageX/test_my_feature.py -v
```

---

## ⚙️ 配置

### 环境变量

测试需要以下环境变量（在 `backend/.env` 中配置）:

```env
OPENROUTER_API_KEY=sk-or-v1-***
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
TEXT_ANALYSIS_MODEL=x-ai/grok-code-fast-1
IMAGE_PROMPT_MODEL=x-ai/grok-code-fast-1
IMAGE_GENERATION_MODEL=openai/gpt-5-image-mini
```

### Pytest 配置

参见 `conftest.py` 和根目录的 `pytest.ini`

---

## 📚 相关文档

- [TEST_GUIDE.md](docs/TEST_GUIDE.md) - 详细测试指南
- [STAGE3_TEST_SUMMARY.md](docs/STAGE3_TEST_SUMMARY.md) - Stage3 测试总结
- [../README.md](../README.md) - 项目总体测试文档

---

## 🐛 常见问题

### Q: 测试失败怎么办？

1. 检查环境变量配置
2. 确认 API Key 有效
3. 查看详细错误日志
4. 运行调试脚本 `debug/debug_image_gen.py`

### Q: 如何跳过某些测试？

```bash
# 跳过耗时的测试
pytest -m "not slow"

# 只运行快速测试
pytest -m "quick"
```

### Q: 测试输出在哪里？

所有测试输出保存在 `fixtures/` 目录下，不会提交到 git。

---

## 🎯 最佳实践

1. **运行测试前**: 确保后端服务已启动
2. **成本控制**: Stage3 图像生成有成本，测试时只生成必要的图像
3. **清理输出**: 定期清理 `fixtures/output/` 目录
4. **文档更新**: 添加新功能时同步更新测试文档
5. **CI/CD**: 配置自动化测试流程（未来）

---

## 📞 支持

如有问题，请查看:
- [项目 README](../../README.md)
- [后端文档](../../backend/README.md)
- Issue Tracker (GitHub)

---

**Happy Testing! 🎉**
