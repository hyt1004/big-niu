#!/bin/bash
#
# Big Niu 任务运行脚本
# 快速启动文本到视频的完整任务
#

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# 打印使用说明
usage() {
    cat << EOF
Big Niu 任务运行器

使用方法:
    $0 [选项]

选项:
    -f, --file FILE       输入文本文件路径
    -t, --text TEXT       直接提供文本内容
    -s, --scenes NUM      场景数量（默认3）
    -n, --name NAME       任务名称
    -l, --list            列出所有任务
    -h, --help            显示此帮助信息

示例:
    # 从文件运行
    $0 --file tests/backend/stage1/mock_input_threebody.txt

    # 从文件运行并指定场景数
    $0 --file story.txt --scenes 5

    # 指定任务名称
    $0 --file story.txt --name "我的故事"

    # 列出所有任务
    $0 --list

    # 使用内置测试文本
    $0

EOF
    exit 0
}

# 检查 Python 环境
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 未安装"
        exit 1
    fi
    
    print_success "Python3 已安装"
}

# 检查依赖
check_dependencies() {
    print_info "检查依赖..."
    
    # 检查 .env 文件
    if [ ! -f "../../backend/.env" ]; then
        print_warning ".env 文件不存在"
        print_info "请创建 backend/.env 文件并配置 API keys"
    else
        print_success ".env 文件存在"
    fi
    
    # 检查 conda 环境
    if command -v conda &> /dev/null; then
        print_success "Conda 已安装"
    else
        print_warning "Conda 未安装，将使用系统 Python"
    fi
}

# 运行任务
run_task() {
    local FILE=""
    local TEXT=""
    local SCENES=3
    local NAME=""
    local LIST=false
    
    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -f|--file)
                FILE="$2"
                shift 2
                ;;
            -t|--text)
                TEXT="$2"
                shift 2
                ;;
            -s|--scenes)
                SCENES="$2"
                shift 2
                ;;
            -n|--name)
                NAME="$2"
                shift 2
                ;;
            -l|--list)
                LIST=true
                shift
                ;;
            -h|--help)
                usage
                ;;
            *)
                print_error "未知参数: $1"
                usage
                ;;
        esac
    done
    
    # 检查环境
    check_python
    check_dependencies
    
    echo ""
    echo "╔═══════════════════════════════════════════════════════════╗"
    echo "║              Big Niu - 任务运行器                          ║"
    echo "╚═══════════════════════════════════════════════════════════╝"
    echo ""
    
    # 构建命令
    CMD="python3 run_task.py"
    
    if [ "$LIST" = true ]; then
        # 列出任务
        CMD="python3 test_full_task.py --mode list"
    elif [ -n "$FILE" ]; then
        # 从文件运行
        CMD="$CMD --file \"$FILE\" --scenes $SCENES"
        if [ -n "$NAME" ]; then
            CMD="$CMD --name \"$NAME\""
        fi
    elif [ -n "$TEXT" ]; then
        # 从文本运行
        CMD="$CMD --text \"$TEXT\" --scenes $SCENES"
        if [ -n "$NAME" ]; then
            CMD="$CMD --name \"$NAME\""
        fi
    else
        # 使用内置测试文本
        print_info "使用内置测试文本..."
        CMD="python3 test_full_task.py"
    fi
    
    # 执行命令
    print_info "执行命令: $CMD"
    echo ""
    
    eval $CMD
    
    if [ $? -eq 0 ]; then
        echo ""
        print_success "任务执行成功！"
    else
        echo ""
        print_error "任务执行失败"
        exit 1
    fi
}

# 主函数
main() {
    if [ $# -eq 0 ]; then
        # 无参数，运行默认测试
        run_task
    else
        # 有参数，解析并运行
        run_task "$@"
    fi
}

# 运行主函数
main "$@"
