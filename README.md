# PathoMind Medical Knowledge and Quality Assistant

> 面向病理科 / 检验科内部知识管理、培训问答与流程质控场景的 AI 知识助手。它不是通用聊天机器人，也不是自动诊断系统，而是构建在模块化 RAG / MCP 底座之上的垂直知识产品案例。

## Why This Project

这个仓库当前的主叙事是：把原来的通用 `Modular RAG MCP Server` 改造成一个更适合招聘市场展示、也更容易让面试官秒懂的垂直产品。

主推方向选择为 `病理 / 检验科医疗知识与质控助手`，原因有三点：

- 和个人经历闭环更强：医疗视觉检测经验 + RAG / Agent 工程化能力可以自然串起来
- 和当前仓库能力更匹配：多模态摄取、混合检索、引用回答、评估、MCP 接入都能直接映射到医疗知识场景
- 风险更可控：聚焦知识、培训、质控、流程辅助，不碰自动诊断和高风险临床决策

## Product Positioning

### One-Liner

`PathoMind` 是一个面向病理科 / 检验科内部使用的医疗知识与质控助手，支持指南 / SOP 检索、术语解释、规范引用回答、图文资料检索、流程排障和 Agent 接入。

### Target Users

- 病理科医生
- 检验科医生 / 技师
- 新人培训人员
- 科室质控负责人
- 院内信息化 / AI 工具接入人员

### Core Scenarios

- 指南 / SOP 检索
- 病理 / 检验术语解释
- 规范引用回答
- 图文混合资料检索
- 设备 / 流程排障问答
- 培训问答
- MCP 接入外部 Agent

## From RAG Platform To Medical Product

虽然对外定位已经切到医疗产品，但底层仍然是一个可复用的模块化 RAG / MCP 工程底座。

| 底层能力 | 医疗产品映射 |
|---|---|
| BM25 + Dense + RRF + rerank | 医疗术语、规范编号、自然语言问法并存场景下的可信检索 |
| Ingestion pipeline | 指南、SOP、设备说明书、培训资料的统一摄取与增量入库 |
| Image captioning / multimodal response | 图文病例资料、流程图、培训图片的混合检索 |
| Trace / evaluation | 引用可追溯、效果可评估、流程可审计 |
| MCP tools | 供 Agent / Copilot 调用的医疗知识基础设施 |

如果从工程视角看，这个仓库依然保留了通用框架能力：

- 可插拔 LLM / Embedding / Reranker / VectorStore
- Streamlit Dashboard
- MCP tool 暴露
- 评估与可观测能力
- spec 驱动的 agent / skill 工作流

## Read This Repo In Two Ways

### 招聘视角

如果你希望把它当成简历代表作来看，建议按这个顺序：

1. 查看 [简历求职材料](简历/项目改造方案-医疗知识助手/README.md)
2. 查看 [产品简报](docs/specs/medical-assistant/PRODUCT_BRIEF.md)
3. 查看 [1 分钟讲稿](简历/项目改造方案-医疗知识助手/面试讲稿-1分钟.md)

### 工程视角

如果你想从“这个产品怎么被工程化”来读，建议按这个顺序：

1. 查看 [spec 首页](docs/specs/medical-assistant/README.md)
2. 查看 [PRD](docs/specs/medical-assistant/PRD.md)
3. 查看 [开发规范](docs/specs/medical-assistant/DEVELOPMENT_SPEC.md)
4. 查看 [项目内 skill](.agents/skills/medical-assistant/SKILL.md)
5. 查看 [技术深读版 README](README_FULL.md)

## Quick Demo Path

如果你准备做求职展示，推荐用下面这条最短演示路径：

1. 先讲产品定位：病理 / 检验科医疗知识与质控助手
2. 再讲能力映射：混合检索、图文摄取、引用回答、可追踪评估
3. 然后讲边界：不做自动诊断，不做高风险医疗决策建议
4. 最后讲工程化：spec 真源 + project-local skill + MCP 接入

## Repo Navigation

### Engineering Source Of Truth

- [medical specs](docs/specs/medical-assistant/README.md)
- [execution status](docs/specs/medical-assistant/EXECUTION_STATUS.yaml)
- [changelog](docs/specs/medical-assistant/CHANGELOG.md)

### Showcase Layer

- [resume materials](简历/项目改造方案-医疗知识助手/README.md)

### Skill Layer

- [medical assistant skill](.agents/skills/medical-assistant/SKILL.md)

### Technical Appendix

- [README_FULL.md](README_FULL.md)

## Spec And Skill Workflow

这个仓库现在采用“spec 真源 + project-local skill”协作方式：

1. 先读 [spec 首页](docs/specs/medical-assistant/README.md)
2. 再读 [SPEC_MANIFEST.yaml](docs/specs/medical-assistant/SPEC_MANIFEST.yaml)
3. 根据任务读取 `PRD`、`DEVELOPMENT_SPEC`、`DEMO_*`
4. 使用 [medical assistant skill](.agents/skills/medical-assistant/SKILL.md) 执行、校验、回写
5. 完成后更新 [EXECUTION_STATUS.yaml](docs/specs/medical-assistant/EXECUTION_STATUS.yaml) 和 [CHANGELOG.md](docs/specs/medical-assistant/CHANGELOG.md)

## Compliance Boundaries

这个项目明确不做以下事项：

- 不做自动诊断
- 不给出高风险医疗决策建议
- 不替代医生判断
- 不输出无引用依据的医疗结论

它的定位始终是：`知识检索 + 培训支持 + 质控辅助 + 流程协同`。
