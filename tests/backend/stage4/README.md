# Stage4 语音合成（TTS）测试

## 功能描述

Stage4 负责将场景的旁白和角色对话转换为语音音频文件，使用火山引擎 TTS 服务提供高质量的语音合成。

---

## 📁 Mock 数据结构

```
stage4/mockdata/
├── original_text.txt              # 原始故事文本
├── stage1_output.json             # Stage1 输出（场景、角色、对话）
├── stage3_output.json             # Stage3 输出（图像信息）
├── stage4_expected_output.json    # 预期输出（用于测试对比）
├── images/                        # 场景图像（来自 Stage3）
│   ├── scene_001.png
│   ├── scene_002.png
│   └── scene_003.png
└── audio/                         # 生成的音频文件
    ├── scene_001_narration.mp3
    ├── scene_001_dialogue_001.mp3
    └── ...
```

---

## 🎯 测试内容

### 单元测试 (`test_unit_tts.py`)

- ✅ 测试文本清理和预处理
- ✅ 测试角色音色分配（火山引擎语音类型）
- ✅ 测试情绪参数映射（语速、音调、音量）
- ✅ 测试音频时长估算
- ✅ 测试火山引擎 TTS 请求格式
- ✅ 测试错误处理机制

### 功能测试 (`test_functional_tts.py`)

- ✅ 测试单个旁白音频生成
- ✅ 测试单个对话音频生成
- ✅ 测试完整场景音频生成
- ✅ 测试音频文件保存
- ✅ 测试火山引擎 TTS 集成
- ✅ 测试角色音色分配一致性
- ✅ 测试情绪参数映射

### 集成测试 (`test_integration_tts.py`)

- ✅ 测试从 Stage1 输出到音频生成的完整流程
- ✅ 测试所有场景的批量音频生成
- ✅ 测试音频时长与字幕时间轴对齐

---

## 🚀 运行测试

```bash
# 运行所有 Stage4 测试
pytest tests/backend/stage4/ -v

# 运行单元测试
pytest tests/backend/stage4/test_unit_tts.py -v

# 运行功能测试
pytest tests/backend/stage4/test_functional_tts.py -v

# 运行集成测试
pytest tests/backend/stage4/test_integration_tts.py -v
```

---

## 📊 输入输出格式

### 输入（Stage1 Output）

```json
{
  "characters": [
    {
      "id": "char_001",
      "name": "Wang Miao",
      "description": "A middle-aged man in his 40s",
      "age": 45,
      "gender": "male"
    }
  ],
  "scenes": [
    {
      "scene_id": "scene_001",
      "narration": "深夜，汪淼站在窗前...",
      "dialogues": [
        {
          "character": "char_001",
          "text": "这到底是什么？",
          "emotion": "Anxious and confused"
        }
      ]
    }
  ]
}
```

### 输出（Stage4 Output）

```json
{
  "scenes": [
    {
      "scene_id": "scene_001",
      "audio_segments": [
        {
          "type": "narration",
          "text": "深夜，汪淼站在窗前...",
          "audio_path": "/path/to/audio/scene_001_narration.mp3",
          "duration": 12.5,
          "start_time": 0.0,
          "voice": "narrator"
        },
        {
          "type": "dialogue",
          "character": "char_001",
          "text": "这到底是什么？",
          "audio_path": "/path/to/audio/scene_001_dialogue_001.mp3",
          "duration": 1.5,
          "start_time": 12.5,
          "voice": "male_middle_aged"
        }
      ],
      "total_duration": 14.0
    }
  ],
  "total_video_duration": 63.5,
  "character_voices": {
    "char_001": "male_middle_aged",
    "char_002": "male_young", 
    "char_003": "female_elderly",
    "narrator": "narrator"
  }
}
```

---

## 🔧 技术实现

### 火山引擎 TTS 服务

1. **语音类型映射**
   - `BV001_streaming`: 标准女声（旁白、年轻女性）
   - `BV700_streaming`: 标准男声（中年男性）
   - `BV701_streaming`: 年轻男声
   - `BV002_streaming`: 成熟女声（老年女性）

2. **情绪参数支持**
   - 语速调整：0.9 - 1.2
   - 音调调整：0.9 - 1.1
   - 音量调整：0.8 - 1.2

3. **音色分配策略**

```python
character_voices = {
    "char_001": "BV700_streaming",  # Wang Miao - 中年男性
    "char_002": "BV701_streaming",  # Xiao Li - 年轻男性
    "char_003": "BV002_streaming",  # Ye Wenjie - 老年女性
    "narrator": "BV001_streaming"   # 旁白 - 标准女声
}
```

### 环境变量配置

```bash
# 必需的环境变量
export VOLCENGINE_APPID="your_appid_here"
export VOLCENGINE_ACCESS_TOKEN="your_access_token_here"

# 可选的环境变量
export VOLCENGINE_CLUSTER="volcano_tts"  # 默认为 volcano_tts
```

---

## 🧪 测试用例说明

### Mock 数据测试

测试使用 `mockdata/` 目录中的真实数据：

1. **原始文本** (`original_text.txt`): 三体故事片段
2. **Stage1 输出** (`stage1_output.json`): 包含3个场景，3个角色
3. **预期输出** (`stage4_expected_output.json`): 用于验证音频生成结果

### 测试场景

1. **场景1**: 汪淼深夜站在窗前，看到神秘数字
2. **场景2**: 实验室中，汪淼与助手小李的对话
3. **场景3**: 汪淼拜访叶文洁，了解三体文明真相

### 角色音色测试

- **汪淼** (char_001): 中年男性科学家 → `BV700_streaming`
- **小李** (char_002): 年轻男性助手 → `BV701_streaming`  
- **叶文洁** (char_003): 老年女性工程师 → `BV002_streaming`
- **旁白**: 故事叙述 → `BV001_streaming`

---

## ⚠️ 注意事项

1. **成本控制**: 火山引擎 TTS 按字符收费，建议测试时使用较短的文本
2. **音频格式**: 统一使用 MP3 格式，采样率根据火山引擎配置
3. **时长估算**: 中文约 3-4 字/秒，英文约 5-6 字/秒
4. **网络依赖**: 需要稳定的网络连接访问火山引擎 API
5. **认证要求**: 需要有效的火山引擎应用凭证

---

## 📝 已完成功能

- ✅ 火山引擎 TTS 服务集成
- ✅ 智能角色音色分配
- ✅ 情绪参数映射（语速、音调、音量）
- ✅ 音频文件生成和保存
- ✅ 完整的测试覆盖
- ✅ 错误处理和异常管理
- ✅ 并发音频生成支持
- ✅ 音频时长估算
- ✅ 时间轴计算

---

## 🔄 测试流程

1. **单元测试**: 验证基础功能（文本处理、音色分配、参数映射）
2. **功能测试**: 验证完整音频生成流程（使用 mockdata）
3. **集成测试**: 验证端到端流程（Stage1 → Stage4）
4. **性能测试**: 验证并发处理和错误恢复

测试确保火山引擎 TTS 服务能够正确读取文本并生成高质量的语音音频。
