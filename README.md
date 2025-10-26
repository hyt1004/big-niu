# Big Niu - 智能动漫生成系统

[![七牛云 Hackathon](https://img.shields.io/badge/七牛云-Hackathon-blue)](https://www.qiniu.com/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## 项目概述

Big Niu 是一个基于 AI 的智能动漫生成系统，能够自动将小说文本转换为包含画面、配音和字幕的动漫视频。本项目为七牛云 Hackathon 参赛作品。

## Demo样例

### 生成视频示例

基于下述输入文本生成的动漫视频，点击链接播放：
https://github.com/user-attachments/assets/86758807-06da-419c-aa63-00bf84f323f4

如果视频无法播放，请在该issue 查看：https://github.com/hyt1004/big-niu/issues/46

*注：该视频展示了系统如何将小说文本转换为包含角色对话、场景画面、配音和字幕的完整动漫视频。*

### 输入文本示例

以下是一个基于《三体》小说的输入文本示例：

```
深夜，汪淼站在窗前，望着天空中闪烁的星星。最近几天，他总是被一些奇怪的现象困扰着。每当他闭上眼睛，就会看到一串神秘的数字在眼前跳动。

"这到底是什么？"汪淼自言自语道，额头上渗出了细密的汗珠。

第二天，汪淼来到实验室，决定用科学的方法来解开这个谜团。他打开了显微镜，但令他震惊的是，在镜头里，那串数字再次出现了。

"不可能！"他惊呼道。

就在这时，他的助手小李走了进来。"汪教授，您今天看起来不太好。"

"我遇到了一些奇怪的事情。"汪淼说着，将最近的异常告诉了小李。

小李听完后，脸色变得凝重："汪教授，我建议您去见一个人。她叫叶文洁，是红岸基地的前工程师。"

几天后，汪淼驱车来到了郊外的一座老房子前。门开了，一位满头银发但目光深邃的老人站在门口。

"叶文洁教授，我是汪淼。"他说道。

"我知道你会来。"叶文洁平静地说，"进来吧，有些事情，是时候让你知道了。"

房间里，叶文洁给汪淼倒了一杯茶，然后缓缓开口："这个宇宙，远比你想象的要复杂。"

汪淼听着叶文洁讲述的故事，关于红岸基地，关于向太空发送的信号，关于那个来自遥远星系的回应。他感到自己的世界观正在崩塌。

"所以，那串数字是..."汪淼的声音颤抖着。

"是倒计时。"叶文洁说，"三体文明正在接近地球。"
```

### 核心功能

- **智能角色生成**：基于小说描述自动生成角色形象，并在整个动漫中保持角色一致性
- **场景画面生成**：根据剧情自动生成对应的场景和画面
- **智能配音**：自动生成角色对话和旁白的语音
- **字幕同步**：生成与语音同步的中文字幕
- **视频合成**：将画面、配音和字幕合成为完整的动漫视频

## 技术架构

```
┌─────────────┐
│   前端界面   │  React + TypeScript
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   后端服务   │  FastAPI + Python
└──────┬──────┘
       │
       ├─────────────────────┬──────────────────┬──────────────────┐
       ▼                     ▼                  ▼                  ▼
┌──────────┐        ┌─────────────┐    ┌─────────────┐   ┌─────────────┐
│ 剧本解析 │        │ 图像生成    │    │ 语音合成    │   │ 视频合成    │
│ (NLP)    │        │ (Stable     │    │ (TTS)       │   │ (FFmpeg)    │
│          │        │  Diffusion) │    │             │   │             │
└──────────┘        └─────────────┘    └─────────────┘   └─────────────┘
```

## 项目结构

```
big-niu/
├── README.md                 # 项目说明文档
├── .gitignore               # Git 忽略配置
├── frontend/                # 前端项目
│   ├── src/                # 前端源代码
│   ├── public/             # 静态资源
│   ├── package.json        # 前端依赖配置
│   └── README.md           # 前端说明文档
├── backend/                 # 后端项目
│   ├── app/                # 应用主目录
│   │   ├── api/           # API 路由
│   │   ├── services/      # 业务逻辑
│   │   ├── models/        # 数据模型
│   │   └── utils/         # 工具函数
│   ├── requirements.txt    # Python 依赖
│   └── README.md           # 后端说明文档
├── docs/                    # 项目文档
│   ├── architecture.md     # 架构设计文档
│   ├── api-spec.md         # API 接口规范
│   ├── dev-guide.md        # 开发指南
│   └── tech-stack.md       # 技术栈说明
├── assets/                  # 资源文件
│   ├── images/             # 图片资源
│   └── videos/             # 视频示例
└── tests/                   # 测试文件
    ├── frontend/           # 前端测试
    └── backend/            # 后端测试
```

## 快速开始

### 环境要求

- **Node.js**: >= 18.0.0
- **Python**: >= 3.10
- **Docker**: >= 20.0 (可选)

### 前端安装

```bash
cd frontend
npm install
npm run dev
```

前端服务将在 `http://localhost:5173` 启动

### 后端安装

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

后端服务将在 `http://localhost:8000` 启动

### Docker 部署（可选）

```bash
docker-compose up -d
```

## 使用说明

1. 访问前端界面 `http://localhost:5173`
2. 在文本框中输入小说内容或剧情片段
3. 点击"生成动漫"按钮
4. 等待 AI 处理（包括角色生成、场景绘制、配音等）
5. 预览并下载生成的动漫视频

## 技术栈

### 前端
- **框架**: React 18 + TypeScript
- **构建工具**: Vite
- **UI 组件**: Ant Design / Material-UI
- **状态管理**: Zustand / Redux
- **HTTP 客户端**: Axios

### 后端
- **框架**: FastAPI
- **AI 模型**:
  - 文本处理: GPT-4 / 通义千问
  - 图像生成: Stable Diffusion / DALL-E
  - 语音合成: Azure TTS / 阿里云 TTS
- **视频处理**: FFmpeg
- **任务队列**: Celery + Redis
- **数据库**: PostgreSQL / MongoDB

### 部署
- **容器化**: Docker + Docker Compose
- **云存储**: 七牛云对象存储
- **CI/CD**: GitHub Actions

## 开发规范

请参阅 [docs/dev-guide.md](docs/dev-guide.md) 了解详细的开发规范。

### 代码风格

- **前端**: ESLint + Prettier
- **后端**: Black + Flake8 + isort
- **提交规范**: Conventional Commits

### Git 工作流

```bash
# 创建功能分支
git checkout -b feature/your-feature-name

# 提交代码
git add .
git commit -m "feat: add new feature"

# 推送到远程
git push origin feature/your-feature-name

# 创建 Pull Request
```

## 团队成员

- **成员 1**: 前端开发 + UI/UX
- **成员 2**: 后端开发 + AI 模型集成
- **成员 3**: 全栈 + DevOps

## 里程碑

- [x] 项目初始化和架构设计
- [ ] 前端界面开发
- [ ] 后端 API 开发
- [ ] AI 模型集成
  - [ ] 文本解析和角色提取
  - [ ] 角色一致性图像生成
  - [ ] 语音合成
- [ ] 视频合成功能
- [ ] 测试和优化
- [ ] 部署上线

## 许可证

MIT License

## 联系方式

如有问题或建议，请通过 Issue 或 Pull Request 与我们联系。

---

**Built with ❤️ for 七牛云 Hackathon**
