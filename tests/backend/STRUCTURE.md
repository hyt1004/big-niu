# 测试目录结构

```
tests/backend/
│
├── 📄 README.md                    # 测试文档主页
├── 📄 STRUCTURE.md                 # 本文件 - 目录结构说明
├── 🚀 run_all_tests.py            # 主测试运行器（Python）
├── 🚀 quick_test.sh               # 快速测试脚本（Shell）
├── 📄 .gitignore                   # Git 忽略配置
├── 📄 __init__.py
│
├── 📁 stage1/                      # ✅ Stage 1: 文本分析与场景分镜
│   ├── __init__.py
│   ├── test_unit_text_analysis.py        # 单元测试
│   ├── test_functional_text_analysis.py  # 功能测试
│   ├── mock_input_threebody.txt          # 测试数据：三体
│   └── mock_input_journey.txt            # 测试数据：西游记
│
├── 📁 stage2/                      # ✅ Stage 2: 图像提示词生成
│   ├── __init__.py
│   ├── test_unit_image_generation.py     # 单元测试
│   └── test_functional_image_generation.py # 功能测试
│
├── 📁 stage3/                      # ✅ Stage 3: 图像生成
│   ├── __init__.py
│   ├── test_unit_image_generation.py         # 单元测试
│   ├── test_functional_image_generation.py   # 功能测试
│   ├── test_stage3.py                        # 完整测试（使用 Stage2 输出）
│   ├── test_stage3_simple.py                 # 简化测试（独立运行）
│   ├── test_unit_video_composition.py        # 视频合成单元测试
│   └── test_functional_video_composition.py  # 视频合成功能测试
│
├── 📁 integration/                 # 🔗 集成测试
│   ├── test_stages.py              # Stage1-3 完整流程测试
│   └── quick_test.py               # 快速集成测试
│
├── 📁 fixtures/                    # 💾 测试固件和输出（不提交到 git）
│   ├── stage1_output.json          # Stage1 输出示例
│   ├── stage2_output.json          # Stage2 输出示例
│   ├── stage3_output.json          # Stage3 输出示例
│   ├── full_response.json          # 完整 API 响应（调试用）
│   ├── stage1/                     # Stage1 固件目录
│   ├── stage2/                     # Stage2 固件目录
│   ├── stage3/                     # Stage3 固件目录
│   └── output/                     # 生成的输出文件
│       └── images/                 # 生成的图像
│           ├── scene_001.png
│           └── test_scene_001.png
│
├── 📁 debug/                       # 🐛 调试工具
│   ├── debug_image_gen.py          # 图像生成 API 调试
│   └── debug_image_gen2.py         # 图像生成响应解析调试
│
└── 📁 docs/                        # 📚 测试文档
    ├── TEST_GUIDE.md               # 测试指南
    └── STAGE3_TEST_SUMMARY.md      # Stage3 测试总结
```

---

## 📋 目录说明

### 核心文件

| 文件 | 说明 |
|------|------|
| `run_all_tests.py` | Python 主测试运行器，运行完整 Stage1-3 流程 |
| `quick_test.sh` | Shell 快速测试脚本，提供交互式测试选择 |
| `README.md` | 测试文档主页，包含完整使用说明 |

### Stage 目录

每个 Stage 目录包含：
- **单元测试** (`test_unit_*.py`): 测试单个函数和类
- **功能测试** (`test_functional_*.py`): 测试完整功能流程
- **测试数据**: Stage1 包含测试文本文件

### Integration 目录

包含跨 Stage 的集成测试，验证完整工作流。

### Fixtures 目录

存放测试输出和固件：
- **.json 文件**: 各 Stage 的结构化输出
- **output/**: 生成的图像等文件
- **不提交到 git**: 通过 .gitignore 排除

### Debug 目录

调试工具脚本，用于：
- 测试 API 连接
- 查看响应格式
- 调试错误

### Docs 目录

测试相关文档，包括：
- 详细测试指南
- Stage 测试总结
- 最佳实践

---

## 🎯 使用流程

### 1. 运行完整测试

```bash
# 方法 1: Python 脚本（推荐）
cd tests/backend
python run_all_tests.py

# 方法 2: Shell 脚本
./quick_test.sh
# 选择 1 - 运行完整流程测试
```

### 2. 运行单个 Stage

```bash
# Stage1
pytest stage1/ -v

# Stage2
pytest stage2/ -v

# Stage3
pytest stage3/ -v
```

### 3. 运行集成测试

```bash
# 完整集成测试
python integration/test_stages.py

# 快速测试
python integration/quick_test.py
```

### 4. 调试问题

```bash
# 调试图像生成 API
python debug/debug_image_gen.py

# 查看完整响应
python debug/debug_image_gen2.py
```

---

## 📊 测试输出位置

所有测试输出保存在 `fixtures/` 目录：

```
fixtures/
├── stage1_output.json      # Stage1 分析结果
├── stage2_output.json      # Stage2 提示词
├── stage3_output.json      # Stage3 图像元数据
└── output/
    └── images/
        ├── scene_001.png   # 生成的场景图像
        └── *.png
```

---

## 🔄 测试数据流

```
[测试文本]
    ↓
[Stage1] → stage1_output.json
    ↓
[Stage2] → stage2_output.json
    ↓
[Stage3] → scene_*.png + stage3_output.json
```

---

## ⚙️ 配置文件

测试使用的配置文件：

| 文件 | 位置 | 说明 |
|------|------|------|
| `.env` | `backend/.env` | 环境变量配置 |
| `conftest.py` | `tests/` | Pytest 配置 |
| `.gitignore` | `tests/backend/` | 忽略测试输出 |

---

## 🎨 测试类型

| 类型 | 命名 | 示例 |
|------|------|------|
| 单元测试 | `test_unit_*.py` | `test_unit_text_analysis.py` |
| 功能测试 | `test_functional_*.py` | `test_functional_image_generation.py` |
| 集成测试 | `test_*.py` (in integration/) | `test_stages.py` |
| 自定义测试 | `test_*.py` | `test_stage3.py` |

---

## 📝 添加新测试

1. **创建测试文件**: 在相应的 Stage 目录下
2. **编写测试**: 使用 pytest 或自定义脚本
3. **更新文档**: 在 README.md 中添加说明
4. **运行测试**: 验证功能

---

## 🧹 清理输出

```bash
# 清理所有测试输出
rm -rf fixtures/output/
rm fixtures/*.json

# 或使用 git clean（谨慎使用）
git clean -fdx fixtures/
```

---

**更新时间**: 2025-10-24
**维护者**: Big Niu Team
