# Big Niu 测试套件

本目录包含 Big Niu 项目的完整测试套件,按照文字生成视频的三个阶段组织。

## 测试结构

```
tests/
├── conftest.py                           # Pytest 配置和公共 fixtures
├── README.md                             # 本文件
└── backend/                              # 后端测试
    ├── stage1/                          # 阶段一:文本分析与分镜设计
    │   ├── test_unit_text_analysis.py       # 单元测试
    │   └── test_functional_text_analysis.py # 功能测试
    ├── stage2/                          # 阶段二:图像生成
    │   ├── test_unit_image_generation.py    # 单元测试
    │   └── test_functional_image_generation.py # 功能测试
    └── stage3/                          # 阶段三:视频合成
        ├── test_unit_video_composition.py   # 单元测试
        └── test_functional_video_composition.py # 功能测试
```

## 测试分类

### 阶段一:文本分析与分镜设计

#### 单元测试 (`test_unit_text_analysis.py`)
- 字符提取功能测试
- 对话提取功能测试
- 场景拆分逻辑测试
- 场景描述构建测试
- 角色ID分配测试
- 输出验证测试
- 构图生成测试
- 情感分析测试

#### 功能测试 (`test_functional_text_analysis.py`)
- 端到端文本分析流程测试
- 不同分镜数量配置测试
- 角色提取准确性测试
- 对话提取与说话人识别测试
- 场景描述生成测试
- 结构化输出验证测试
- 长文本处理测试
- 错误处理和重试机制测试

### 阶段二:图像生成

#### 单元测试 (`test_unit_image_generation.py`)
- 提示词构建测试
- 多角色提示词测试
- 风格标签应用测试
- 图像生成参数测试(seed, steps)
- 图像存储测试
- 角色参考图生成测试
- ControlNet 一致性测试
- 图像质量验证测试
- 缓存机制测试
- 降级方案测试

#### 功能测试 (`test_functional_image_generation.py`)
- 端到端图像生成流程测试
- 角色一致性跨场景测试
- 并行图像生成测试
- 不同风格图像生成测试
- 重试机制测试
- 存储集成测试
- 提示词优化测试
- 质量验证与重新生成测试
- ControlNet/LoRA 集成测试

### 阶段三:视频合成

#### 单元测试 (`test_unit_video_composition.py`)
- TTS 语音生成测试
- 情感语音生成测试
- 角色音色分配测试
- 音频合并测试
- 音频时长计算测试
- SRT 字幕生成测试
- 时间戳格式化测试
- 字幕同步测试
- FFmpeg 命令构建测试
- 视频验证测试
- 元数据提取测试
- 临时文件清理测试

#### 功能测试 (`test_functional_video_composition.py`)
- 端到端视频合成流程测试
- 全场景 TTS 生成测试
- 角色音色分配测试
- 字幕生成与时间同步测试
- 音频合并序列测试
- FFmpeg 视频合成测试
- 视频质量验证测试
- 进度跟踪测试
- 错误处理和重试测试
- 降级服务测试
- 存储上传测试
- 性能优化测试

## 运行测试

### 运行所有测试
```bash
pytest tests/
```

### 运行特定阶段的测试
```bash
# 阶段一测试
pytest tests/backend/stage1/

# 阶段二测试
pytest tests/backend/stage2/

# 阶段三测试
pytest tests/backend/stage3/
```

### 运行特定类型的测试
```bash
# 所有单元测试
pytest tests/ -k "unit"

# 所有功能测试
pytest tests/ -k "functional"
```

### 运行单个测试文件
```bash
pytest tests/backend/stage1/test_unit_text_analysis.py
```

### 带覆盖率报告
```bash
pytest tests/ --cov=app --cov-report=html
```

### 详细输出
```bash
pytest tests/ -v
```

### 并行运行测试
```bash
pytest tests/ -n auto
```

## 测试要求

### 依赖安装
```bash
pip install -r requirements-test.txt
```

### 主要测试依赖
- `pytest`: 测试框架
- `pytest-asyncio`: 异步测试支持
- `pytest-cov`: 代码覆盖率
- `pytest-xdist`: 并行测试
- `unittest.mock`: Mock 对象
- `Pillow`: 图像处理(用于测试)

## Mock 策略

所有测试使用 mock 对象模拟外部服务:

- **AI 模型服务**: GPT-4, 通义千问, Stable Diffusion, DALL-E
- **TTS 服务**: Azure TTS, 阿里云 TTS
- **存储服务**: 七牛云对象存储
- **缓存服务**: Redis
- **任务队列**: Celery
- **FFmpeg**: 视频处理命令

这样可以确保测试:
1. 快速执行,不依赖外部服务
2. 可靠且可重复
3. 不产生实际费用
4. 可离线运行

## 最佳实践

1. **测试隔离**: 每个测试应该独立,不依赖其他测试的状态
2. **使用 Fixtures**: 复用测试数据和 mock 对象
3. **清晰命名**: 测试函数名应清楚描述测试内容
4. **断言明确**: 使用清晰的断言消息
5. **覆盖边界情况**: 测试正常流程和错误情况
6. **异步测试**: 使用 `@pytest.mark.asyncio` 标记异步测试

## 持续集成

测试会在以下情况自动运行:
- Pull Request 提交时
- 合并到主分支时
- 定期计划任务

## 参考文档

- 设计文档: [docs/text-to-video-design.md](../docs/text-to-video-design.md)
- API 规范: [docs/api-spec.md](../docs/api-spec.md)
- 开发指南: [docs/dev-guide.md](../docs/dev-guide.md)
