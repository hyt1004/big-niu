# Stage5 视频合成测试

## 功能描述

Stage5 负责将图像、音频和字幕合成为最终视频。

---

## 📁 Mock 数据结构

```
stage5/mockdata/
├── stage4_output.json          # Stage4 输出（音频信息）
├── expected_subtitles.srt      # 预期生成的字幕文件
├── images/                     # 场景图像
│   ├── scene_001.png
│   ├── scene_002.png
│   └── scene_003.png
├── audio/                      # 音频文件
│   ├── scene_001_narration.mp3
│   ├── scene_001_dialogue_001.mp3
│   └── ...
├── subtitles/                  # 生成的字幕文件
│   └── video_subtitles.srt
└── video/                      # 生成的视频文件
    └── final_video.mp4
```

---

## 🎯 测试内容

### 单元测试 (`test_unit_video_composition.py`)

已存在，测试：
- FFmpeg 命令生成
- 字幕格式转换
- 视频参数验证

### 功能测试 (`test_functional_video_composition.py`)

已存在，测试：
- 单个场景视频生成
- 音频合并
- 字幕叠加
- 完整视频合成

---

## 🚀 运行测试

```bash
# 运行所有 Stage5 测试
pytest tests/backend/stage5/ -v

# 运行单元测试
pytest tests/backend/stage5/test_unit_video_composition.py -v

# 运行功能测试
pytest tests/backend/stage5/test_functional_video_composition.py -v
```

---

## 📊 输入输出格式

### 输入（Stage4 Output）

```json
{
  "scenes": [
    {
      "scene_id": "scene_001",
      "image_path": "/path/to/scene_001.png",
      "audio_segments": [...],
      "total_duration": 14.0
    }
  ]
}
```

### 输出（Stage5 Output）

```json
{
  "video_path": "/path/to/final_video.mp4",
  "subtitle_path": "/path/to/subtitles.srt",
  "duration": 63.5,
  "resolution": "1920x1080",
  "fps": 30,
  "codec": "h264"
}
```

---

## 🔧 技术实现

### FFmpeg 视频合成流程

1. **图片序列生成**
   ```bash
   ffmpeg -loop 1 -t 14.0 -i scene_001.png -c:v libx264 scene_001.mp4
   ```

2. **音频合并**
   ```bash
   ffmpeg -i "concat:audio1.mp3|audio2.mp3" -c copy merged_audio.mp3
   ```

3. **视频拼接**
   ```bash
   ffmpeg -f concat -safe 0 -i inputs.txt -c copy temp_video.mp4
   ```

4. **字幕叠加**
   ```bash
   ffmpeg -i video.mp4 -vf subtitles=subtitles.srt final_video.mp4
   ```

### 字幕生成（SRT 格式）

```python
def generate_srt(audio_segments):
    """生成 SRT 字幕文件"""
    srt_content = []
    index = 1
    cumulative_time = 0.0
    
    for segment in audio_segments:
        start_time = format_timestamp(cumulative_time)
        end_time = format_timestamp(cumulative_time + segment["duration"])
        
        srt_content.append(f"{index}")
        srt_content.append(f"{start_time} --> {end_time}")
        srt_content.append(segment["text"])
        srt_content.append("")  # 空行
        
        index += 1
        cumulative_time += segment["duration"]
    
    return "\n".join(srt_content)
```

---

## ⚠️ 注意事项

1. **FFmpeg 依赖**: 需要系统安装 FFmpeg
2. **视频编码**: 使用 H.264 编码，兼容性好
3. **分辨率**: 默认 1920x1080（16:9）
4. **帧率**: 30fps
5. **音频编码**: AAC 或 MP3

---

## 📝 TODO

- [ ] 实现 FFmpeg 包装器
- [ ] 支持多种视频格式输出
- [ ] 添加转场效果
- [ ] 支持背景音乐
- [ ] 实现进度回调
- [ ] 添加水印功能
