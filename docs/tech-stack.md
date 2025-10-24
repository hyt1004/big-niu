# 技术栈说明

## 概览

本项目采用现代化的全栈技术架构，前端使用 React + TypeScript，后端使用 FastAPI + Python，AI 能力依托多个开源和商业模型。

## 前端技术栈

### 核心框架

#### React 18
- **版本**: 18.x
- **选择理由**:
  - 组件化开发，代码复用性强
  - 虚拟 DOM 提供高性能
  - 生态系统成熟，社区活跃
  - Hooks API 简化状态管理
- **主要特性**:
  - Concurrent Mode 并发渲染
  - Automatic Batching 自动批处理
  - Suspense 组件懒加载

#### TypeScript 5.x
- **选择理由**:
  - 静态类型检查，减少运行时错误
  - 提供更好的 IDE 支持和代码补全
  - 提高代码可维护性
  - 与 React 深度集成
- **配置**:
  ```json
  {
    "compilerOptions": {
      "target": "ES2020",
      "strict": true,
      "jsx": "react-jsx"
    }
  }
  ```

### 构建工具

#### Vite 5.x
- **选择理由**:
  - 极快的冷启动速度
  - 基于 ESM 的热模块替换 (HMR)
  - 开箱即用的 TypeScript 支持
  - 优化的生产构建
- **插件**:
  - `@vitejs/plugin-react`: React 支持
  - `vite-plugin-pwa`: PWA 支持

### UI 框架

#### Ant Design 或 Material-UI
- **Ant Design**:
  - 丰富的企业级组件
  - 完善的国际化支持
  - 定制化主题系统
  
- **Material-UI**:
  - Google Material Design 设计语言
  - 响应式设计
  - 可访问性支持

**组件库选择**: 根据团队偏好和设计风格在 Hackathon 初期确定

### 状态管理

#### Zustand
- **选择理由**:
  - API 简洁，学习曲线低
  - 无需样板代码
  - 支持 TypeScript
  - 轻量级（< 1KB）
- **示例**:
  ```typescript
  import create from 'zustand';
  
  interface TaskStore {
    tasks: Task[];
    addTask: (task: Task) => void;
  }
  
  const useTaskStore = create<TaskStore>((set) => ({
    tasks: [],
    addTask: (task) => set((state) => ({ 
      tasks: [...state.tasks, task] 
    })),
  }));
  ```

### HTTP 客户端

#### Axios
- **选择理由**:
  - 支持 Promise API
  - 浏览器和 Node.js 通用
  - 支持请求和响应拦截器
  - 自动转换 JSON 数据
- **配置**:
  ```typescript
  import axios from 'axios';
  
  const apiClient = axios.create({
    baseURL: 'http://localhost:8000/api/v1',
    timeout: 30000,
  });
  
  apiClient.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  });
  ```

### 代码质量工具

- **ESLint**: JavaScript/TypeScript 代码检查
- **Prettier**: 代码格式化
- **Husky**: Git hooks 管理
- **lint-staged**: 暂存文件检查

## 后端技术栈

### 核心框架

#### FastAPI
- **版本**: 0.104+
- **选择理由**:
  - 高性能，基于 Starlette 和 Pydantic
  - 原生支持异步 (async/await)
  - 自动生成 OpenAPI 文档
  - 强大的数据验证
  - 依赖注入系统
- **关键特性**:
  ```python
  from fastapi import FastAPI, Depends
  from pydantic import BaseModel
  
  app = FastAPI(
      title="Big Niu API",
      description="智能动漫生成系统 API",
      version="1.0.0"
  )
  
  class TaskCreate(BaseModel):
      novel_text: str
      options: dict = {}
  
  @app.post("/tasks")
  async def create_task(task: TaskCreate):
      return {"task_id": "123"}
  ```

### 数据库

#### PostgreSQL 15
- **选择理由**:
  - 成熟可靠的关系型数据库
  - 支持复杂查询和事务
  - JSON 字段支持
  - 强大的扩展生态
- **ORM**: SQLAlchemy 2.0
  ```python
  from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
  from sqlalchemy.orm import DeclarativeBase
  
  engine = create_async_engine(
      "postgresql+asyncpg://user:pass@localhost/bigniu"
  )
  
  class Base(DeclarativeBase):
      pass
  
  class Task(Base):
      __tablename__ = "tasks"
      id = Column(String, primary_key=True)
      status = Column(String)
      created_at = Column(DateTime)
  ```

#### Redis
- **选择理由**:
  - 高性能缓存
  - 支持多种数据结构
  - 消息队列功能
  - 分布式锁
- **用途**:
  - 缓存 AI 生成结果
  - Celery 任务队列后端
  - Session 存储

### 异步任务队列

#### Celery
- **选择理由**:
  - 成熟的分布式任务队列
  - 支持定时任务
  - 任务重试和错误处理
  - 监控和管理工具
- **配置**:
  ```python
  from celery import Celery
  
  celery_app = Celery(
      "bigniu",
      broker="redis://localhost:6379/0",
      backend="redis://localhost:6379/1"
  )
  
  @celery_app.task
  def generate_anime_task(task_id: str, novel_text: str):
      # 异步处理动漫生成
      pass
  ```

### AI 模型集成

#### 文本处理

**选项 1: OpenAI GPT-4**
- **用途**: 剧本解析、角色提取
- **SDK**: `openai`
- **示例**:
  ```python
  import openai
  
  response = openai.ChatCompletion.create(
      model="gpt-4",
      messages=[
          {"role": "system", "content": "你是一个专业的剧本分析师"},
          {"role": "user", "content": f"解析以下小说: {novel_text}"}
      ]
  )
  ```

**选项 2: 阿里云通义千问**
- **优势**: 国内访问速度快
- **SDK**: `dashscope`

#### 图像生成

**选项 1: Stable Diffusion**
- **版本**: SDXL 1.0
- **部署方式**: 
  - 本地部署（需要 GPU）
  - 或使用 Replicate API
- **库**: `diffusers`
- **角色一致性方案**:
  - LoRA (Low-Rank Adaptation) 微调
  - DreamBooth 训练
  - ControlNet 控制
  
**选项 2: DALL-E 3**
- **优势**: 图像质量高，理解能力强
- **限制**: API 调用成本较高

#### 语音合成

**选项 1: Azure TTS**
- **语音质量**: 优秀
- **多音色支持**: 是
- **SDK**: `azure-cognitiveservices-speech`
- **示例**:
  ```python
  import azure.cognitiveservices.speech as speechsdk
  
  speech_config = speechsdk.SpeechConfig(
      subscription=AZURE_KEY,
      region="eastasia"
  )
  synthesizer = speechsdk.SpeechSynthesizer(
      speech_config=speech_config
  )
  ```

**选项 2: 阿里云 TTS**
- **优势**: 国内访问稳定
- **SDK**: `aliyun-python-sdk-nls`

### 视频处理

#### FFmpeg
- **版本**: 6.0+
- **功能**:
  - 图像序列转视频
  - 音视频合成
  - 字幕叠加
  - 视频转码
- **Python 绑定**: `ffmpeg-python`
- **示例**:
  ```python
  import ffmpeg
  
  (
      ffmpeg
      .input('scene_%03d.png', framerate=1)
      .input('audio.mp3')
      .output('output.mp4', vcodec='libx264', acodec='aac')
      .run()
  )
  ```

### 代码质量工具

- **Black**: 代码格式化
- **Flake8**: 代码风格检查
- **isort**: import 语句排序
- **mypy**: 静态类型检查
- **pytest**: 测试框架

## 云服务

### 七牛云

#### 对象存储 (Kodo)
- **用途**: 存储生成的视频、图像、音频
- **SDK**: `qiniu`
- **示例**:
  ```python
  from qiniu import Auth, put_file
  
  q = Auth(ACCESS_KEY, SECRET_KEY)
  token = q.upload_token('bucket-name', 'video.mp4')
  ret, info = put_file(token, 'video.mp4', '/path/to/file')
  ```

#### CDN
- **用途**: 加速视频和图片访问
- **功能**: 自动 HTTPS、全球加速

## 开发工具

### 版本控制
- **Git**: 版本控制
- **GitHub**: 代码托管、CI/CD

### 容器化
- **Docker**: 容器化应用
- **Docker Compose**: 多容器编排
- **示例**:
  ```yaml
  version: '3.8'
  services:
    frontend:
      build: ./frontend
      ports:
        - "5173:5173"
    
    backend:
      build: ./backend
      ports:
        - "8000:8000"
      depends_on:
        - postgres
        - redis
    
    postgres:
      image: postgres:15
      environment:
        POSTGRES_DB: bigniu
    
    redis:
      image: redis:7
  ```

### CI/CD
- **GitHub Actions**: 自动化测试和部署
- **工作流**:
  1. 代码推送
  2. 运行测试
  3. 代码检查
  4. 构建 Docker 镜像
  5. 部署到测试/生产环境

### 监控和日志

#### 日志
- **Loguru**: Python 日志库
- **Winston**: Node.js 日志库

#### 监控
- **Prometheus**: 指标收集
- **Grafana**: 可视化仪表板

## 技术决策记录

### 为什么选择 FastAPI 而不是 Django?
- FastAPI 性能更高（基于异步）
- 自动生成 API 文档
- 更适合构建 API 服务
- 更轻量级，启动更快

### 为什么选择 Zustand 而不是 Redux?
- API 更简洁，学习成本低
- 无需大量样板代码
- 更适合小型项目
- 在 Hackathon 中可以快速上手

### 为什么使用 PostgreSQL 而不是 MongoDB?
- 结构化数据更适合关系型数据库
- 支持事务，数据一致性强
- 查询功能更强大
- 团队更熟悉 SQL

## 技术栈版本矩阵

| 技术 | 版本 | 发布日期 | 稳定性 |
|------|------|---------|--------|
| React | 18.2+ | 2022-06 | 稳定 |
| TypeScript | 5.x | 2023-03 | 稳定 |
| Vite | 5.x | 2023-11 | 稳定 |
| FastAPI | 0.104+ | 2023-10 | 稳定 |
| Python | 3.10+ | 2021-10 | 稳定 |
| PostgreSQL | 15.x | 2022-10 | 稳定 |
| Redis | 7.x | 2022-04 | 稳定 |
| FFmpeg | 6.0+ | 2023-02 | 稳定 |

## 学习资源

### 前端
- [React 官方文档](https://react.dev/)
- [TypeScript 官方文档](https://www.typescriptlang.org/)
- [Vite 官方文档](https://vitejs.dev/)

### 后端
- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [SQLAlchemy 文档](https://docs.sqlalchemy.org/)
- [Celery 文档](https://docs.celeryproject.org/)

### AI/ML
- [Hugging Face Diffusers](https://huggingface.co/docs/diffusers/)
- [OpenAI API 文档](https://platform.openai.com/docs/)
- [FFmpeg 文档](https://ffmpeg.org/documentation.html)

## 未来扩展

可能考虑的技术升级：

1. **前端**:
   - Next.js (SSR/SSG)
   - React Query (服务端状态管理)
   - WebSocket 实时通信

2. **后端**:
   - GraphQL API
   - gRPC 服务间通信
   - Kubernetes 容器编排

3. **AI**:
   - 自托管 Stable Diffusion 集群
   - 模型量化和优化
   - 边缘计算推理
