# 🔍 Modular RAG MCP Server

> 面向垂直领域的模块化知识检索系统，支持医疗、自动驾驶等多领域知识库

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 📋 项目简介

本项目是一个基于 RAG（检索增强生成）技术的模块化知识检索系统，可快速适配不同垂直领域的知识库。系统不做自动诊断或决策，而是帮助专业人员快速检索内部文档，提供带引用的可信回答。

目前已支持的领域：
- 🏥 **医疗知识助手**：病理科/检验科指南、SOP、设备手册检索
- 🚗 **自动驾驶知识检索**：传感器文档、算法文档、法规标准、测试场景检索

### 核心特性

- 🔍 **混合检索**：BM25 + 向量检索 + RRF 融合 + Cross-Encoder 重排序
- 🎯 **Metadata Boost**：针对查询类型动态提升目标文档权重（传感器查询优先返回传感器文档）
- 📚 **多模态支持**：处理 PDF、图片、表格等多种格式
- 📎 **精准引用**：每个回答标注来源文档和页码，可追溯验证
- 🔌 **MCP 集成**：支持作为 MCP 服务器被 AI Agent 调用
- 📊 **可观测性**：完整的 trace 记录、评估指标和可视化 Dashboard

### 技术亮点

- **模块化架构**：可插拔的 LLM、Embedding、Reranker、向量数据库
- **领域适配**：通过配置和 metadata 标签快速切换知识领域
- **工程化实践**：完整测试覆盖（单元/集成/E2E）、配置管理、日志追踪
- **增量更新**：基于 SHA256 哈希的增量摄取，避免重复处理

## 🚀 快速开始

### 环境要求

- Python 3.11+
- 8GB+ RAM
- OpenAI API Key 或 Azure OpenAI 配置

### 安装步骤

```bash
# 1. 克隆仓库
git clone https://github.com/yourusername/modular-rag-mcp-server.git
cd modular-rag-mcp-server

# 2. 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的 API keys

# 5. 配置设置
cp config/settings.yaml.example config/settings.yaml
```

### 数据摄取

```bash
# 医疗知识库
python scripts/ingest.py \
  --collection medical_demo_v01 \
  --source demo-data/guidelines \
  --config config/settings.yaml

# 自动驾驶知识库
python scripts/ingest.py \
  --collection ad_knowledge_v01 \
  --source demo-data-ad/ \
  --config config/settings.ad_knowledge.yaml
```

### 启动服务

```bash
# 命令行查询
python scripts/query.py --collection medical_demo_v01 --query "WHO实验室质量管理体系的核心要素？"
python scripts/query.py --collection ad_knowledge_v01 --query "激光雷达的探测距离和分辨率参数"

# 启动可视化 Dashboard
python scripts/start_dashboard.py

# 启动 MCP 服务器（供 AI Agent 调用）
python -m src.mcp_server.server
```

## 📊 系统架构

```
用户查询
    ↓
Query Analyzer      (复杂度检测、意图分类)
    ↓
Query Processor     (关键词提取、术语识别)
    ↓
Hybrid Search       (BM25 + Dense + RRF Fusion)
    ↓
Metadata Booster    (查询类型感知的权重提升)
    ↓
Document Grouper    (按来源文档分组)
    ↓
Reranker            (Cross-Encoder 重排序)
    ↓
Citation Enhancer   (引用元数据增强)
    ↓
Response Builder    (多文档综合响应)
    ↓
Boundary Validator  (边界控制：拒绝预测/诊断类查询)
    ↓
响应与引用
```

## 🧪 测试

```bash
# 运行所有单元测试
pytest tests/unit/ -v

# 运行集成测试
pytest tests/integration/ -v

# 运行 E2E 测试
pytest tests/e2e/ -v

# 查看覆盖率
pytest --cov=src --cov-report=html
```

## 📁 项目结构

```
.
├── src/
│   ├── core/
│   │   ├── query_engine/       # 检索、融合、重排序、Metadata Boost
│   │   └── response/           # 响应生成、引用增强、边界控制
│   ├── ingestion/              # 文档摄取流水线
│   ├── libs/                   # 可插拔组件（LLM、Embedding、Reranker）
│   ├── mcp_server/             # MCP 服务器
│   └── observability/          # Dashboard、评估、追踪
├── tests/
│   ├── unit/                   # 单元测试
│   ├── integration/            # 集成测试
│   └── e2e/                    # 端到端测试
├── config/                     # 配置文件
├── demo-data/                  # 医疗示例数据
├── demo-data-ad/               # 自动驾驶示例数据
├── docs/                       # 文档
└── scripts/                    # 工具脚本
```

## 🔧 配置说明

```yaml
# config/settings.yaml 核心配置
llm:
  provider: openai
  model: gpt-4o-mini

embedding:
  provider: openai
  model: text-embedding-3-small

retrieval:
  top_k: 20
  rerank_top_k: 5
  fusion_method: rrf

vector_store:
  provider: chroma
  persist_directory: data/db/chroma
```

## 🛡️ 边界控制

系统明确**不做**以下事项：
- ❌ 不做自动诊断或实时故障判断
- ❌ 不提供预测性分析或未来趋势判断
- ❌ 不替代专业人员决策

定位：**知识检索 + 文档引用 + 流程辅助**

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE)

## 👤 作者

**King Doja**
- GitHub: [@kingdoja]
- Email: 1477793103@qq.com
