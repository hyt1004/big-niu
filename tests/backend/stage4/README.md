# Stage4 语音合成（TTS）测试

## 功能描述

Stage4 负责将场景的旁白和角色对话转换为语音音频文件。

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

- 测试文本清理和预处理
- 测试角色音色分配
- 测试情绪参数映射
- 测试音频时长估算

### 功能测试 (`test_functional_tts.py`)

- 测试单个旁白音频生成
- 测试单个对话音频生成
- 测试完整场景音频生成
- 测试音频文件保存

### 集成测试 (`test_integration_tts.py`)

- 测试从 Stage1 输出到音频生成的完整流程
- 测试所有场景的批量音频生成
- 测试音频时长与字幕时间轴对齐

---

## 🚀 运行测试

```bash
# 运行所有 Stage4 测试
pytest tests/backend/stage4/ -v

# 运行单元测试
pytest tests/backend/stage4/test_unit_tts.py -v

# 运行功能测试
pytest tests/backend/stage4/test_functional_tts.py -v
```

---

## 📊 输入输出格式

### 输入（Stage1 Output）

```json
{
  "characters": [...],
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
```

---

## 🔧 技术实现

### TTS 服务选择

1. **OpenAI TTS** (推荐)
   - 模型：`tts-1`, `tts-1-hd`
   - 音色：`alloy`, `echo`, `fable`, `onyx`, `nova`, `shimmer`
   - 支持中文

2. **Azure TTS**
   - 丰富的中文音色
   - 支持 SSML 情绪控制

3. **本地TTS**
   - Bark
   - Coqui TTS

### 音色分配策略

```python
character_voices = {
    "char_001": "echo",      # Wang Miao - 中年男性
    "char_002": "onyx",      # Xiao Li - 年轻男性
    "char_003": "shimmer",   # Ye Wenjie - 老年女性
    "narrator": "nova"       # 旁白
}
```

---

## ⚠️ 注意事项

1. **成本控制**: TTS API 按字符收费
2. **音频格式**: 统一使用 MP3 格式
3. **采样率**: 24kHz 或 48kHz
4. **时长估算**: 中文约 3-4 字/秒

---

## 📝 TODO

- [ ] 实现 TTS 服务封装
- [ ] 支持多种 TTS 提供商
- [ ] 实现情绪参数映射
- [ ] 添加音频后处理（音量均衡等）
- [ ] 支持音频缓存和重用
