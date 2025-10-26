#!/bin/bash

# Big Niu 运行脚本

echo "🚀 启动 Big Niu 智能动漫生成系统..."

# 检查环境
echo "📋 检查环境..."

# 检查Python
if ! command -v python &> /dev/null; then
    echo "❌ Python 未安装，请先安装 Python 3.10+"
    exit 1
fi

# 检查Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js 未安装，请先安装 Node.js 18+"
    exit 1
fi

# 检查FFmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "❌ FFmpeg 未安装，请先安装 FFmpeg"
    exit 1
fi

echo "✅ 环境检查通过"

# 创建必要的目录
mkdir -p backend/output/audio
mkdir -p backend/output/videos
mkdir -p backend/output/temp
mkdir -p backend/configs/clients

# 检查环境变量文件
if [ ! -f "backend/.env" ]; then
    echo "⚠️  未找到 .env 文件，正在创建示例配置..."
    cat > backend/.env << EOF
# OpenRouter API Configuration
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# Model Configuration
TEXT_ANALYSIS_MODEL=anthropic/claude-3.5-sonnet
IMAGE_PROMPT_MODEL=anthropic/claude-3.5-sonnet
IMAGE_GENERATION_MODEL=openai/dall-e-3

# Application Configuration
DEFAULT_SCENES_COUNT=10

# Optional: VolcEngine TTS Configuration
# VOLCENGINE_APPID=your_volcengine_appid
# VOLCENGINE_ACCESS_TOKEN=your_volcengine_access_token
# VOLCENGINE_CLUSTER=volcano_tts
EOF
    echo "📝 已创建 .env 示例文件，请编辑并填入真实的API密钥"
fi

# 安装后端依赖
echo "📦 安装后端依赖..."
cd backend
if [ ! -d "venv" ]; then
    echo "创建Python虚拟环境..."
    python -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt
cd ..

# 安装前端依赖
echo "📦 安装前端依赖..."
cd frontend
if [ ! -d "node_modules" ]; then
    npm install
fi
cd ..

echo "🎯 启动服务..."

# 启动后端服务
echo "🔧 启动后端服务 (端口 8000)..."
cd backend
source venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

# 等待后端启动
sleep 3

# 启动前端服务
echo "🎨 启动前端服务 (端口 5173)..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "🎉 Big Niu 系统已启动！"
echo ""
echo "📱 服务地址:"
echo "   前端界面: http://localhost:5173"
echo "   后端API:  http://localhost:8000"
echo "   API文档:  http://localhost:8000/docs"
echo ""
echo "🛑 按 Ctrl+C 停止所有服务"

# 等待用户中断
trap 'echo ""; echo "🛑 正在停止服务..."; kill $BACKEND_PID $FRONTEND_PID; echo "✅ 服务已停止"; exit 0' INT

# 保持脚本运行
wait
