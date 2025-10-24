# API 接口规范

## 基础信息

- **Base URL**: `http://localhost:8000/api/v1`
- **认证方式**: JWT Token
- **数据格式**: JSON
- **字符编码**: UTF-8

## 通用响应格式

### 成功响应

```json
{
  "success": true,
  "data": {},
  "message": "操作成功"
}
```

### 错误响应

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述",
    "details": {}
  }
}
```

## 错误码

| 错误码 | HTTP 状态码 | 说明 |
|--------|------------|------|
| `INVALID_INPUT` | 400 | 请求参数无效 |
| `UNAUTHORIZED` | 401 | 未授权 |
| `FORBIDDEN` | 403 | 禁止访问 |
| `NOT_FOUND` | 404 | 资源不存在 |
| `RATE_LIMIT_EXCEEDED` | 429 | 请求频率超限 |
| `INTERNAL_ERROR` | 500 | 服务器内部错误 |
| `SERVICE_UNAVAILABLE` | 503 | 服务不可用 |

## API 端点

### 1. 创建动漫生成任务

**端点**: `POST /tasks`

**请求头**:
```
Content-Type: application/json
Authorization: Bearer {token}
```

**请求体**:
```json
{
  "novel_text": "这是一段小说文本...",
  "options": {
    "style": "anime",
    "aspect_ratio": "16:9",
    "duration_per_scene": 5,
    "voice_speed": 1.0,
    "subtitle_enabled": true
  }
}
```

**参数说明**:
- `novel_text` (string, required): 小说文本内容
- `options` (object, optional): 生成选项
  - `style` (string): 画风样式，可选值: `anime`, `manga`, `realistic`
  - `aspect_ratio` (string): 视频比例，可选值: `16:9`, `4:3`, `9:16`
  - `duration_per_scene` (number): 每个场景持续时间（秒）
  - `voice_speed` (number): 语音速度倍数，范围 0.5-2.0
  - `subtitle_enabled` (boolean): 是否启用字幕

**响应** (201 Created):
```json
{
  "success": true,
  "data": {
    "task_id": "task_123456",
    "status": "pending",
    "created_at": "2025-10-24T12:00:00Z"
  }
}
```

### 2. 查询任务状态

**端点**: `GET /tasks/{task_id}`

**请求头**:
```
Authorization: Bearer {token}
```

**响应** (200 OK):
```json
{
  "success": true,
  "data": {
    "task_id": "task_123456",
    "status": "processing",
    "progress": 45,
    "current_step": "生成角色图像",
    "created_at": "2025-10-24T12:00:00Z",
    "updated_at": "2025-10-24T12:05:00Z",
    "result": null
  }
}
```

**状态说明**:
- `pending`: 等待处理
- `processing`: 处理中
- `completed`: 完成
- `failed`: 失败

### 3. 获取任务结果

**端点**: `GET /tasks/{task_id}/result`

**请求头**:
```
Authorization: Bearer {token}
```

**响应** (200 OK):
```json
{
  "success": true,
  "data": {
    "task_id": "task_123456",
    "video_url": "https://cdn.qiniu.com/videos/task_123456.mp4",
    "thumbnail_url": "https://cdn.qiniu.com/thumbnails/task_123456.jpg",
    "duration": 120,
    "scenes": [
      {
        "id": "scene_001",
        "image_url": "https://cdn.qiniu.com/scenes/scene_001.png",
        "audio_url": "https://cdn.qiniu.com/audios/scene_001.mp3"
      }
    ],
    "characters": [
      {
        "name": "角色A",
        "image_url": "https://cdn.qiniu.com/characters/character_a.png"
      }
    ]
  }
}
```

### 4. 取消任务

**端点**: `DELETE /tasks/{task_id}`

**请求头**:
```
Authorization: Bearer {token}
```

**响应** (200 OK):
```json
{
  "success": true,
  "message": "任务已取消"
}
```

### 5. 获取任务列表

**端点**: `GET /tasks`

**请求头**:
```
Authorization: Bearer {token}
```

**查询参数**:
- `status` (string, optional): 按状态筛选
- `page` (number, optional): 页码，默认 1
- `page_size` (number, optional): 每页数量，默认 10

**响应** (200 OK):
```json
{
  "success": true,
  "data": {
    "tasks": [
      {
        "task_id": "task_123456",
        "status": "completed",
        "created_at": "2025-10-24T12:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "page_size": 10,
      "total": 25,
      "total_pages": 3
    }
  }
}
```

### 6. WebSocket 进度推送

**端点**: `ws://localhost:8000/ws/tasks/{task_id}`

**连接参数**:
```
token={jwt_token}
```

**服务器推送消息**:
```json
{
  "type": "progress",
  "data": {
    "task_id": "task_123456",
    "status": "processing",
    "progress": 60,
    "current_step": "生成场景画面",
    "message": "正在生成第 3/5 个场景"
  }
}
```

**消息类型**:
- `progress`: 进度更新
- `completed`: 任务完成
- `failed`: 任务失败

## 速率限制

| 端点 | 限制 |
|------|------|
| `POST /tasks` | 每用户 10 次/小时 |
| `GET /tasks` | 每用户 100 次/小时 |
| `GET /tasks/{task_id}` | 每用户 1000 次/小时 |

## 认证

### 获取 Token

**端点**: `POST /auth/login`

**请求体**:
```json
{
  "username": "user@example.com",
  "password": "password123"
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer",
    "expires_in": 3600
  }
}
```

### 使用 Token

在请求头中添加:
```
Authorization: Bearer {access_token}
```

## 示例代码

### Python

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"
token = "your_jwt_token"

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

data = {
    "novel_text": "这是一段小说文本...",
    "options": {
        "style": "anime",
        "aspect_ratio": "16:9"
    }
}

response = requests.post(f"{BASE_URL}/tasks", json=data, headers=headers)
result = response.json()
task_id = result["data"]["task_id"]

print(f"任务创建成功: {task_id}")

while True:
    status_response = requests.get(f"{BASE_URL}/tasks/{task_id}", headers=headers)
    status = status_response.json()["data"]["status"]
    
    if status == "completed":
        result_response = requests.get(f"{BASE_URL}/tasks/{task_id}/result", headers=headers)
        video_url = result_response.json()["data"]["video_url"]
        print(f"视频生成完成: {video_url}")
        break
    elif status == "failed":
        print("任务失败")
        break
    
    time.sleep(5)
```

### JavaScript

```javascript
const BASE_URL = "http://localhost:8000/api/v1";
const token = "your_jwt_token";

async function createTask() {
  const response = await fetch(`${BASE_URL}/tasks`, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${token}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      novel_text: "这是一段小说文本...",
      options: {
        style: "anime",
        aspect_ratio: "16:9"
      }
    })
  });
  
  const result = await response.json();
  return result.data.task_id;
}

async function pollTaskStatus(taskId) {
  while (true) {
    const response = await fetch(`${BASE_URL}/tasks/${taskId}`, {
      headers: {
        "Authorization": `Bearer ${token}`
      }
    });
    
    const result = await response.json();
    const status = result.data.status;
    
    if (status === "completed") {
      const resultResponse = await fetch(`${BASE_URL}/tasks/${taskId}/result`, {
        headers: {
          "Authorization": `Bearer ${token}`
        }
      });
      
      const resultData = await resultResponse.json();
      console.log("视频生成完成:", resultData.data.video_url);
      break;
    } else if (status === "failed") {
      console.log("任务失败");
      break;
    }
    
    await new Promise(resolve => setTimeout(resolve, 5000));
  }
}

const taskId = await createTask();
await pollTaskStatus(taskId);
```

## 测试环境

- **测试服务器**: `http://test.bigniu.com/api/v1`
- **测试账号**: `test@bigniu.com` / `test123`
- **API 文档**: `http://localhost:8000/docs` (Swagger UI)
- **ReDoc**: `http://localhost:8000/redoc`
