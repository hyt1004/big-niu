# Stage5 视频合成测试

## 功能描述

Stage5 负责将图像、音频和字幕合成为最终视频。基于 `Stage5VideoCompositionService` 实现图片和声音整合成视频的完整功能。

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
│   ├── scene_002_narration.mp3
│   ├── scene_002_dialogue_001.mp3
│   ├── scene_002_dialogue_002.mp3
│   ├── scene_002_dialogue_003.mp3
│   ├── scene_002_dialogue_004.mp3
│   ├── scene_003_narration.mp3
│   ├── scene_003_dialogue_001.mp3
│   ├── scene_003_dialogue_002.mp3
│   ├── scene_003_dialogue_003.mp3
│   ├── scene_003_dialogue_004.mp3
│   └── scene_003_dialogue_005.mp3
└── output/                     # 生成的输出文件
    ├── videos/                 # 最终视频文件
    └── temp/                   # 临时文件
```

---

## 🎯 测试脚本

### 1. 完整测试脚本 (`test_video_composition.py`)

**功能**: 完整的视频合成测试，包含所有测试场景

**特性**:
- 测试 `compose_video` 方法（使用stage4数据）
- 测试 `compose_video_simple` 方法（使用简单参数）
- 自动验证生成的字幕文件
- 完整的错误处理和日志输出
- 自动清理临时文件

**运行方式**:
```bash
cd tests/backend/stage5/
python test_video_composition.py
```


## 🚀 运行测试

### 运行新创建的测试脚本

```bash
# 进入测试目录
cd tests/backend/stage5/

# 运行完整测试脚本
python test_video_composition.py

```

---

## 📊 输入输出格式

### 输入数据格式

#### Stage3 数据（图片信息）
```python
stage3_data = [
    {
        "scene_id": "scene_001",
        "image_path": "tests/backend/stage5/mockdata/images/scene_001.png"
    },
    {
        "scene_id": "scene_002", 
        "image_path": "tests/backend/stage5/mockdata/images/scene_002.png"
    }
]
```

#### Stage4 数据（音频信息）
```json
{
  "scenes": [
    {
      "scene_id": "scene_001",
      "image_path": "tests/backend/stage5/mockdata/images/scene_001.png",
      "audio_segments": [
        {
          "type": "narration",
          "text": "深夜，汪淼站在窗前，望着天空中闪烁的星星。",
          "audio_path": "tests/backend/stage5/mockdata/audio/scene_001_narration.mp3",
          "duration": 12.5,
          "start_time": 0.0
        },
        {
          "type": "dialogue",
          "character": "char_001",
          "text": "这到底是什么？",
          "audio_path": "tests/backend/stage5/mockdata/audio/scene_001_dialogue_001.mp3",
          "duration": 1.5,
          "start_time": 12.5
        }
      ],
      "total_duration": 14.0
    }
  ],
  "total_video_duration": 63.5
}
```

### 输出数据格式

#### Stage5Output 对象
```python
{
    "video_id": "test_video_001",
    "video_path": "/path/to/final_video.mp4",
    "video_url": None,
    "duration": 63.5,
    "resolution": "1920x1080", 
    "file_size": 15728640,
    "format": "mp4",
    "scenes_count": 3
}
```

#### 生成的字幕文件（SRT格式）
```
1
00:00:00,000 --> 00:00:12,500
深夜，汪淼站在窗前，望着天空中闪烁的星星。

2
00:00:12,500 --> 00:00:14,000
这到底是什么？
```

---

## 🔧 技术实现

### Stage5VideoCompositionService 核心方法

#### 1. `compose_video()` - 完整视频合成
```python
def compose_video(self, stage3_data, stage4_data, video_id):
    """
    使用stage3和stage4数据合成完整视频
    - stage3_data: 图片信息列表
    - stage4_data: 音频信息字典
    - video_id: 视频ID
    """
```

#### 2. `compose_video_simple()` - 简化视频合成
```python
def compose_video_simple(self, image_paths, audio_paths, durations, subtitle_texts, video_id):
    """
    使用简单参数合成视频
    - image_paths: 图片路径列表
    - audio_paths: 音频路径列表  
    - durations: 时长列表
    - subtitle_texts: 字幕文本列表
    - video_id: 视频ID
    """
```

### FFmpeg 视频合成流程

#### 1. 场景视频生成
```bash
ffmpeg -y -loop 1 -t 14.0 -i scene_001.png \
  -c:v libx264 -pix_fmt yuv420p \
  -vf scale=1920:1080 scene_001_video.mp4
```

#### 2. 音频合并
```bash
ffmpeg -y -f concat -safe 0 -i audio_concat_list.txt \
  -c copy merged_audio.mp3
```

#### 3. 视频拼接
```bash
ffmpeg -y -f concat -safe 0 -i video_concat_list.txt \
  -c copy temp_video.mp4
```

#### 4. 添加音频和字幕
```bash
ffmpeg -y -i temp_video.mp4 -i merged_audio.mp3 \
  -vf "subtitles=subtitles.srt:force_style='FontSize=24,PrimaryColour=&HFFFFFF&,OutlineColour=&H000000&,Outline=2'" \
  -c:v libx264 -preset medium -crf 23 \
  -c:a aac -b:a 192k -pix_fmt yuv420p \
  final_video.mp4
```

### 字幕生成（SRT 格式）

#### SubtitleEntry 类
```python
class SubtitleEntry:
    def __init__(self, index, start_time, end_time, text):
        self.index = index
        self.start_time = start_time
        self.end_time = end_time
        self.text = text
    
    def to_srt_format(self):
        """转换为SRT格式字符串"""
        start_str = format_timestamp(self.start_time)
        end_str = format_timestamp(self.end_time)
        return f"{self.index}\n{start_str} --> {end_str}\n{self.text}\n"
```

#### 时间戳格式化
```python
def format_timestamp(seconds):
    """将秒数转换为SRT时间戳格式"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
```

---

## ⚠️ 注意事项

### 系统要求
1. **FFmpeg 依赖**: 需要系统安装 FFmpeg
   ```bash
   # macOS
   brew install ffmpeg
   
   # Ubuntu/Debian
   sudo apt install ffmpeg
   
   # Windows
   # 下载并安装 FFmpeg，添加到 PATH
   ```

2. **Python 依赖**: 需要安装项目依赖
   ```bash
   pip install -r requirements.txt
   ```

### 视频参数
- **编码**: H.264 (libx264)
- **分辨率**: 1920x1080 (16:9)
- **像素格式**: yuv420p
- **音频编码**: AAC
- **音频码率**: 192k
- **字幕样式**: 白色字体，黑色描边

### 文件路径
- 确保所有图片和音频文件路径正确
- 支持相对路径和绝对路径
- 临时文件会自动清理

### 错误处理
- FFmpeg 命令失败时会抛出 `ValueError`
- 文件不存在时会抛出 `FileNotFoundError`
- 建议在生产环境中添加重试机制

---

## 📝 使用示例

### 基本使用
```python
from backend.app.services.stage5_video_composition import Stage5VideoCompositionService

# 初始化服务
service = Stage5VideoCompositionService(
    output_dir="./output/videos",
    temp_dir="./output/temp"
)

# 使用完整数据合成视频
result = service.compose_video(
    stage3_data=stage3_data,
    stage4_data=stage4_data, 
    video_id="my_video"
)

# 使用简单参数合成视频
result = service.compose_video_simple(
    image_paths=["image1.png", "image2.png"],
    audio_paths=["audio1.mp3", "audio2.mp3"],
    durations=[10.0, 15.0],
    subtitle_texts=[(0, 10, "第一段"), (10, 25, "第二段")],
    video_id="simple_video"
)
```

### 测试脚本使用
```bash
# 运行完整测试
python test_video_composition.py

# 运行快速测试  
python run_video_test.py

# 运行pytest测试
pytest tests/backend/stage5/ -v
```

---

## 📝 TODO

- [x] 实现完整的视频合成服务
- [x] 创建测试脚本
- [x] 支持SRT字幕格式
- [x] 实现音频合并功能
- [ ] 支持多种视频格式输出
- [ ] 添加转场效果
- [ ] 支持背景音乐
- [ ] 实现进度回调
- [ ] 添加水印功能
- [ ] 支持视频质量预设
- [ ] 添加批量处理功能
