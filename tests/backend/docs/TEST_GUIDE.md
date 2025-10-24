# Stage1 & Stage2 测试指南

## 服务状态

✅ 后端服务已启动在: `http://localhost:8000`

## 重要提醒

⚠️ **在测试之前，请确保已配置 OpenRouter API Key:**

```bash
# 编辑 .env 文件
nano .env

# 或
vim .env

# 确保 OPENROUTER_API_KEY 已设置
OPENROUTER_API_KEY=your_actual_api_key_here
```

## 快速测试方法

### 方法 1: 使用测试脚本 (推荐)

```bash
# 激活 conda 环境
conda activate big-niu-backend

# 测试三体故事 (默认5个场景)
python test_stages.py

# 测试西游记故事 (8个场景)
python test_stages.py journey 8

# 测试三体故事 (10个场景)
python test_stages.py threebody 10
```

### 方法 2: 使用 API 文档界面

访问 Swagger UI: http://localhost:8000/docs

在这里你可以:
- 查看所有 API 接口
- 直接在浏览器中测试 API
- 查看请求/响应格式

### 方法 3: 使用 curl 命令

#### 测试 Stage1

```bash
curl -X POST "http://localhost:8000/api/v1/stage1/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "story_text": "深夜，汪淼站在窗前，望着天空中闪烁的星星...",
    "scenes_count": 3
  }' | jq
```

#### 测试 Stage2

```bash
# 首先保存 stage1 的输出到文件
curl -X POST "http://localhost:8000/api/v1/stage1/analyze" \
  -H "Content-Type: application/json" \
  -d @stage1_request.json > stage1_output.json

# 然后使用 stage1 的输出测试 stage2
curl -X POST "http://localhost:8000/api/v1/stage2/generate-prompts" \
  -H "Content-Type: application/json" \
  -d "{\"stage1_output\": $(cat stage1_output.json)}" | jq
```

## 测试数据位置

- 三体测试文本: `../tests/backend/stage1/mock_input_threebody.txt`
- 西游记测试文本: `../tests/backend/stage1/mock_input_journey.txt`

## 输出文件

测试脚本会自动生成以下文件:
- `stage1_output.json` - Stage1 的完整输出
- `stage2_output.json` - Stage2 的完整输出

## 调试技巧

### 查看服务日志

服务启动时的日志会显示在终端中，包括:
- 请求信息
- 错误堆栈
- API 调用详情

### 检查服务状态

```bash
# 健康检查
curl http://localhost:8000/health

# 查看根路径信息
curl http://localhost:8000/
```

### 常见问题

1. **API Key 错误**
   - 检查 `.env` 文件中的 `OPENROUTER_API_KEY` 是否正确设置
   - 重启服务使环境变量生效

2. **超时错误**
   - AI 模型可能需要较长时间响应
   - 测试脚本已设置 120-180 秒超时
   - 可以尝试减少 `scenes_count` 数量

3. **JSON 解析错误**
   - 检查 AI 模型返回的内容
   - 查看服务日志中的原始响应
   - 可能需要调整 prompt 或模型参数

## Stage1 输出格式示例

```json
{
  "metadata": {
    "total_scenes": 5,
    "story_title": "故事标题",
    "total_characters": 2
  },
  "characters": [
    {
      "id": "char_001",
      "name": "汪淼",
      "description": "中年科学家...",
      "personality": "理性、好奇..."
    }
  ],
  "scenes": [
    {
      "scene_id": "scene_001",
      "order": 1,
      "description": "深夜的居室...",
      "composition": "中景镜头...",
      "characters": ["char_001"],
      "narration": "深夜，汪淼站在窗前...",
      "dialogues": [
        {
          "character": "char_001",
          "text": "这到底是什么？",
          "emotion": "困惑"
        }
      ]
    }
  ]
}
```

## Stage2 输出格式示例

```json
{
  "total_prompts": 5,
  "prompts": [
    {
      "scene_id": "scene_001",
      "image_prompt": "A middle-aged scientist standing by a window at night...",
      "negative_prompt": "blurry, low quality, distorted...",
      "style_tags": ["cinematic", "realistic", "4k"],
      "characters_in_scene": ["char_001"]
    }
  ]
}
```

## 停止服务

```bash
# 在运行 uvicorn 的终端按 Ctrl+C
# 或者找到进程并杀死
ps aux | grep uvicorn
kill <pid>
```
