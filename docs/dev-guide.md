# 开发指南

## 开发环境搭建

### 前端开发环境

1. **安装 Node.js**
   ```bash
   # 推荐使用 nvm 管理 Node.js 版本
   nvm install 18
   nvm use 18
   ```

2. **安装依赖**
   ```bash
   cd frontend
   npm install
   ```

3. **启动开发服务器**
   ```bash
   npm run dev
   ```

4. **构建生产版本**
   ```bash
   npm run build
   ```

### 后端开发环境

1. **安装 Python**
   ```bash
   # 推荐使用 pyenv 管理 Python 版本
   pyenv install 3.10.0
   pyenv local 3.10.0
   ```

2. **创建虚拟环境**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **启动开发服务器**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### 数据库设置

1. **安装 PostgreSQL**
   ```bash
   # macOS
   brew install postgresql@15
   brew services start postgresql@15
   
   # Ubuntu
   sudo apt-get install postgresql-15
   sudo service postgresql start
   ```

2. **创建数据库**
   ```bash
   createdb bigniu_dev
   ```

3. **运行迁移**
   ```bash
   cd backend
   alembic upgrade head
   ```

### Redis 设置

```bash
# macOS
brew install redis
brew services start redis

# Ubuntu
sudo apt-get install redis-server
sudo service redis-server start
```

## 代码规范

### 前端代码规范

#### 文件命名
- 组件文件: `PascalCase.tsx` (例: `VideoPlayer.tsx`)
- 工具文件: `camelCase.ts` (例: `apiClient.ts`)
- 样式文件: `kebab-case.css` (例: `video-player.css`)

#### 组件结构
```tsx
import React, { useState, useEffect } from 'react';
import './ComponentName.css';

interface ComponentNameProps {
  prop1: string;
  prop2?: number;
}

export const ComponentName: React.FC<ComponentNameProps> = ({ prop1, prop2 = 0 }) => {
  const [state, setState] = useState<string>('');

  useEffect(() => {
    // Side effects
  }, []);

  const handleEvent = () => {
    // Event handler logic
  };

  return (
    <div className="component-name">
      <h1>{prop1}</h1>
      <button onClick={handleEvent}>Click me</button>
    </div>
  );
};
```

#### TypeScript 规范
- 所有 props 和 state 必须定义类型
- 避免使用 `any`，使用 `unknown` 替代
- 优先使用接口 (`interface`) 而不是类型别名 (`type`)
- 使用严格模式 (`strict: true`)

#### 代码风格
```javascript
// ✅ 好的实践
const fetchData = async () => {
  try {
    const response = await api.get('/data');
    return response.data;
  } catch (error) {
    console.error('Failed to fetch data:', error);
    throw error;
  }
};

// ❌ 避免的实践
const fetchData = async () => {
  const response = await api.get('/data');
  return response.data;
};
```

### 后端代码规范

#### 文件命名
- 模块文件: `snake_case.py` (例: `video_service.py`)
- 类名: `PascalCase` (例: `VideoService`)
- 函数名: `snake_case` (例: `generate_video`)

#### API 路由结构
```python
from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.schemas import TaskCreate, TaskResponse
from app.services import TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/", response_model=TaskResponse, status_code=201)
async def create_task(
    task: TaskCreate,
    service: TaskService = Depends()
):
    """
    创建新的动漫生成任务
    
    Args:
        task: 任务创建数据
        service: 任务服务依赖注入
    
    Returns:
        TaskResponse: 创建的任务信息
    """
    try:
        return await service.create_task(task)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

#### 类型注解
```python
from typing import List, Optional, Dict, Any

def process_novel(
    text: str,
    options: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """处理小说文本并返回场景列表"""
    if options is None:
        options = {}
    
    scenes: List[Dict[str, Any]] = []
    return scenes
```

#### 错误处理
```python
# ✅ 好的实践
from app.exceptions import ValidationError, ServiceUnavailableError

async def generate_image(prompt: str) -> str:
    try:
        result = await sd_client.generate(prompt)
        return result.url
    except ValidationError as e:
        logger.error(f"Invalid prompt: {e}")
        raise HTTPException(status_code=400, detail="Invalid prompt")
    except ServiceUnavailableError as e:
        logger.error(f"Service unavailable: {e}")
        raise HTTPException(status_code=503, detail="AI service unavailable")
```

### Git 提交规范

使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范:

```bash
<type>(<scope>): <subject>

<body>

<footer>
```

**类型 (type)**:
- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档更新
- `style`: 代码格式调整（不影响功能）
- `refactor`: 重构代码
- `perf`: 性能优化
- `test`: 测试相关
- `chore`: 构建/工具链相关

**示例**:
```bash
feat(frontend): add video player component

- Implement video player with controls
- Add fullscreen support
- Support subtitle display

Closes #123
```

## 分支管理

### 分支命名规范

- `main`: 主分支，受保护
- `develop`: 开发分支
- `feature/功能名`: 功能分支 (例: `feature/video-player`)
- `fix/问题描述`: 修复分支 (例: `fix/login-error`)
- `hotfix/紧急修复`: 紧急修复分支
- `release/版本号`: 发布分支 (例: `release/v1.0.0`)

### 工作流程

1. **创建功能分支**
   ```bash
   git checkout -b feature/new-feature develop
   ```

2. **开发和提交**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

3. **保持同步**
   ```bash
   git fetch origin
   git rebase origin/develop
   ```

4. **推送到远程**
   ```bash
   git push origin feature/new-feature
   ```

5. **创建 Pull Request**
   - 在 GitHub 上创建 PR
   - 至少需要 1 个团队成员 review
   - CI 测试必须通过
   - 解决所有 review comments

6. **合并**
   ```bash
   # 使用 squash merge 保持提交历史清晰
   git checkout develop
   git merge --squash feature/new-feature
   git commit -m "feat: add new feature"
   ```

## 测试规范

### 前端测试

使用 Vitest + React Testing Library

```tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { VideoPlayer } from './VideoPlayer';

describe('VideoPlayer', () => {
  it('should render video player', () => {
    render(<VideoPlayer src="test.mp4" />);
    const player = screen.getByRole('video');
    expect(player).toBeInTheDocument();
  });

  it('should play video when play button clicked', () => {
    render(<VideoPlayer src="test.mp4" />);
    const playButton = screen.getByRole('button', { name: /play/i });
    fireEvent.click(playButton);
    const player = screen.getByRole('video') as HTMLVideoElement;
    expect(player.paused).toBe(false);
  });
});
```

**运行测试**:
```bash
npm test
npm run test:coverage
```

### 后端测试

使用 pytest + httpx

```python
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_create_task():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/tasks",
            json={
                "novel_text": "测试文本",
                "options": {"style": "anime"}
            },
            headers={"Authorization": "Bearer test_token"}
        )
    
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert "task_id" in data["data"]

@pytest.mark.asyncio
async def test_get_task_status():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            "/api/v1/tasks/task_123",
            headers={"Authorization": "Bearer test_token"}
        )
    
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["status"] in ["pending", "processing", "completed", "failed"]
```

**运行测试**:
```bash
pytest
pytest --cov=app --cov-report=html
```

## 代码审查清单

### Pull Request 检查项

- [ ] 代码符合项目规范
- [ ] 所有测试通过
- [ ] 代码覆盖率 >= 80%
- [ ] 没有遗留的 TODO 或 FIXME
- [ ] 文档已更新（如果需要）
- [ ] 没有敏感信息（API key, 密码等）
- [ ] 性能影响已评估
- [ ] 错误处理完善
- [ ] 日志记录适当
- [ ] 可维护性良好

### Review 关注点

1. **功能性**: 代码是否实现了预期功能
2. **正确性**: 逻辑是否正确，边界情况是否处理
3. **性能**: 是否有性能问题或可优化的地方
4. **安全性**: 是否有安全漏洞
5. **可读性**: 代码是否清晰易懂
6. **可维护性**: 代码是否易于维护和扩展

## 调试技巧

### 前端调试

1. **使用 React DevTools**
   - 安装浏览器扩展
   - 检查组件层级和 props/state

2. **使用 console 调试**
   ```javascript
   console.log('Debug:', value);
   console.table(arrayData);
   console.time('operation');
   // ... code
   console.timeEnd('operation');
   ```

3. **网络请求调试**
   - 使用浏览器 Network 标签
   - 或使用 axios 拦截器记录请求

### 后端调试

1. **使用 pdb**
   ```python
   import pdb; pdb.set_trace()
   ```

2. **使用日志**
   ```python
   import logging
   logger = logging.getLogger(__name__)
   logger.debug("Debug message")
   logger.info("Info message")
   logger.error("Error message")
   ```

3. **FastAPI 交互式文档**
   - 访问 `http://localhost:8000/docs`
   - 直接测试 API 端点

## 性能优化建议

### 前端优化

1. **代码分割**
   ```javascript
   const LazyComponent = React.lazy(() => import('./LazyComponent'));
   ```

2. **使用 memo 避免不必要的重渲染**
   ```javascript
   const MemoizedComponent = React.memo(ExpensiveComponent);
   ```

3. **优化图片加载**
   ```javascript
   <img loading="lazy" src="image.jpg" alt="description" />
   ```

### 后端优化

1. **使用异步操作**
   ```python
   async def process_task():
       results = await asyncio.gather(
           generate_image(),
           generate_audio(),
           generate_subtitle()
       )
   ```

2. **数据库查询优化**
   ```python
   # 使用 select_related 减少查询次数
   tasks = await Task.objects.select_related('user').all()
   ```

3. **缓存频繁访问的数据**
   ```python
   @lru_cache(maxsize=128)
   def get_config(key: str) -> str:
       return config[key]
   ```

## 文档编写

### 代码注释

```python
def generate_anime(novel_text: str, options: dict) -> str:
    """
    生成动漫视频
    
    Args:
        novel_text: 小说文本内容
        options: 生成选项，包含:
            - style: 画风样式
            - aspect_ratio: 视频比例
            - duration_per_scene: 每个场景持续时间
    
    Returns:
        str: 生成的视频 URL
    
    Raises:
        ValueError: 当 novel_text 为空时
        ServiceError: 当 AI 服务不可用时
    
    Example:
        >>> video_url = generate_anime(
        ...     "一个关于冒险的故事...",
        ...     {"style": "anime", "aspect_ratio": "16:9"}
        ... )
    """
    pass
```

### API 文档

使用 FastAPI 自动生成的文档，但需要添加详细的描述:

```python
@router.post(
    "/",
    response_model=TaskResponse,
    status_code=201,
    summary="创建动漫生成任务",
    description="根据输入的小说文本创建一个新的动漫生成任务",
    responses={
        201: {"description": "任务创建成功"},
        400: {"description": "请求参数无效"},
        429: {"description": "请求频率超限"}
    }
)
async def create_task(task: TaskCreate):
    pass
```

## 常见问题

### Q: 如何处理跨域问题？

**A**: 在后端配置 CORS:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Q: 如何管理环境变量？

**A**: 使用 `.env` 文件:
```bash
# .env
DATABASE_URL=postgresql://user:pass@localhost/bigniu
REDIS_URL=redis://localhost:6379
QINIU_ACCESS_KEY=your_access_key
QINIU_SECRET_KEY=your_secret_key
```

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    redis_url: str
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### Q: 如何处理大文件上传？

**A**: 使用流式上传:
```python
from fastapi import UploadFile

@router.post("/upload")
async def upload_file(file: UploadFile):
    async with aiofiles.open(f"uploads/{file.filename}", "wb") as f:
        while chunk := await file.read(1024 * 1024):  # 1MB chunks
            await f.write(chunk)
```

## 资源链接

- [React 文档](https://react.dev/)
- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [TypeScript 文档](https://www.typescriptlang.org/)
- [Python 风格指南](https://peps.python.org/pep-0008/)
- [七牛云文档](https://developer.qiniu.com/)
