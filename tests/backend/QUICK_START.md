# 🚀 快速开始指南

Big Niu 测试快速上手指南。

---

## ⚡ 30秒快速开始

```bash
# 1. 进入测试目录
cd tests/backend

# 2. 运行完整测试
python run_all_tests.py
```

就这么简单！✨

---

## 📋 测试前准备

### 1. 环境检查

```bash
# 检查 conda 环境
conda info --envs | grep big-niu-backend

# 激活环境
conda activate big-niu-backend

# 检查依赖
conda list | grep -E "fastapi|pydantic|httpx|pillow"
```

### 2. 配置检查

确保 `backend/.env` 文件配置正确：

```bash
# 查看配置（隐藏 API Key）
cat backend/.env | grep -v "API_KEY"
```

必须配置：
- ✅ `OPENROUTER_API_KEY`
- ✅ `IMAGE_GENERATION_MODEL=openai/gpt-5-image-mini`

### 3. 服务检查

```bash
# 检查后端服务是否运行
curl http://localhost:8000/health

# 如果没有运行，启动服务
cd backend
conda run -n big-niu-backend uvicorn app.main:app --reload &
```

---

## 🎯 测试选项

### 选项 1: 完整流程测试 ⭐ 推荐

运行 Stage1 → Stage2 → Stage3 完整流程：

```bash
cd tests/backend
python run_all_tests.py
```

**耗时**: ~2-3 分钟
**成本**: ~$0.02 USD（生成1张图像）

输出：
```
✅ Stage1: 分析了 3 个场景
✅ Stage2: 生成了 3 个提示词
✅ Stage3: 生成了 1 张图像
```

---

### 选项 2: 交互式测试

使用 Shell 脚本选择测试：

```bash
./quick_test.sh
```

选择菜单：
```
1. 运行完整流程测试 (Stage1 → Stage2 → Stage3)
2. 运行 Stage1 测试
3. 运行 Stage2 测试
4. 运行 Stage3 测试
5. 运行所有 pytest 测试
```

---

### 选项 3: 单个 Stage 测试

#### Stage 1: 文本分析

```bash
# Pytest 测试
pytest stage1/ -v

# 或查看测试数据
cat stage1/mock_input_threebody.txt
```

#### Stage 2: 提示词生成

```bash
# Pytest 测试
pytest stage2/ -v
```

#### Stage 3: 图像生成

```bash
# 简化测试（最快）
python stage3/test_stage3_simple.py

# 完整测试（使用 Stage2 输出）
python stage3/test_stage3.py

# Pytest 测试
pytest stage3/test_functional_image_generation.py -v
```

---

### 选项 4: 集成测试

测试多个 Stage 的集成：

```bash
# 完整集成测试
python integration/test_stages.py

# 快速测试
python integration/quick_test.py
```

---

## 📊 查看测试结果

### 1. JSON 输出

```bash
# 查看 Stage1 输出
cat fixtures/stage1_output.json | jq .

# 查看 Stage2 输出
cat fixtures/stage2_output.json | jq .

# 查看 Stage3 输出
cat fixtures/stage3_output.json | jq .
```

### 2. 生成的图像

```bash
# 查看生成的图像
ls -lh fixtures/output/images/

# 在 Mac 上打开图像
open fixtures/output/images/scene_001.png
```

### 3. 完整响应（调试用）

```bash
# 查看完整 API 响应
cat fixtures/full_response.json | jq . | less
```

---

## 🐛 调试问题

### 常见问题 1: API 连接失败

```bash
# 测试 API 连接
python debug/debug_image_gen.py
```

### 常见问题 2: 图像生成失败

```bash
# 查看详细响应
python debug/debug_image_gen2.py

# 检查生成的响应文件
cat full_response.json
```

### 常见问题 3: 环境变量未设置

```bash
# 检查环境变量
cd backend
source .env
echo $OPENROUTER_API_KEY
```

---

## 📈 测试进度追踪

### 当前状态

| Stage | 功能 | 状态 |
|-------|------|------|
| Stage1 | 文本分析 | ✅ 完成 |
| Stage2 | 提示词生成 | ✅ 完成 |
| Stage3 | 图像生成 | ✅ 完成 |
| Stage4 | 语音合成 | ⬜ 待开发 |
| Stage5 | 视频合成 | ⬜ 待开发 |

### 测试覆盖率

- ✅ 单元测试
- ✅ 功能测试
- ✅ 集成测试
- ⬜ E2E 测试（待添加）

---

## 💡 最佳实践

### ✅ DO

- ✅ 测试前检查 API Key
- ✅ 先运行简化测试验证环境
- ✅ 定期清理 `fixtures/output/` 目录
- ✅ 查看测试文档 `README.md`

### ❌ DON'T

- ❌ 不要提交测试输出到 git
- ❌ 不要在生产环境运行测试
- ❌ 不要频繁生成大量图像（成本）
- ❌ 不要硬编码 API Key

---

## 🎓 学习路径

### 1. 初学者

```bash
# 从简单开始
python stage3/test_stage3_simple.py
```

### 2. 进阶者

```bash
# 运行完整流程
python run_all_tests.py
```

### 3. 高级用户

```bash
# 编写自定义测试
# 阅读 README.md 了解详细信息
```

---

## 📞 获取帮助

### 文档

- 📄 [README.md](README.md) - 完整文档
- 📄 [STRUCTURE.md](STRUCTURE.md) - 目录结构
- 📄 [docs/TEST_GUIDE.md](docs/TEST_GUIDE.md) - 测试指南
- 📄 [docs/STAGE3_TEST_SUMMARY.md](docs/STAGE3_TEST_SUMMARY.md) - Stage3 总结

### 命令速查

```bash
# 查看所有测试
pytest --collect-only

# 运行特定测试
pytest -k "test_name" -v

# 查看详细输出
pytest -vv -s

# 停在第一个失败
pytest -x
```

---

## 🎉 成功标志

运行成功后，你应该看到：

```
✅ Stage1: 分析了 3 个场景
✅ Stage2: 生成了 3 个提示词
✅ Stage3: 生成了 1 张图像

🎉 所有测试通过！
```

并在 `fixtures/output/images/` 中看到生成的图像。

---

## 🚀 下一步

1. 查看生成的图像
2. 阅读完整文档
3. 尝试修改测试文本
4. 探索调试工具
5. 开始开发 Stage4/5

---

**祝测试愉快！** 🎊

有问题？查看 [README.md](README.md) 或运行 `./quick_test.sh`
