# Stage3 图像生成测试总结

## ✅ 测试状态：成功

测试时间：2025-10-24

---

## 🎯 测试目标

使用 OpenRouter API 和 `openai/gpt-5-image-mini` 模型，从 Stage2 生成的图像提示词创建实际图像。

---

## 🔧 环境配置

### 已安装的依赖
- ✅ **pillow**: 12.0.0（用于图像处理）
- ✅ **httpx**: 0.28.1（异步 HTTP 客户端）
- ✅ **FastAPI**: 0.115.5
- ✅ **Pydantic**: 2.10.3

### 配置文件 (.env)
```bash
OPENROUTER_API_KEY=sk-or-v1-***
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
IMAGE_GENERATION_MODEL=openai/gpt-5-image-mini
```

---

## 📋 关键修复

### 问题 1: API 端点错误
**错误**: 405 Method Not Allowed for `/images/generations`
**原因**: OpenRouter 不支持标准的 DALL-E `/images/generations` 端点
**解决**: 改用 `/chat/completions` 端点

### 问题 2: 响应结构不匹配
**错误**: 无法在 `content` 中找到图像
**原因**: 图像数据在 `message.images` 数组中，而不是 `content` 中
**解决**: 从 `message.images[0].image_url.url` 提取 base64 编码的图像

### 问题 3: 不支持的参数
**错误**: `temperature` parameter not supported
**原因**: `gpt-5-image-mini` 模型不支持 temperature 参数
**解决**: 移除 temperature 参数

### 问题 4: Content 格式问题
**错误**: 400 Bad Request with structured content
**原因**: 使用了结构化的 content 格式
**解决**: 使用简单的字符串格式 `"Generate an image: {prompt}"`

---

## 🧪 测试结果

### 测试 1: 简化提示词测试
- **场景ID**: `test_scene_001`
- **提示词**: "A cute cat sitting on a red chair, anime style, high quality"
- **结果**: ✅ 成功
- **文件**: `test_scene_001.png` (1.8 MB)
- **尺寸**: 1024x1024

### 测试 2: Stage2 输出测试（三体场景）
- **场景ID**: `scene_001`
- **提示词**: 完整的三体故事场景描述（汪淼在卧室看星空）
- **结果**: ✅ 成功
- **文件**: `scene_001.png` (1.6 MB)
- **尺寸**: 1024x1024

---

## 📁 生成的文件

```
backend/output/images/
├── test_scene_001.png  (1.8 MB) - 简化测试
└── scene_001.png       (1.6 MB) - 三体场景

backend/
└── stage3_output.json  - 生成参数记录
```

---

## 🎨 Stage3 实现要点

### 核心代码逻辑

```python
# 1. 使用聊天完成接口
payload = {
    "model": "openai/gpt-5-image-mini",
    "messages": [
        {
            "role": "user",
            "content": f"Generate an image: {prompt}"
        }
    ],
    "max_tokens": 4000,
}

# 2. 发送请求
response = await client.post(
    f"{base_url}/chat/completions",
    headers=headers,
    json=payload,
)

# 3. 提取 base64 图像
message = result["choices"][0]["message"]
if "images" in message:
    image_url = message["images"][0]["image_url"]["url"]
    # data:image/png;base64,iVBORw0KG...
    base64_data = image_url.split(",")[1]
    image_bytes = base64.b64decode(base64_data)

# 4. 保存图像
image = Image.open(BytesIO(image_bytes))
image.save(filepath, format='PNG')
```

---

## 💰 成本信息

### GPT-5 Image Mini 定价
- **Prompt tokens**: $0.0000025 per token
- **Image generation**: $0.0000025 per token
- **预计单张图像成本**: ~$0.01 - $0.02 USD

### 实际消耗
- **测试 1**: ~3,000 tokens
- **测试 2**: ~3,000 tokens
- **总成本**: < $0.05 USD

---

## 🚀 下一步计划

### 立即可用
- ✅ Stage1: 文本分析 → 场景分镜
- ✅ Stage2: 生成图像提示词
- ✅ Stage3: 图像生成

### 待实现
- ⬜ Stage4: 语音合成（TTS）
- ⬜ Stage5: 视频合成（FFmpeg）
- ⬜ 批量场景图像生成
- ⬜ 角色一致性优化
- ⬜ 图像质量验证
- ⬜ 七牛云存储集成

---

## 📝 使用说明

### 运行简化测试
```bash
conda activate big-niu-backend
cd backend
python test_stage3_simple.py
```

### 运行完整测试
```bash
# 使用 Stage2 输出生成图像
python test_stage3.py
```

### 完整流程测试
```bash
# Stage1 → Stage2 → Stage3
python test_stages.py  # 先生成 Stage2 输出
python test_stage3.py  # 再生成图像
```

---

## ⚠️ 注意事项

1. **API Key**: 确保 `.env` 文件中配置了有效的 OpenRouter API Key
2. **成本控制**: 每次图像生成都会产生费用，测试时使用少量场景
3. **模型限制**: 
   - 不支持 `temperature` 参数
   - 每次请求生成 1 张图像
   - 最大尺寸 1024x1024
4. **超时设置**: 图像生成可能需要 20-40 秒，已设置 120 秒超时
5. **存储空间**: 每张 PNG 约 1-2 MB

---

## 🎉 总结

Stage3 图像生成功能已完全实现并通过测试！

- ✅ 成功集成 OpenRouter API
- ✅ 正确处理 GPT-5 Image Mini 的响应格式
- ✅ 实现 base64 图像解码和保存
- ✅ 生成高质量 1024x1024 图像
- ✅ 完整的错误处理和日志记录

现在可以继续开发 Stage4（语音合成）和 Stage5（视频合成）功能！
