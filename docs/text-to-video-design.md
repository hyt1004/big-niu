# 文字生成视频功能设计文档

## 1. 需求概述

将用户上传的小说或故事文字内容转换为完整的视频，包含画面、配音和字幕。

### 1.1 核心流程

```
文字内容输入 → 结构化提取与分镜拆分 → 图像生成 → 视频合成（音频+字幕）→ 视频输出
```

### 1.2 技术目标

- 自动提取故事关键要素（人物、剧情、对白）
- 智能拆分为可配置数量的分镜（默认10个）
- 为每个分镜生成对应的图像
- 合成包含旁白、字幕和画面的完整视频

## 2. 系统架构

### 2.1 整体流程图

```
┌─────────────────────────────────────────────────────────────────┐
│                        用户上传文字内容                          │
└────────────────────────────┬────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                   阶段1: 文本分析与分镜设计                       │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │ 关键信息提取 │ →  │ 分镜拆分     │ →  │ 结构化输出   │      │
│  │ (人物/剧情)  │    │ (N个镜头)    │    │ (JSON)       │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
└────────────────────────────┬────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                   阶段2: 图像生成                                │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │ 提示词构建   │ →  │ 文生图/图生图│ →  │ 分镜图片     │      │
│  │ (Prompt)     │    │ (AI模型)     │    │ (Images)     │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
└────────────────────────────┬────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                   阶段3: 视频合成                                │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │ 旁白TTS生成  │    │ 字幕文件生成 │    │ 视频合成     │      │
│  │ (音频+时长)  │ →  │ (SRT+时长)   │ →  │ (FFmpeg)     │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
└────────────────────────────┬────────────────────────────────────┘
                             ↓
                      ┌──────────────┐
                      │  视频文件输出 │
                      └──────────────┘
```

## 3. 阶段一：文本分析与分镜设计

### 3.1 功能描述

从原始文字内容中提取结构化信息，并拆分为多个分镜。

### 3.2 输入

- **文字内容**: 小说或故事文本（String）
- **分镜数量**: 目标分镜数（可配置，默认10）

### 3.3 处理流程

#### 3.3.1 关键信息提取

通过NLP模型（GPT-4/通义千问）提取：

- **人物列表**: 主要角色及其特征描述
- **剧情概要**: 故事的起承转合
- **关键对白**: 重要对话内容

#### 3.3.2 分镜拆分逻辑

根据配置的分镜数量N，将故事分为N个段落，每个分镜包含：

- **镜头编号**: scene_001, scene_002...
- **镜头描述**: 该段落的场景和构图说明
- **涉及人物**: 出现在该镜头的角色列表
- **剧情文字**: 对应的故事文本片段
- **对白内容**: 角色对话（如有）
- **旁白文字**: 叙述性文本

### 3.4 输出格式

```json
{
  "metadata": {
    "total_scenes": 10,
    "story_title": "故事标题",
    "total_characters": 3
  },
  "characters": [
    {
      "id": "char_001",
      "name": "张三",
      "description": "年轻男子，黑色短发，穿着现代休闲装",
      "personality": "勇敢、善良"
    }
  ],
  "scenes": [
    {
      "scene_id": "scene_001",
      "order": 1,
      "description": "清晨的城市街道，阳光洒在高楼之间",
      "composition": "远景，俯视角度",
      "characters": ["char_001"],
      "narration": "这是一个平凡的早晨，张三走在上班的路上。",
      "dialogues": [
        {
          "character": "char_001",
          "text": "今天会是美好的一天。",
          "emotion": "愉悦"
        }
      ]
    }
  ]
}
```

### 3.5 技术实现

- **API 接口**: OpenRouter API (https://openrouter.ai/)
- **模型选择**: 通过 OpenRouter 访问 Claude 3.5 Sonnet / GPT-4 等大语言模型
- **提示工程**: 设计专门的Prompt模板确保输出格式一致性
- **验证机制**: 检查输出JSON的完整性和有效性

OpenRouter 提供了统一的 API 接口访问多种 AI 模型，简化了模型切换和管理。

## 4. 阶段二：图像生成

### 4.1 功能描述

根据每个分镜的描述和人物信息，生成对应的图像。

### 4.2 输入

- 阶段一输出的结构化分镜数据
- 人物特征描述
- 场景构图信息

### 4.3 处理流程

#### 4.3.1 提示词构建

为每个分镜构建图像生成提示词（Prompt）：

```
基础提示词 = 场景描述 + 人物特征 + 构图信息 + 风格标签
```

示例：
```
"清晨的城市街道，阳光洒在高楼之间，一位黑色短发的年轻男子穿着休闲装行走，
远景俯视角度，动漫风格，高质量，4K分辨率"
```

#### 4.3.2 图像生成模式

**模式1: 纯文生图**
- 使用Stable Diffusion / DALL-E
- 直接从提示词生成图像

**模式2: 图+文生图（角色一致性）**
- 首次为角色生成参考图
- 后续使用ControlNet/LoRA保持角色一致性
- 将角色合成到新场景中

#### 4.3.3 图像质量控制

- **分辨率**: 1920x1080（Full HD）
- **格式**: PNG（无损）
- **风格**: 统一的动漫/插画风格
- **比例**: 16:9宽屏

### 4.4 输出

```json
{
  "scene_id": "scene_001",
  "image_path": "/storage/scenes/scene_001.png",
  "image_url": "https://cdn.qiniu.com/xxx/scene_001.png",
  "width": 1920,
  "height": 1080,
  "generation_params": {
    "model": "stable-diffusion-xl",
    "seed": 123456,
    "steps": 30
  }
}
```

### 4.5 技术实现

- **API 接口**: OpenRouter API (https://openrouter.ai/)
- **提示词生成**: 通过 OpenRouter 访问 Claude 3.5 Sonnet / GPT-4 生成优化的图像提示词
- **图像生成模型**: 通过 OpenRouter 访问 Stable Diffusion XL / DALL-E 3 等图像生成模型
- **一致性保持**: ControlNet / LoRA微调（后续阶段实现）
- **存储方案**: 七牛云对象存储
- **缓存策略**: Redis缓存生成参数，支持重新生成

阶段二当前实现重点是生成高质量的图像提示词（Prompt），为后续实际图像生成做准备。

## 5. 阶段三：视频合成

### 5.1 功能描述

将分镜图片、旁白音频、字幕组合成完整视频。

### 5.2 子流程

### 5.2.1 旁白音频生成（TTS）

**输入**:
- 每个分镜的旁白文字
- 角色对白及情绪标签

**处理**:
1. 为不同角色分配不同音色
2. 根据情绪调整语速和音调
3. 生成音频文件并记录时长

**输出**:
```json
{
  "scene_id": "scene_001",
  "audio_segments": [
    {
      "type": "narration",
      "text": "这是一个平凡的早晨...",
      "audio_path": "/storage/audio/scene_001_narration.mp3",
      "duration": 3.5,
      "start_time": 0.0
    },
    {
      "type": "dialogue",
      "character": "char_001",
      "text": "今天会是美好的一天。",
      "audio_path": "/storage/audio/scene_001_dialogue_001.mp3",
      "duration": 2.0,
      "start_time": 3.5
    }
  ],
  "total_duration": 5.5
}
```

### 5.2.2 字幕文件生成

根据音频时长和文字内容，生成SRT格式字幕：

```srt
1
00:00:00,000 --> 00:00:03,500
这是一个平凡的早晨，张三走在上班的路上。

2
00:00:03,500 --> 00:00:05,500
今天会是美好的一天。
```

### 5.2.3 视频合成

**合成逻辑**:

1. **图片处理**: 每个分镜图片显示时长 = 对应音频时长
2. **音频合并**: 按分镜顺序拼接所有音频片段
3. **字幕叠加**: 根据SRT文件添加字幕轨道
4. **视频编码**: 使用H.264编码输出MP4

**FFmpeg命令示例**:
```bash
# 1. 生成图片列表文件
echo "file 'scene_001.png'\nduration 5.5" > inputs.txt
echo "file 'scene_002.png'\nduration 4.2" >> inputs.txt

# 2. 合并音频
ffmpeg -i "concat:scene_001.mp3|scene_002.mp3" -c copy merged_audio.mp3

# 3. 合成视频
ffmpeg -f concat -safe 0 -i inputs.txt \
       -i merged_audio.mp3 \
       -vf "subtitles=subtitles.srt" \
       -c:v libx264 -preset medium -crf 23 \
       -c:a aac -b:a 192k \
       -pix_fmt yuv420p \
       output.mp4
```

### 5.3 输出

```json
{
  "video_id": "video_20241024_001",
  "video_path": "/storage/videos/video_20241024_001.mp4",
  "video_url": "https://cdn.qiniu.com/xxx/video_20241024_001.mp4",
  "duration": 125.5,
  "resolution": "1920x1080",
  "file_size": 45678901,
  "format": "mp4",
  "scenes_count": 10
}
```

## 6. 数据模型设计

### 6.1 任务表 (tasks)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 任务ID |
| user_id | UUID | 用户ID |
| story_text | TEXT | 原始文字内容 |
| scenes_count | INT | 分镜数量配置 |
| status | ENUM | pending/processing/completed/failed |
| current_stage | INT | 1:文本分析/2:图像生成/3:视频合成 |
| progress | INT | 0-100进度百分比 |
| result_video_url | STRING | 最终视频URL |
| created_at | TIMESTAMP | 创建时间 |
| completed_at | TIMESTAMP | 完成时间 |

### 6.2 分镜表 (scenes)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 分镜ID |
| task_id | UUID | 所属任务ID |
| scene_order | INT | 分镜顺序 |
| description | TEXT | 场景描述 |
| narration | TEXT | 旁白文字 |
| image_url | STRING | 生成的图片URL |
| audio_url | STRING | 音频文件URL |
| duration | FLOAT | 时长（秒） |
| created_at | TIMESTAMP | 创建时间 |

### 6.3 角色表 (characters)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 角色ID |
| task_id | UUID | 所属任务ID |
| name | STRING | 角色名称 |
| description | TEXT | 外貌特征 |
| voice_id | STRING | TTS音色ID |
| reference_image_url | STRING | 参考图片URL |
| created_at | TIMESTAMP | 创建时间 |

## 7. API接口设计

### 7.1 创建任务

```http
POST /api/v1/text-to-video/tasks

Request:
{
  "story_text": "故事文本内容...",
  "scenes_count": 10,
  "style": "anime"
}

Response:
{
  "task_id": "uuid-xxx",
  "status": "pending",
  "message": "任务已创建"
}
```

### 7.2 查询任务进度

```http
GET /api/v1/text-to-video/tasks/{task_id}

Response:
{
  "task_id": "uuid-xxx",
  "status": "processing",
  "current_stage": 2,
  "progress": 65,
  "stage_info": {
    "name": "图像生成",
    "completed_scenes": 6,
    "total_scenes": 10
  }
}
```

### 7.3 获取任务结果

```http
GET /api/v1/text-to-video/tasks/{task_id}/result

Response:
{
  "task_id": "uuid-xxx",
  "status": "completed",
  "video_url": "https://cdn.qiniu.com/xxx/video.mp4",
  "duration": 125.5,
  "scenes": [
    {
      "scene_id": "scene_001",
      "image_url": "...",
      "audio_url": "..."
    }
  ]
}
```

## 8. 异步任务处理

### 8.1 任务队列设计

使用Celery + Redis实现异步处理：

```python
@celery.task
def process_text_to_video(task_id: str):
    # 阶段1: 文本分析
    update_progress(task_id, stage=1, progress=0)
    structured_data = analyze_and_split_text(task_id)
    update_progress(task_id, stage=1, progress=100)
    
    # 阶段2: 图像生成
    update_progress(task_id, stage=2, progress=0)
    for i, scene in enumerate(structured_data.scenes):
        generate_scene_image(scene)
        progress = int((i + 1) / len(scenes) * 100)
        update_progress(task_id, stage=2, progress=progress)
    
    # 阶段3: 视频合成
    update_progress(task_id, stage=3, progress=0)
    generate_audio(task_id)
    update_progress(task_id, stage=3, progress=50)
    compose_video(task_id)
    update_progress(task_id, stage=3, progress=100)
    
    mark_task_completed(task_id)
```

### 8.2 WebSocket实时推送

前端通过WebSocket接收任务进度更新：

```javascript
const ws = new WebSocket('wss://api.bigniu.com/ws/tasks/{task_id}');
ws.onmessage = (event) => {
  const progress = JSON.parse(event.data);
  updateProgressBar(progress.stage, progress.progress);
};
```

## 9. 性能优化策略

### 9.1 并行处理

- 图像生成阶段，多个分镜并行生成（受GPU资源限制）
- 音频生成可与图像生成并行

### 9.2 缓存机制

- 角色参考图缓存（相同角色描述复用）
- 分镜描述相似度检测，复用已生成图片

### 9.3 资源控制

- 限制同时处理的任务数
- GPU资源队列管理
- 设置任务超时时间（默认30分钟）

## 10. 错误处理

### 10.1 失败重试机制

- 文本分析失败：重试3次
- 图像生成失败：跳过该分镜或使用占位图
- TTS生成失败：使用备用TTS服务
- 视频合成失败：重试1次

### 10.2 降级方案

- AI模型不可用时，使用备用模型
- 对象存储失败时，使用本地存储临时保存

## 11. 监控指标

### 11.1 业务指标

- 每日任务创建数
- 任务成功率
- 平均处理时长
- 各阶段耗时分布

### 11.2 技术指标

- API响应时间
- GPU利用率
- 存储使用量
- 任务队列长度

## 12. 未来扩展

### 12.1 功能增强

- 支持自定义角色外貌
- 支持分镜手动调整
- 支持背景音乐添加
- 支持多种视频风格（写实、水彩等）

### 12.2 性能提升

- 使用更快的图像生成模型
- 实现分布式GPU计算
- 引入CDN加速视频分发
