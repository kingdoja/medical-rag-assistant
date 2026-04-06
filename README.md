# 🏥 PathoMind - 医疗知识与质控助手

> 面向病理科/检验科的智能知识检索与质控辅助系统

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 📋 项目简介

PathoMind 是一个基于 RAG（检索增强生成）技术的医疗知识助手，专为病理科和检验科设计。它不是自动诊断系统，而是帮助医护人员快速检索指南、SOP、设备手册等内部知识，提供带引用的可信回答。

### 核心特性

- 🔍 **混合检索**：BM25 + 向量检索 + RRF融合 + 重排序，适配医疗术语和自然语言查询
- 📚 **多模态支持**：处理PDF文档、图片、表格等多种格式的医疗资料
- 🎯 **精准引用**：每个回答都标注来源文档和页码，可追溯验证
- 📊 **可观测性**：完整的trace记录、评估指标和可视化dashboard
- 🔌 **MCP集成**：支持作为MCP服务器被AI Agent调用

### 技术亮点

- **模块化架构**：可插拔的LLM、Embedding、Reranker、向量数据库
- **工程化实践**：完整的测试覆盖（单元/集成/E2E）、配置管理、日志追踪
- **评估体系**：基于RAGAS的自动化评估，包含准确率、召回率等多维度指标
- **增量更新**：支持文档增量摄取，避免重复处理

## 🎯 应用场景

| 场景 | 说明 | 示例 |
|------|------|------|
| 指南检索 | 快速查找WHO、行业标准等指南内容 | "WHO实验室质量管理体系的核心要素是什么？" |
| SOP查询 | 检索标准操作流程和规范 | "样本管理的标准流程是什么？" |
| 设备排障 | 查询设备手册和故障处理方法 | "Peloris 3组织处理仪如何进行日常维护？" |
| 术语解释 | 解释专业术语和缩写 | "什么是IHC？" |
| 培训支持 | 为新员工提供知识问答 | "质量控制的基本原则有哪些？" |

## 🚀 快速开始

### 环境要求

- Python 3.11+
- 8GB+ RAM
- OpenAI API Key 或 Azure OpenAI 配置

### 安装步骤

```bash
# 1. 克隆仓库
git clone https://github.com/yourusername/pathomind.git
cd pathomind

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
# 根据需要调整配置
```

### 数据摄取

```bash
# 摄取示例医疗文档
python scripts/ingest.py \
  --collection medical_demo_v01 \
  --source demo-data/guidelines \
  --config config/settings.medical_demo.local.yaml
```

### 启动服务

```bash
# 方式1: 命令行查询
python scripts/query.py \
  --collection medical_demo_v01 \
  --query "WHO实验室质量管理体系的核心要素是什么？"

# 方式2: 启动可视化Dashboard
python scripts/start_dashboard.py

# 方式3: 启动MCP服务器（供AI Agent调用）
python -m src.mcp_server.server
```

## 📊 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                        用户查询                              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    查询处理层                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ 查询分析     │  │ 意图识别     │  │ 范围提取     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    混合检索层                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ BM25检索     │  │ 向量检索     │  │ RRF融合      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    重排序层                                  │
│  ┌──────────────┐  ┌──────────────┐                         │
│  │ Cross-Encoder│  │ LLM Reranker │                         │
│  └──────────────┘  └──────────────┘                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    响应生成层                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ 上下文组装   │  │ LLM生成      │  │ 引用增强     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## 🧪 测试与评估

### 运行测试

```bash
# 运行所有测试
pytest

# 运行单元测试
pytest tests/unit/

# 运行集成测试
pytest tests/integration/

# 运行E2E测试
pytest tests/e2e/

# 查看测试覆盖率
pytest --cov=src --cov-report=html
```

### 评估系统性能

```bash
# 运行医疗场景评估
python scripts/run_medical_evaluation.py

# 查看评估结果
python scripts/start_dashboard.py
# 访问 http://localhost:8501 -> Medical Demo Evaluation
```

评估指标包括：
- **Answer Correctness**: 答案准确性（0-1）
- **Context Precision**: 检索精确度（0-1）
- **Context Recall**: 检索召回率（0-1）
- **Faithfulness**: 答案忠实度（0-1）

## 📁 项目结构

```
pathomind/
├── src/                          # 源代码
│   ├── core/                     # 核心查询引擎
│   │   ├── query_engine/         # 检索、融合、重排序
│   │   └── response/             # 响应生成、引用增强
│   ├── ingestion/                # 数据摄取管道
│   │   ├── chunking/             # 文档分块
│   │   ├── embedding/            # 向量编码
│   │   └── storage/              # 存储管理
│   ├── libs/                     # 可插拔组件库
│   │   ├── llm/                  # LLM适配器
│   │   ├── embedding/            # Embedding适配器
│   │   ├── reranker/             # Reranker适配器
│   │   └── vector_store/         # 向量数据库适配器
│   ├── mcp_server/               # MCP服务器
│   └── observability/            # 可观测性
│       ├── dashboard/            # Streamlit Dashboard
│       └── evaluation/           # 评估框架
├── tests/                        # 测试代码
│   ├── unit/                     # 单元测试
│   ├── integration/              # 集成测试
│   └── e2e/                      # 端到端测试
├── config/                       # 配置文件
├── demo-data/                    # 示例数据
│   ├── guidelines/               # WHO指南
│   ├── sops/                     # 标准操作流程
│   ├── manuals/                  # 设备手册
│   └── training/                 # 培训资料
├── docs/                         # 文档
│   └── specs/                    # 产品规格说明
└── scripts/                      # 工具脚本
```

## 🔧 配置说明

主要配置文件：`config/settings.yaml`

```yaml
# LLM配置
llm:
  provider: openai  # openai, azure, ollama
  model: gpt-4o-mini
  temperature: 0.1

# Embedding配置
embedding:
  provider: openai
  model: text-embedding-3-small
  batch_size: 100

# 检索配置
retrieval:
  top_k: 20
  rerank_top_k: 5
  fusion_method: rrf

# 向量数据库
vector_store:
  provider: chroma
  persist_directory: data/db/chroma
```

## 📈 性能指标

基于医疗场景测试集（20个问题）的评估结果：

| 指标 | P1版本 | 目标 |
|------|--------|------|
| Answer Correctness | 0.72 | 0.75+ |
| Context Precision | 0.85 | 0.80+ |
| Context Recall | 0.78 | 0.75+ |
| Faithfulness | 0.88 | 0.85+ |

## 🛡️ 合规边界

本系统明确**不做**以下事项：
- ❌ 不做自动诊断
- ❌ 不给出高风险医疗决策建议
- ❌ 不替代医生判断
- ❌ 不输出无引用依据的医疗结论

定位：**知识检索 + 培训支持 + 质控辅助 + 流程协同**

## 🗺️ 技术路线图

### P1 - 核心能力（已完成）
- ✅ 混合检索（BM25 + Dense + RRF）
- ✅ 多模态文档处理
- ✅ 引用增强回答
- ✅ 基础评估体系
- ✅ MCP服务器

### P2 - 增强能力（规划中）
- 🔄 多轮对话支持
- 🔄 查询改写与扩展
- 🔄 文档分组与聚合
- 🔄 高级评估指标
- 🔄 性能优化

详见：[P2 Roadmap](docs/specs/medical-assistant/P2_ROADMAP.md)

## 📚 相关文档

- [产品简报](docs/specs/medical-assistant/core/PRODUCT_BRIEF.md)
- [产品需求文档](docs/specs/medical-assistant/core/PRD.md)
- [开发规范](docs/specs/medical-assistant/core/DEVELOPMENT_SPEC.md)
- [演示指南](docs/specs/medical-assistant/demo/DEMO_RUNBOOK_3MIN.md)
- [完整技术文档](README_FULL.md)

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

1. Fork本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 👤 作者

**林淑能**
- 医疗AI应用开发者
- 专注于RAG系统和AI Agent工程化
- Email: [your-email@example.com]
- GitHub: [@yourusername]

## 🙏 致谢

- 感谢WHO提供的公开医疗指南文档
- 感谢开源社区提供的优秀工具和框架

---

**注意**：本项目仅用于技术展示和学习交流，不应用于实际临床决策。
