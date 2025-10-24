# Big Niu Backend - 文字生成视频后端服务

基于 FastAPI 的智能文字生成视频系统后端服务，使用 OpenRouter API 进行 AI 处理。

## 技术栈

- **FastAPI**: 高性能 Python Web 框架
- **Pydantic**: 数据验证和设置管理
- **OpenRouter API**: 统一的 AI 模型访问接口
- **HTTPx**: 异步 HTTP 客户端

## 项目结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI 应用入口
│   ├── config.py                  # 配置管理
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py            # Pydantic 数据模型
│   └── services/
│       ├── __init__.py
│       ├── openrouter_client.py  # OpenRouter API 客户端
│       ├── stage1_text_analysis.py   # 阶段1：文本分析服务
│       └── stage2_image_prompt.py    # 阶段2：图像提示词生成服务
├── .env.example                   # 环境变量示例
├── environment.yml                # Conda 环境配置（推荐）
├── requirements.txt               # Python 依赖（备选）
└── README.md                      # 本文件
```

## 快速开始

### 1. 安装依赖

使用 conda 创建并激活虚拟环境：

```bash
cd backend

# 创建 conda 环境
conda env create -f environment.yml

# 激活环境
conda activate big-niu-backend
```

> **注意**：如果你更喜欢使用 pip，也可以运行 `pip install -r requirements.txt`

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并填写您的 OpenRouter API Key：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
TEXT_ANALYSIS_MODEL=anthropic/claude-3.5-sonnet
IMAGE_PROMPT_MODEL=anthropic/claude-3.5-sonnet
DEFAULT_SCENES_COUNT=10
```

### 3. 启动服务

```bash
uvicorn app.main:app --reload
```

服务将在 `http://localhost:8000` 启动。

访问 API 文档：`http://localhost:8000/docs`

## API 接口

### 阶段一：文本分析与分镜设计

**POST** `/api/v1/stage1/analyze`

将故事文本分析并拆分为多个场景分镜。

**请求体：**
```json
{
  "story_text": "故事文本内容...",
  "scenes_count": 10
}
```

**响应：**
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
      "name": "角色名称",
      "description": "角色外貌描述",
      "personality": "性格特点"
    }
  ],
  "scenes": [
    {
      "scene_id": "scene_001",
      "order": 1,
      "description": "场景描述",
      "composition": "镜头构图",
      "characters": ["char_001"],
      "narration": "旁白文字",
      "dialogues": [
        {
          "character": "char_001",
          "text": "对话内容",
          "emotion": "情绪"
        }
      ]
    }
  ]
}
```

### 阶段二：图像生成提示词

**POST** `/api/v1/stage2/generate-prompts`

为每个场景生成图像生成提示词。

**请求体：**
```json
{
  "stage1_output": {
    // 阶段一的完整输出
  }
}
```

**响应：**
```json
{
  "total_prompts": 10,
  "prompts": [
    {
      "scene_id": "scene_001",
      "image_prompt": "详细的英文图像生成提示词",
      "negative_prompt": "负向提示词",
      "style_tags": ["anime", "high_quality", "4k"],
      "characters_in_scene": ["char_001"]
    }
  ]
}
```

## 使用示例

### 使用 Python 调用

```python
import httpx
import asyncio

async def analyze_story():
    story_text = """
    深夜，汪淼站在窗前，望着天空中闪烁的星星...
    """
    
    async with httpx.AsyncClient() as client:
        # 阶段一：文本分析
        response = await client.post(
            "http://localhost:8000/api/v1/stage1/analyze",
            json={
                "story_text": story_text,
                "scenes_count": 5
            }
        )
        stage1_result = response.json()
        print("阶段一完成：", stage1_result)
        
        # 阶段二：生成图像提示词
        response = await client.post(
            "http://localhost:8000/api/v1/stage2/generate-prompts",
            json={"stage1_output": stage1_result}
        )
        stage2_result = response.json()
        print("阶段二完成：", stage2_result)

asyncio.run(analyze_story())
```

### 使用 curl 调用

```bash
# 阶段一：文本分析
curl -X POST "http://localhost:8000/api/v1/stage1/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "story_text": "故事文本...",
    "scenes_count": 5
  }'
```

## OpenRouter 配置说明

本项目使用 [OpenRouter](https://openrouter.ai/) 作为统一的 AI 模型访问接口。OpenRouter 支持多种 AI 模型，包括：

- **文本生成**: GPT-4, Claude 3.5 Sonnet, Gemini Pro 等
- **图像生成**: DALL-E 3, Stable Diffusion 等

### 获取 API Key

1. 访问 [OpenRouter 官网](https://openrouter.ai/)
2. 注册账号并登录
3. 在 [Keys](https://openrouter.ai/keys) 页面创建 API Key
4. 将 API Key 填入 `.env` 文件

### 选择模型

在 `.env` 文件中配置模型：

```env
# 推荐使用 Claude 3.5 Sonnet，效果好且价格合理
TEXT_ANALYSIS_MODEL=anthropic/claude-3.5-sonnet
IMAGE_PROMPT_MODEL=anthropic/claude-3.5-sonnet

# 也可以使用其他模型
# TEXT_ANALYSIS_MODEL=openai/gpt-4-turbo
# IMAGE_PROMPT_MODEL=openai/gpt-4-turbo
```

查看所有可用模型：https://openrouter.ai/models

## 测试数据

测试输入文件位于 `tests/backend/stage1/`：

- `mock_input_threebody.txt` - 三体故事片段
- `mock_input_journey.txt` - 西游记故事片段

可以读取这些文件进行测试：

```python
with open("tests/backend/stage1/mock_input_threebody.txt", "r") as f:
    story = f.read()

# 调用 API 进行测试
```

## 开发指南

### Conda 环境管理

#### 更新依赖

如果需要添加新的依赖包：

1. 手动编辑 `environment.yml` 文件，在 `pip:` 部分添加新包
2. 更新环境：
   ```bash
   conda env update -f environment.yml --prune
   ```

#### 导出当前环境

如果你在环境中安装了新包，想要更新 `environment.yml`：

```bash
# 导出完整环境（包括所有依赖）
conda env export > environment.yml

# 或者只导出明确安装的包（推荐）
conda env export --from-history > environment.yml
```

#### 删除环境

```bash
conda deactivate
conda env remove -n big-niu-backend
```

#### 列出所有 conda 环境

```bash
conda env list
```

### 代码规范

- 使用 Black 进行代码格式化
- 使用 isort 整理导入
- 遵循 PEP 8 规范

### 运行测试

```bash
pytest tests/backend/
```

### 添加新功能

1. 在 `app/services/` 中添加新的服务类
2. 在 `app/models/schemas.py` 中定义数据模型
3. 在 `app/main.py` 中添加 API 端点
4. 编写相应的测试

## 故障排查

### API Key 错误

如果遇到 `OpenRouter API key is required` 错误：

1. 确认 `.env` 文件存在且配置正确
2. 确认 `OPENROUTER_API_KEY` 已设置
3. 重启服务

### JSON 解析错误

如果 AI 返回的内容无法解析为 JSON：

1. 检查模型配置是否正确
2. 尝试调整 temperature 参数
3. 查看错误信息中的原始内容

### 超时错误

如果请求超时：

1. 增加 `httpx.AsyncClient` 的 timeout 值
2. 检查网络连接
3. 考虑使用更快的模型

## 许可证

MIT License
