#!/bin/bash
# Big Niu 快速测试脚本

echo "🚀 Big Niu 快速测试"
echo "===================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查是否在正确的目录
if [ ! -f "run_all_tests.py" ]; then
    echo -e "${RED}❌ 错误: 请在 tests/backend/ 目录下运行此脚本${NC}"
    exit 1
fi

# 检查 conda 环境
if ! conda info --envs | grep -q "big-niu-backend"; then
    echo -e "${RED}❌ 错误: 找不到 big-niu-backend conda 环境${NC}"
    exit 1
fi

echo -e "${YELLOW}📋 测试选项:${NC}"
echo "  1. 运行完整流程测试 (Stage1 → Stage2 → Stage3)"
echo "  2. 运行 Stage1 测试"
echo "  3. 运行 Stage2 测试"
echo "  4. 运行 Stage3 测试"
echo "  5. 运行所有 pytest 测试"
echo ""

read -p "选择测试 (1-5): " choice

case $choice in
    1)
        echo -e "${GREEN}运行完整流程测试...${NC}"
        conda run -n big-niu-backend python run_all_tests.py
        ;;
    2)
        echo -e "${GREEN}运行 Stage1 测试...${NC}"
        conda run -n big-niu-backend pytest stage1/ -v
        ;;
    3)
        echo -e "${GREEN}运行 Stage2 测试...${NC}"
        conda run -n big-niu-backend pytest stage2/ -v
        ;;
    4)
        echo -e "${GREEN}运行 Stage3 测试...${NC}"
        conda run -n big-niu-backend pytest stage3/ -v
        ;;
    5)
        echo -e "${GREEN}运行所有 pytest 测试...${NC}"
        conda run -n big-niu-backend pytest . -v
        ;;
    *)
        echo -e "${RED}❌ 无效选择${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}✅ 测试完成！${NC}"
