# Big Niu Frontend

智能动漫生成系统前端界面

## 技术栈

- **框架**: React 18 + TypeScript
- **构建工具**: Vite
- **HTTP 客户端**: Axios
- **样式**: CSS3

## 项目结构

```
frontend/
├── src/
│   ├── components/          # React 组件
│   │   ├── NovelInput.tsx   # 小说文案输入
│   │   ├── ModelConfig.tsx  # 模型配置
│   │   ├── VideoOutput.tsx  # 视频输出
│   │   └── AudioVideoConfig.tsx # 音视频配置
│   ├── types/               # TypeScript 类型定义
│   ├── App.tsx              # 主应用组件
│   ├── App.css              # 主应用样式
│   ├── main.tsx             # 应用入口
│   └── index.css            # 全局样式
├── public/                  # 静态资源
├── index.html               # HTML 模板
├── package.json             # 项目依赖
├── tsconfig.json            # TypeScript 配置
└── vite.config.ts           # Vite 配置

## 快速开始

### 安装依赖

```bash
npm install
```

### 开发模式

```bash
npm run dev
```

应用将在 http://localhost:5173 启动

### 生产构建

```bash
npm run build
```

构建产物将生成在 `dist/` 目录

### 预览构建

```bash
npm run preview
```

## 核心功能

### 1. 小说文案输入 (NovelInput)
- 文本输入区域
- TXT 文件上传
- 生成模型提示词

### 2. 模型配置 (ModelConfig)
- 动漫模式选择（黑白/彩色/插画）
- 时代背景选择（8个选项）
- 随机选项（微调/构图/镜头）
- 参数滑块（气氛/距离/写实/动态）
- 主角描述（5个输入框）

### 3. 视频输出 (VideoOutput)
- 视频播放器
- 加载状态显示
- 视频下载功能

### 4. 音视频配置 (AudioVideoConfig)
- 音频格式（AAC/MP3/WAV/M4A）
- 视频格式（MP4/AVI/MKV/MOV）
- 分辨率（720p/1080p/1440p/4K）
- 帧率（24/30/60 fps）
- 码率设置

## 界面布局

采用两栏布局设计：

- **左栏**: 小说文案输入 + 模型配置
- **右栏**: 视频输出 + 音视频配置

响应式设计，在小屏幕设备上自动切换为单栏布局。

## API 集成

前端通过 Vite 代理与后端通信：

```typescript
// vite.config.ts
proxy: {
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true
  }
}
```

## 开发规范

- 使用 TypeScript 严格模式
- 组件化开发
- Props 类型定义
- CSS 模块化

## 待办事项

- [ ] 集成后端 API
- [ ] 添加错误处理
- [ ] 实现实时生成进度显示
- [ ] 添加表单验证
- [ ] 优化移动端体验
