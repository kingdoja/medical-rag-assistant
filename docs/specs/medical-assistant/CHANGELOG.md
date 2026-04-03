# Changelog

## 2026-04-03

### Changed

- 按 `DEMO_DATA_SOURCES.md` 下载首轮 6 份核心公开资料到 `demo-data/`
- 更新 `demo-data/sources.md`，登记已下载文件与下载日期
- 新增 `demo-data/INGESTION_COMMANDS.md`，固化 collection 名、py310 命令和首轮查询命令
- 新增 `config/settings.medical_demo.local.example.yaml`，提供医疗 demo 最小化本地配置模板
- 更新 `.gitignore`，忽略 `config/settings.medical_demo.local.yaml`
- 新增 `DEMO_DATA_SOURCES.md`，固化首轮真实公开 demo 文档来源清单
- 新增 `DEMO_SCENARIO_MAPPING.md`，将 12 题标准题集映射到真实公开文档
- 建立 `demo-data/` 工作区骨架与 `sources.md` 登记表，便于后续实际收集资料
- 更新 spec 首页、manifest、runbook 与项目内 skill，使 agent 能读取新文档
- 将当前目标从“题集骨架”推进到“真实来源清单 + 题集映射 + 工作区骨架”

### Validation

- 已成功下载 6 份首轮核心资料到本地工作区
- 使用 `C:\\ProgramData\\Anaconda3\\envs\\py310\\python.exe` 运行 `scripts/ingest.py --dry-run`，识别到 6 个 PDF
- 确认默认 `python` 解释器会因版本不兼容报错，已在命令文档和状态文件中记录
- 已将 demo 配置收敛到最小模板，首轮只要求填写 `embedding.api_key`
- 选用来源均为 WHO、Leica Biosystems、Roche Diagnostics 等官方公开页面或官方 PDF
- DEMO_DATA_SOURCES 与 DEMO_SCENARIO_MAPPING 的依赖关系已写入 `SPEC_MANIFEST.yaml`
- 项目内 skill、spec-map、task-routing 已同步新文档读取协议

### Next

- 复制并填写 `config/settings.medical_demo.local.yaml`
- 建立实际 collection `medical_demo_v01` 并跑 S1、S2、S4、S5、S6、S7 的首轮验证
- 开始 Dashboard 首页、页面名与示例问题的医疗化改造

## 2026-04-02

### Changed

- 在 `DEVELOPMENT_SPEC.md` 中补充 6 步项目路线、当前阶段定义与固定优先级
- 将 `DEMO_DATA_CHECKLIST.md` 从原则清单扩展为可执行的公开医疗 demo 数据包方案
- 将 `DEMO_SCENARIOS.md` 从 7 个骨架场景扩展为 v0.1 的 12 题标准演示题集
- 将 `EXECUTION_STATUS.yaml` 当前阶段切换为 `demo-data-and-scenarios`

### Validation

- 核对路线图与 `PRD.md` 的 v0.1 范围、P0 / P1 / P2 不冲突
- 核对最小数据包方案符合“公开、可说明来源、可去敏”的既有边界
- 核对标准题集覆盖 SOP、指南、术语、设备、图文、培训、拒答等核心场景

### Next

- 准备真实可导入的公开医疗 demo 数据包
- 将 12 题标准题映射到实际文档并跑通首轮演示
- 开始 Dashboard 首页与页面文案医疗化改造

## 2026-04-02

### Changed

- 新建 `.agents/skills/medical-assistant/`，补齐 `SKILL.md`、`agents/openai.yaml`、`references/`、`templates/`
- 重写根 `README.md`，切换为“医疗产品定位 + 通用底座补充”的双层叙事
- 将 `README_FULL.md` 降级为技术深读版 / 架构附录
- 同步精简 `简历/项目改造方案-医疗知识助手/README.md`，明确主工程入口与真源入口

### Validation

- 校验 skill 目录包含 `SKILL.md`、`agents/openai.yaml`、`references/`、`templates/`
- 校验根 README 已链接 spec 真源、展示目录与 `README_FULL.md`
- 校验展示层 README 不再承担执行规范职责
- 将正式 Markdown 入口链接改为相对路径，确保仓库内可点击
- 核对 git 状态中的新增内容均属于本轮计划产物

### Next

- 准备公开 demo 数据集并对齐 `DEMO_DATA_CHECKLIST.md`
- 补齐标准演示题集并对齐 `DEMO_SCENARIOS.md`
- 逐步把医疗化定位同步到 Dashboard 与 MCP tool 文案

## 2026-04-02

### Added

- 新建 `docs/specs/medical-assistant/` 作为工程真源目录
- 新增：
  - `README.md`
  - `PRODUCT_BRIEF.md`
  - `DEVELOPMENT_SPEC.md`
  - `PRD.md`
  - `DEMO_DATA_CHECKLIST.md`
  - `DEMO_SCENARIOS.md`
  - `SPEC_MANIFEST.yaml`
  - `EXECUTION_STATUS.yaml`
  - `AGENT_RUNBOOK.md`

### Changed

- 将医疗方向文档从“简历目录中的草稿”升级为 agent 可消费的 spec 体系

### Next

- 建立展示层 README、求职版项目建议、1 分钟讲稿
- 删除旧文件名，避免出现重复真源
