# Big Niu 测试流程总览

完整的文本到视频生成流程测试文档。

---

## 🎯 流程概览

```
原始文本
    ↓
[Stage1] 文本分析与场景分镜
    ↓ (scenes, characters, dialogues)
[Stage2] 图像提示词生成
    ↓ (image_prompts)
[Stage3] 图像生成
    ↓ (scene_images)
[Stage4] 语音合成（TTS）
    ↓ (audio_segments, subtitles)
[Stage5] 视频合成
    ↓
最终视频 MP4
```

---

## 📁 目录结构

```
tests/backend/
├── stage1/                     ✅ Stage1: 文本分析
│   ├── test_unit_text_analysis.py
│   ├── test_functional_text_analysis.py
│   ├── mock_input_threebody.txt
│   └── mock_input_journey.txt
│
├── stage2/                     ✅ Stage2: 提示词生成
│   ├── test_unit_image_generation.py
│   └── test_functional_image_generation.py
│
├── stage3/                     ✅ Stage3: 图像生成
│   ├── test_unit_image_generation.py
│   ├── test_functional_image_generation.py
│   ├── test_stage3.py
│   └── test_stage3_simple.py
│
├── stage4/                     🆕 Stage4: 语音合成
│   ├── test_unit_tts.py
│   ├── test_functional_tts.py
│   ├── README.md
│   └── mockdata/
│       ├── original_text.txt
│       ├── stage1_output.json
│       ├── stage3_output.json
│       ├── stage4_expected_output.json
│       ├── images/              # 来自 Stage3
│       │   ├── scene_001.png
│       │   ├── scene_002.png
│       │   └── scene_003.png
│       └── audio/               # TTS 生成的音频
│
├── stage5/                     🆕 Stage5: 视频合成
│   ├── test_unit_video_composition.py
│   ├── test_functional_video_composition.py
│   ├── README.md
│   └── mockdata/
│       ├── stage4_output.json
│       ├── expected_subtitles.srt
│       ├── images/              # 场景图像
│       ├── audio/               # 音频文件
│       ├── subtitles/           # 字幕文件
│       └── video/               # 最终视频
│
├── integration/                # 🔗 集成测试
│   ├── test_stages.py
│   └── quick_test.py
│
├── fixtures/                   # 💾 测试输出
│   ├── stage1_output.json
│   ├── stage2_output.json
│   ├── stage3_output.json
│   └── output/images/
│
├── debug/                      # 🐛 调试工具
│   ├── debug_image_gen.py
│   └── debug_image_gen2.py
│
├── docs/                       # 📚 文档
│   ├── TEST_GUIDE.md
│   ├── STAGE3_TEST_SUMMARY.md
│   └── STAGE3_OPTIMIZATION.md
│
├── run_all_tests.py            # 🚀 主测试运行器
├── quick_test.sh               # 📝 快速测试脚本
└── README.md                   # 📄 主文档
```

---

## 📊 各 Stage 详情

### Stage 1: 文本分析与场景分镜

**输入**: 原始故事文本
**输出**: 结构化场景、角色、对话

**测试状态**: ✅ 完成
- 单元测试：8个测试用例
- 功能测试：5个测试用例
- Mock数据：2个测试文本（三体、西游记）

**运行**:
```bash
pytest stage1/ -v
```

---

### Stage 2: 图像提示词生成

**输入**: Stage1 输出
**输出**: 英文图像提示词（Stable Diffusion/DALL-E格式）

**测试状态**: ✅ 完成
- 单元测试：6个测试用例
- 功能测试：4个测试用例

**运行**:
```bash
pytest stage2/ -v
```

---

### Stage 3: 图像生成

**输入**: Stage2 输出
**输出**: 场景图像（PNG, 1024x1024）

**测试状态**: ✅ 完成（支持并发）
- 单元测试：6个测试用例
- 功能测试：3个测试用例
- 自定义测试：2个测试脚本
- **并发优化**: 3张图 90秒 → 30秒 ⚡

**运行**:
```bash
pytest stage3/ -v
python stage3/test_stage3.py
```

**特性**:
- ✅ 并发生成（提升3-10倍速度）
- ✅ 支持多种图像模型
- ✅ 自动保存和管理

---

### Stage 4: 语音合成（TTS）

**输入**: Stage1 输出（旁白+对话）
**输出**: 音频文件（MP3）+ 时间轴信息

**测试状态**: 🆕 已创建框架
- 单元测试：框架已创建（待实现）
- 功能测试：框架已创建（待实现）
- Mock数据：完整

**Mock 数据**:
```
mockdata/
├── original_text.txt          # 原始文本
├── stage1_output.json         # 场景和对话
├── stage3_output.json         # 图像信息
├── stage4_expected_output.json # 预期输出
├── images/                    # 3张场景图
└── audio/                     # 生成的音频（待生成）
```

**待实现**:
- [ ] TTS 服务集成（OpenAI TTS / Azure TTS）
- [ ] 角色音色分配
- [ ] 情绪参数映射
- [ ] 音频时长估算

**运行**:
```bash
pytest stage4/ -v
```

---

### Stage 5: 视频合成

**输入**: Stage4 输出（图像+音频+时长）
**输出**: 最终视频（MP4）+ 字幕（SRT）

**测试状态**: ✅ 已有测试 + 🆕 Mock数据补充
- 单元测试：已存在
- 功能测试：已存在
- Mock数据：🆕 已补充完整

**Mock 数据**:
```
mockdata/
├── stage4_output.json         # 音频和时长信息
├── expected_subtitles.srt     # 预期字幕
├── images/                    # 场景图像
├── audio/                     # 音频文件
└── video/                     # 最终视频（待生成）
```

**待实现**:
- [ ] FFmpeg 包装器
- [ ] 字幕生成器
- [ ] 音频合并
- [ ] 视频拼接

**运行**:
```bash
pytest stage5/ -v
```

---

## 🧪 测试类型

### 1. 单元测试 (Unit Tests)

测试单个函数和类的功能。

```bash
pytest -k "test_unit" -v
```

### 2. 功能测试 (Functional Tests)

测试完整的功能流程。

```bash
pytest -k "test_functional" -v
```

### 3. 集成测试 (Integration Tests)

测试多个 Stage 的集成。

```bash
pytest integration/ -v
python integration/test_stages.py
```

---

## 🚀 快速开始

### 运行所有测试

```bash
cd tests/backend
python run_all_tests.py
```

### 运行单个 Stage

```bash
pytest stage1/ -v  # Stage1
pytest stage2/ -v  # Stage2
pytest stage3/ -v  # Stage3
pytest stage4/ -v  # Stage4
pytest stage5/ -v  # Stage5
```

### 交互式测试

```bash
./quick_test.sh
```

---

## 📈 测试覆盖率

| Stage | 单元测试 | 功能测试 | 集成测试 | Mock数据 | 状态 |
|-------|----------|----------|----------|----------|------|
| Stage1 | ✅ 8个 | ✅ 5个 | ✅ | ✅ 2份 | 完成 |
| Stage2 | ✅ 6个 | ✅ 4个 | ✅ | ✅ | 完成 |
| Stage3 | ✅ 6个 | ✅ 3个 | ✅ | ✅ | 完成 |
| Stage4 | 🆕 框架 | 🆕 框架 | ⬜ | ✅ 完整 | 待实现 |
| Stage5 | ✅ 已有 | ✅ 已有 | ⬜ | ✅ 完整 | 待实现 |

**总体覆盖率**: ~70%

---

## 📝 Mock 数据说明

### 数据流转

```
Stage1 Input (原始文本)
    ↓
Stage1 Output → Stage2 Input
    ↓
Stage2 Output → Stage3 Input
    ↓
Stage3 Output → Stage4 Input
    ↓
Stage4 Output → Stage5 Input
    ↓
Final Video
```

### Mock 数据位置

| Stage | Input Mock | Output Mock | 说明 |
|-------|------------|-------------|------|
| Stage1 | `mock_input_*.txt` | `fixtures/stage1_output.json` | 测试文本 |
| Stage2 | `fixtures/stage1_output.json` | `fixtures/stage2_output.json` | - |
| Stage3 | `fixtures/stage2_output.json` | `fixtures/stage3_output.json` + images | 图像文件 |
| Stage4 | `stage4/mockdata/stage1_output.json` | `stage4_expected_output.json` | 音频文件 |
| Stage5 | `stage5/mockdata/stage4_output.json` | `expected_subtitles.srt` | 视频文件 |

---

## 🎯 下一步计划

### 短期（1-2周）

- [ ] 实现 Stage4 TTS 服务
- [ ] 完善 Stage4 测试用例
- [ ] 实现 Stage5 FFmpeg 包装器
- [ ] 完善 Stage5 测试用例

### 中期（1个月）

- [ ] 添加 E2E 测试
- [ ] 实现性能测试
- [ ] 添加错误恢复机制
- [ ] 优化并发处理

### 长期（2-3个月）

- [ ] CI/CD 集成
- [ ] 自动化测试报告
- [ ] 性能基准测试
- [ ] 压力测试

---

## 🔧 开发指南

### 添加新测试

1. 在对应 Stage 目录创建测试文件
2. 编写测试用例
3. 准备 Mock 数据
4. 更新 README.md

### 运行特定测试

```bash
# 运行特定文件
pytest tests/backend/stage3/test_stage3.py -v

# 运行特定测试
pytest tests/backend/stage3/test_stage3.py::test_function_name -v

# 运行标记的测试
pytest -m "not slow" -v
```

---

## 📚 相关文档

- [README.md](README.md) - 主测试文档
- [QUICK_START.md](QUICK_START.md) - 快速开始
- [STRUCTURE.md](STRUCTURE.md) - 目录结构
- [docs/TEST_GUIDE.md](docs/TEST_GUIDE.md) - 详细测试指南
- [docs/STAGE3_OPTIMIZATION.md](docs/STAGE3_OPTIMIZATION.md) - Stage3 优化说明

### 各 Stage 文档

- [stage1/README.md](stage1/README.md) - Stage1 说明（如存在）
- [stage2/README.md](stage2/README.md) - Stage2 说明（如存在）
- [stage3/README.md](stage3/README.md) - Stage3 说明（如存在）
- [stage4/README.md](stage4/README.md) - Stage4 说明 ✅
- [stage5/README.md](stage5/README.md) - Stage5 说明 ✅

---

## 🎉 总结

### 已完成

- ✅ Stage1-3 完整测试
- ✅ Stage3 并发优化
- ✅ Stage4-5 Mock 数据准备
- ✅ 测试框架搭建
- ✅ 文档完善

### 进行中

- 🔄 Stage4 TTS 实现
- 🔄 Stage5 视频合成实现

### 待开始

- ⬜ E2E 测试
- ⬜ CI/CD 集成
- ⬜ 性能优化

---

**更新时间**: 2025-10-24  
**维护者**: Big Niu Team

🚀 **完整的测试流程已就绪！**
