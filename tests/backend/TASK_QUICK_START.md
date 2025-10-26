# 🚀 任务系统快速开始

**5分钟从文本到视频！**

---

## ⚡ 最快开始

```bash
cd tests/backend

# 使用内置测试文本，一键运行
python test_full_task.py
```

就这么简单！等待2-3分钟，你将得到：
- ✅ 3个场景分镜
- ✅ 3张生成的图像
- ✅ 完整的音频配音
- ✅ 带字幕的最终视频

---

## 📖 使用自己的文本

### 方法1: 命令行（推荐）

```bash
# 从文件运行
python run_task.py --file your_story.txt

# 指定场景数量
python run_task.py --file your_story.txt --scenes 5

# 指定任务名称
python run_task.py --file your_story.txt --name "我的故事"
```

### 方法2: Shell 脚本

```bash
# 简单运行
./run_task.sh --file your_story.txt

# 完整参数
./run_task.sh --file your_story.txt --scenes 5 --name "我的故事"
```

### 方法3: Python 代码

```python
import asyncio
from app.services.task_orchestrator import TaskOrchestrator

async def main():
    orchestrator = TaskOrchestrator()
    
    # 从文件读取
    with open("your_story.txt") as f:
        text = f.read()
    
    # 运行任务
    result = await orchestrator.run_task(
        text=text,
        scenes_count=3,
        task_name="我的视频"
    )
    
    print(f"视频: {result['final_output']['video_path']}")

asyncio.run(main())
```

---

## 📁 输出在哪里？

所有输出保存在：
```
output/tasks/task_YYYYMMDD_HHMMSS_xxxx/
├── task_metadata.json          # 任务信息
├── stage1/output.json          # 场景分镜
├── stage2/output.json          # 图像提示词
├── stage3/images/              # 生成的图像
├── stage4/audio/               # 生成的音频
└── stage5/video/final_video.mp4  # 🎬 最终视频！
```

---

## 🎬 查看结果

### 播放视频

```bash
# macOS
open output/tasks/task_xxx/stage5/video/final_video.mp4

# Linux
xdg-open output/tasks/task_xxx/stage5/video/final_video.mp4

# Windows
start output/tasks/task_xxx/stage5/video/final_video.mp4
```

### 查看任务信息

```bash
# 查看任务元数据
cat output/tasks/task_xxx/task_metadata.json | jq .

# 列出所有任务
python test_full_task.py --mode list

# 或
./run_task.sh --list
```

---

## 💡 实用示例

### 示例1: 批量处理

```bash
# 处理目录中所有文本
for file in stories/*.txt; do
    python run_task.py --file "$file" --scenes 3
done
```

### 示例2: 不同场景数

```bash
# 短视频（3个场景，约1分钟）
python run_task.py --file short_story.txt --scenes 3

# 中等视频（5个场景，约2分钟）
python run_task.py --file medium_story.txt --scenes 5

# 长视频（10个场景，约4分钟）
python run_task.py --file long_story.txt --scenes 10
```

### 示例3: 测试不同的故事

```bash
# 三体故事
python run_task.py --file tests/backend/stage1/mock_input_threebody.txt

# 西游记故事
python run_task.py --file tests/backend/stage1/mock_input_journey.txt
```

---

## ⚙️ 环境配置

确保 `backend/.env` 文件包含：

```bash
# OpenRouter API (用于 Stage1-3)
OPENROUTER_API_KEY=your_key_here

# OpenAI API (用于 Stage4 TTS)
OPENAI_API_KEY=your_key_here
```

---

## ⏱️ 预计时间

| 场景数 | 预计时间 | 视频时长 |
|--------|----------|----------|
| 3个 | 2-3分钟 | ~1分钟 |
| 5个 | 3-5分钟 | ~2分钟 |
| 10个 | 6-10分钟 | ~4分钟 |

---

## 💰 预计成本

| Stage | 3个场景 | 5个场景 |
|-------|---------|---------|
| Stage1 | $0.01 | $0.01 |
| Stage2 | $0.03 | $0.05 |
| Stage3 | $0.15 | $0.25 |
| Stage4 | $0.05 | $0.08 |
| Stage5 | 免费 | 免费 |
| **总计** | **~$0.25** | **~$0.40** |

---

## ❓ 常见问题

### Q: 如何停止正在运行的任务？

A: 按 `Ctrl+C` 中断执行。

### Q: 任务失败了怎么办？

A: 查看错误信息，检查：
1. API keys 是否配置正确
2. 网络连接是否正常
3. 磁盘空间是否充足

### Q: 如何删除旧任务？

A: 直接删除 `output/tasks/` 下的任务目录。

### Q: 如何查看详细日志？

A: 任务执行时会实时输出日志。也可以查看 `task_metadata.json`。

---

## 🔧 故障排查

### 问题1: 导入错误

```
ModuleNotFoundError: No module named 'app'
```

**解决**: 确保在正确目录
```bash
cd tests/backend
python run_task.py --file story.txt
```

### 问题2: API Key 错误

```
ValueError: API key is required
```

**解决**: 检查 `.env` 文件
```bash
cat ../../backend/.env | grep API_KEY
```

### 问题3: FFmpeg 未安装

```
FileNotFoundError: ffmpeg not found
```

**解决**: 安装 FFmpeg
```bash
# macOS
brew install ffmpeg

# Ubuntu
sudo apt-get install ffmpeg
```

---

## 📚 更多文档

- **完整指南**: [TASK_SYSTEM.md](../../docs/TASK_SYSTEM.md)
- **系统设计**: [text-to-video-design.md](../../docs/text-to-video-design.md)
- **Stage测试**: [STAGES_OVERVIEW.md](STAGES_OVERVIEW.md)

---

## 🎉 开始创作吧！

```bash
# 准备好你的故事
echo "你的精彩故事..." > my_story.txt

# 一键生成视频
python run_task.py --file my_story.txt --scenes 3

# 等待几分钟...

# 享受成果！
open output/tasks/task_*/stage5/video/final_video.mp4
```

**🚀 从文本到视频，就是这么简单！**
