# Big Niu 后端API文档

## 概述

智能文字生成视频系统的后端API，支持多客户端并发访问，提供完整的客户端管理、配置管理、提示词管理、小说提交、分镜表管理和视频生成功能。

## 技术栈

- **框架**: FastAPI
- **数据验证**: Pydantic
- **异步支持**: 完全异步设计
- **数据存储**: JSON文件存储
- **CORS支持**: 支持前端跨域访问

## API基础URL

```
http://localhost:8000/api/v1/bigniu
```

## 模块说明

### 1. 客户端管理 (`/client`)

- `POST /client/register` - 注册新客户端
- `POST /client/heartbeat/{client_id}` - 发送心跳
- `GET /client/sessions` - 获取所有会话
- `GET /client/status/{client_id}` - 获取客户端状态
- `GET /client/stats` - 获取会话统计
- `POST /client/cleanup/{client_id}` - 清理指定客户端
- `POST /client/cleanup/expired` - 清理过期客户端
- `GET /client/online` - 获取在线客户端
- `GET /client/offline` - 获取离线客户端

### 2. 音视频配置 (`/config/audio-video`)

- `GET /config/audio-video/{client_id}` - 获取音视频配置
- `POST /config/audio-video/{client_id}` - 保存音视频配置

### 3. 模型配置 (`/config/model`)

- `GET /config/model/{client_id}` - 获取模型配置
- `POST /config/model/{client_id}` - 保存模型配置（自动生成提示词）

### 4. 提示词管理 (`/prompts`)

- `GET /prompts/{client_id}` - 获取所有提示词
- `POST /prompts/{client_id}` - 保存用户提示词

### 5. 小说提交 (`/novel`)

- `POST /novel/submit/{client_id}` - 提交小说文本

### 6. 分镜表管理 (`/storyboard`)

- `GET /storyboard/{client_id}` - 获取分镜表
- `POST /storyboard/{client_id}` - 保存分镜表
- `GET /storyboard/examples` - 获取分镜表示例

### 7. 图片管理 (`/images`)

- `GET /images/{client_id}` - 获取图片列表
- `POST /images/{client_id}` - 上传图片
- `GET /images/test/{filename}` - 获取测试图片
- `GET /images/{client_id}/{filename}` - 获取客户端图片

### 8. 视频管理 (`/video`)

- `POST /video/generate/{client_id}` - 生成视频
- `GET /video/status/{client_id}` - 获取视频状态
- `GET /video/download/{client_id}` - 下载视频

## 使用流程

1. **注册客户端**: 调用 `/client/register` 获取 `client_id`
2. **配置设置**: 设置音视频配置和模型配置
3. **提交内容**: 提交小说文本，自动生成分镜表
4. **生成视频**: 调用视频生成接口
5. **保持在线**: 定期发送心跳保持客户端在线

## 完整API文档

访问 http://localhost:8000/docs 查看Swagger UI文档
访问 http://localhost:8000/redoc 查看ReDoc文档

## 数据存储

所有数据存储在 `configs/` 目录下：
- `configs/sessions.json` - 会话信息
- `configs/clients/{client_id}/` - 客户端数据目录
  - `audio_video_config.json` - 音视频配置
  - `model_config.json` - 模型配置
  - `user_prompts.json` - 用户提示词
  - `generated_prompts.json` - 生成的提示词
  - `storyboard.json` - 分镜表
  - `video_info.json` - 视频信息
  - `processing_log.json` - 处理日志
