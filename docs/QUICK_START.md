# 快速开始指南

本指南将帮助你在5分钟内运行起 PathoMind 系统。

## 前置要求

- Python 3.11 或更高版本
- 8GB+ RAM
- OpenAI API Key（或其他LLM提供商的API Key）

## 安装步骤

### 1. 克隆仓库

```bash
git clone https://github.com/yourusername/pathomind.git
cd pathomind
```

### 2. 创建虚拟环境

```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Linux/Mac:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate
```

### 3. 安装依赖

```bash
# 使用 pip
pip install -r requirements.txt

# 或使用 pip 安装开发版本（包含测试工具）
pip install -e ".[dev]"
```

### 4. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入你的 API Key
# 至少需要设置：
# OPENAI_API_KEY=your_api_key_here
```

### 5. 配置系统设置

```bash
# 复制配置文件模板
cp config/settings.yaml.example config/settings.yaml

# 根据需要调整配置（可选）
# 默认配置已经可以直接使用
```

## 运行示例

### 方式1: 摄取示例数据并查询

```bash
# 1. 摄取示例医疗文档
python scripts/ingest.py \
  --collection medical_demo \
  --source demo-data/guidelines \
  --config config/settings.yaml

# 2. 执行查询
python scripts/query.py \
  --collection medical_demo \
  --query "WHO实验室质量管理体系的核心要素是什么？"
```

### 方式2: 启动可视化Dashboard

```bash
# 启动 Streamlit Dashboard
python scripts/start_dashboard.py

# 在浏览器中访问: http://localhost:8501
```

Dashboard 功能：
- 📊 Overview: 系统概览和统计
- 📥 Ingestion Manager: 数据摄取管理
- 🔍 Data Browser: 浏览已摄取的数据
- 📈 Evaluation Panel: 查看评估结果
- 🔬 Medical Demo Evaluation: 医疗场景专项评估

### 方式3: 作为MCP服务器运行

```bash
# 启动 MCP 服务器
python -m src.mcp_server.server

# 服务器将监听标准输入/输出
# 可以被 Claude Desktop 或其他 MCP 客户端调用
```

## 验证安装

运行测试以验证安装是否成功：

```bash
# 运行单元测试（快速）
pytest tests/unit/ -v

# 运行所有测试
pytest
```

## 常见问题

### Q: 提示 "No module named 'xxx'"

A: 确保已激活虚拟环境并安装了所有依赖：
```bash
source .venv/bin/activate  # 或 Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Q: OpenAI API 调用失败

A: 检查以下几点：
1. `.env` 文件中的 `OPENAI_API_KEY` 是否正确
2. 网络连接是否正常
3. API Key 是否有足够的额度

### Q: 向量数据库初始化失败

A: 确保 `data/db/chroma` 目录存在且有写入权限：
```bash
mkdir -p data/db/chroma
mkdir -p data/db/bm25
```

### Q: 内存不足

A: 尝试以下方法：
1. 减小 `config/settings.yaml` 中的 `batch_size`
2. 减小 `retrieval.dense_top_k` 和 `retrieval.sparse_top_k`
3. 使用更小的embedding模型

## 下一步

- 📖 阅读 [完整文档](../README.md)
- 🎯 查看 [应用场景示例](../docs/specs/medical-assistant/demo/DEMO_SCENARIOS.md)
- 🧪 运行 [评估测试](../docs/specs/medical-assistant/operations/EVALUATION_BASELINE.md)
- 🔧 自定义 [配置选项](../config/settings.yaml.example)

## 获取帮助

- 查看 [FAQ](FAQ.md)
- 提交 [Issue](https://github.com/yourusername/pathomind/issues)
- 阅读 [贡献指南](../CONTRIBUTING.md)
