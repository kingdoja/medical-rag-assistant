# Technical Appendix: Modular RAG MCP Server

> 本文件是根 README 的技术深读版 / 架构附录。对外产品定位请优先查看 [README.md](README.md)。

## Original Technical Positioning

`Modular RAG MCP Server` 是一个可插拔、可观测的模块化 RAG 服务框架，通过 MCP（Model Context Protocol）协议对外暴露工具接口，支持 Copilot / Claude 等 AI 助手直接调用。

在当前仓库中，它被进一步包装为 `PathoMind 医疗知识与质控助手` 的工程底座。也就是说：

- 根 README 负责产品叙事和招聘表达
- 本文件负责补充底层架构、分支策略、学习路径和通用工程视角

---

## 📖 目录

- [项目概述](#-项目概述)
- [分支说明](#-分支说明)
- [快速开始](#-快速开始)
- [谁适合用这个项目 & 怎么用](#-谁适合用这个项目--怎么用)
- [简历参考](#-简历参考)
- [常见问题](#-常见问题)
- [后续安排](#-后续安排)

---

## 🏗️ 项目概述

### 这个项目是什么

本项目将 RAG 面试中最常见的核心环节：**检索（Hybrid Search + Rerank）**、**多模态视觉处理（Image Captioning）**、**RAG 评估（Ragas + Custom）**、**生成（LLM Response）**，以及当下热门的应用协议 **MCP（Model Context Protocol）** 串联为一个完整的、可运行的工程项目。

**项目的一大亮点是极易适配到你自己的业务中**。得益于全链路可插拔架构，你可以快速将它结合到自己已有的项目里，无论你的背景和需求如何，都能找到适合自己的使用方式。具体的使用策略会在后文 [谁适合用这个项目 & 怎么用](#-谁适合用这个项目--怎么用) 中详细展开。

### 不只是项目，更是一整套思路

**比这个项目本身更有价值的，是它背后蕴含的一整套工程化思路**：

- 如何编写 **DEV_SPEC**（开发规格文档）来驱动开发
- 如何用 **Skill** 基于 Spec 自动完成代码编写
- 如何用 **Skill** 进行自动化测试、打包、环境配置
- 如何基于可插拔架构进行扩展（比如扩展到 Agent）

**学会了思路，你可以自己做全新的项目和扩展**。以上每一步的具体做法、设计思路，在笔记中都有对应的视频讲解，建议配合观看。

### 核心能力一览

| 模块 | 能力 | 说明 |
|------|------|------|
| **Ingestion Pipeline** | PDF → Markdown → Chunk → Transform → Embedding → Upsert | 全链路数据摄取，支持多模态图片描述（Image Captioning） |
| **Hybrid Search** | Dense (向量) + Sparse (BM25) + RRF Fusion + Rerank | 粗排召回 + 精排重排的两段式检索架构 |
| **MCP Server** | 标准 MCP 协议暴露 Tools | `query_knowledge_hub`、`list_collections`、`get_document_summary` |
| **Dashboard** | Streamlit 六页面管理平台 | 系统总览 / 数据浏览 / Ingestion 管理 / 摄取追踪 / 查询追踪 / 评估面板 |
| **Evaluation** | Ragas + Custom 评估体系 | 支持 golden test set 回归测试，拒绝“凭感觉”调优 |
| **Observability** | 全链路白盒化追踪 | Ingestion 与 Query 两条链路的每一个中间状态透明可见 |
| **Skill 驱动全流程** | 从编写到测试、打包、配置一键完成 | auto-coder / qa-tester / package / setup 等 Skill 覆盖完整开发生命周期 |

### 技术亮点

**全链路可插拔架构**：LLM / Embedding / Reranker / Splitter / VectorStore / Evaluator 每一个核心环节均定义了抽象接口，支持“乐高积木式”替换，通过配置文件一键切换后端，零代码修改。

**混合检索 + 重排**：BM25 稀疏检索解决专有名词精确匹配，Dense Embedding 解决同义词语义匹配，RRF 融合后可选 Cross-Encoder / LLM Rerank 精排，平衡查全率与查准率。

**多模态图像处理**：采用 Image-to-Text 策略，利用 Vision LLM 自动生成图片描述并缝合进 Chunk，复用纯文本 RAG 链路即可实现“搜文字出图”。

**MCP 生态集成**：遵循 Model Context Protocol 标准，可直接对接 GitHub Copilot、Claude Desktop 等 MCP Client，零前端开发，一次开发处处可用。

**可视化管理 + 自动化评估**：Streamlit Dashboard 提供完整的数据管理与链路追踪能力，集成 Ragas 等评估框架，建立基于数据的迭代反馈回路。

**三层测试体系**：Unit / Integration / E2E 分层测试，覆盖独立模块逻辑、模块间交互、完整链路（MCP Client / Dashboard）。

> 详细架构设计、模块说明和任务排期请参阅 `DEV_SPEC.md`

---

## 📂 分支说明

本项目提供三个分支，面向不同使用场景，请根据自身需求选择：

### `main`

- 最干净的完整代码
- 适合快速体验项目完整能力

### `dev`

- 与 `main` 代码一致
- 保留完整 commit 历史，适合回溯开发过程

### `clean-start`

- 仅保留骨架与规范
- 适合从零体验 spec 驱动开发流程

---

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone <repo-url>
cd Modular-RAG-MCP-Server
```

### 2. 安装依赖

```bash
pip install -e ".[dev]"
```

### 3. 启动主要能力

```bash
streamlit run scripts/start_dashboard.py
python scripts/ingest.py --input-dir ./data/documents
python scripts/evaluate.py --test-set ./data/eval/golden_test_set.json
```

---

## 🎯 谁适合用这个项目 & 怎么用

- 把它当作完整的 RAG / MCP 工程学习样例
- 把它改造成自己行业的垂直知识产品
- 把它融入已有 Agent / AI 应用项目中
- 把它当作 spec + skill 协作工作流的模板

---

## 📄 简历参考

如果你更关心“如何把这个项目讲成一个好项目”，请优先查看：

- `简历/项目改造方案-医疗知识助手/`
- `docs/specs/medical-assistant/PRODUCT_BRIEF.md`

---

## ❓常见问题

### 这个仓库现在到底是什么？

对外，它是 `PathoMind 医疗知识与质控助手`。

对内，它依然是一个模块化 RAG / MCP 工程底座。

### 为什么要保留技术附录？

因为招聘方更关心产品定位和落地表达，工程方更关心架构抽象、模块边界和可扩展性。这两个视角都重要，但不适合挤在同一个首页第一屏里。

---

## ⏭️ 后续安排

- 持续补充公开 demo 数据集
- 完善标准演示题集与回归场景
- 逐步把医疗化命名同步到 Dashboard、MCP tool 文案与展示材料
