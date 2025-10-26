# 真实TTS音频生成测试

这个测试脚本能够读取Stage1的输出数据，调用火山引擎TTS接口生成真实的音频文件，并按照Stage4的预期输出格式保存结果。

## 功能特性

- ✅ 读取Stage1输出数据（`stage1_output.json`）
- ✅ 智能音色分配（基于角色特征）
- ✅ 调用火山引擎TTS接口生成真实音频
- ✅ 计算音频时长信息
- ✅ 按照Stage4格式保存输出结果
- ✅ 生成统计信息和验证报告

## 环境要求

### 1. 环境变量设置

在运行测试前，需要设置以下环境变量：

```bash
export VOLCENGINE_APPID='your_volcengine_appid'
export VOLCENGINE_ACCESS_TOKEN='your_volcengine_access_token'
export VOLCENGINE_CLUSTER='volcano_tts'  # 可选，默认为volcano_tts
```

### 2. 依赖安装

确保已安装项目依赖：

```bash
cd /path/to/big-niu
pip install -r backend/requirements.txt
```

## 使用方法

### 方法1：直接运行测试脚本

```bash
cd /path/to/big-niu
python tests/backend/stage4/test_real_tts_generation.py
```

### 方法2：使用运行脚本

```bash
cd /path/to/big-niu
python tests/backend/stage4/run_real_tts_test.py
```

## 输出结果

测试完成后，会在临时目录中生成以下文件：

```
/tmp/tts_generation_xxxxxx/
├── audio/                          # 音频文件目录
│   ├── scene_001_narration.mp3     # 场景1旁白
│   ├── scene_001_dialogue_001.mp3  # 场景1对话1
│   ├── scene_002_narration.mp3     # 场景2旁白
│   └── ...                         # 其他音频文件
└── stage4_output.json              # Stage4格式的输出结果
```

## 音色分配规则

脚本会根据角色特征自动分配音色：

- **老年女性** (70s, 银发) → `female_elderly`
- **年轻男性** (20s) → `male_young`  
- **中年男性** (40s) → `male_middle_aged`
- **旁白** → `narrator`
- **默认** → `male_middle_aged`

## 输出格式

生成的`stage4_output.json`文件包含：

```json
{
  "scenes": [
    {
      "scene_id": "scene_001",
      "audio_segments": [
        {
          "type": "narration",
          "text": "旁白文本",
          "audio_path": "音频文件路径",
          "duration": 12.5,
          "start_time": 0.0,
          "voice": "narrator"
        },
        {
          "type": "dialogue",
          "character": "char_001",
          "character_name": "角色名称",
          "text": "对话文本",
          "emotion": "情感描述",
          "audio_path": "音频文件路径",
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

## 测试流程

1. **环境检查** - 验证环境变量和依赖
2. **数据加载** - 读取Stage1输出数据
3. **音色分配** - 为角色分配合适的音色
4. **音频生成** - 调用TTS接口生成音频文件
5. **结果保存** - 按Stage4格式保存输出
6. **文件验证** - 验证生成的音频文件
7. **统计报告** - 显示生成统计信息

## 注意事项

- 确保火山引擎TTS服务可用且有足够的配额
- 生成的音频文件会占用磁盘空间，测试完成后可选择清理
- 音频生成需要时间，请耐心等待
- 如果遇到网络问题，脚本会显示相应错误信息

## 故障排除

### 环境变量未设置
```
❌ 环境变量 VOLCENGINE_APPID 未设置
```
**解决方案**: 设置相应的环境变量

### 依赖模块缺失
```
ModuleNotFoundError: No module named 'aiofiles'
```
**解决方案**: 安装项目依赖 `pip install -r backend/requirements.txt`

### TTS接口调用失败
```
❌ TTS音频生成失败: HTTP 401 Unauthorized
```
**解决方案**: 检查APPID和ACCESS_TOKEN是否正确

### 音频文件生成失败
```
❌ 音频文件未找到
```
**解决方案**: 检查输出目录权限和磁盘空间
