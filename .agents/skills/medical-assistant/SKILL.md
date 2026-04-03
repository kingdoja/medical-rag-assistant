---
name: medical-assistant
description: Project-local execution skill for the PathoMind medical assistant specs. Reads the medical spec source of truth, routes tasks by type, executes or validates against the correct docs, and writes back execution status plus changelog. Use when the user asks to implement, validate, sync, or update the medical assistant project according to spec.
---

# Medical Assistant Skill

这是 `PathoMind 医疗知识与质控助手` 的项目内 skill。它只服务当前仓库，不做跨项目抽象。

## Purpose

统一完成三类动作：

- `execute`：按 spec 执行实现、文档整理或展示材料同步
- `validate`：按 spec 校验结果、边界与一致性
- `sync-records`：只更新状态与变更记录

## Source Of Truth

- 真源目录：`docs/specs/medical-assistant/`
- 展示目录：`简历/项目改造方案-医疗知识助手/`

当两处内容冲突时，始终以真源目录为准。禁止直接把展示目录当成执行规范。

## Mandatory Read Order

每次执行前必须按以下顺序读取：

1. `docs/specs/medical-assistant/README.md`
2. `docs/specs/medical-assistant/SPEC_MANIFEST.yaml`
3. `docs/specs/medical-assistant/EXECUTION_STATUS.yaml`

然后根据任务类型继续读取，具体映射见：

- `references/spec-map.md`
- `references/task-routing.md`

## Routing Rules

### execute

- 产品定义、定位、展示材料同步：读 `PRODUCT_BRIEF.md`、`PRD.md`
- 开发与实现：读 `DEVELOPMENT_SPEC.md`
- demo 数据相关：读 `DEMO_DATA_CHECKLIST.md`、`DEMO_DATA_SOURCES.md`
- 演示与回归相关：读 `DEMO_SCENARIOS.md`、`DEMO_SCENARIO_MAPPING.md`

### validate

- 产品边界和范围：以 `PRD.md` 为主
- 开发规范与工程约束：以 `DEVELOPMENT_SPEC.md` 为主
- 数据来源、命名、去敏：以 `DEMO_DATA_CHECKLIST.md`、`DEMO_DATA_SOURCES.md` 为主
- 演示行为、引用要求、拒答边界：以 `DEMO_SCENARIOS.md`、`DEMO_SCENARIO_MAPPING.md` 为主

### sync-records

- 只读取 `EXECUTION_STATUS.yaml` 和 `CHANGELOG.md`
- 不新增功能，不扩写 spec 结论

## Execution Contract

1. 先确认任务属于 `execute`、`validate` 或 `sync-records`
2. 读取必要 spec，禁止凭猜测补边界
3. 执行任务时不得越过当前版本范围，不得引入自动诊断类高风险功能
4. 如涉及展示材料，必须从真源提炼，不得直接在展示目录发明新口径
5. 完成后按固定顺序回写记录

## Write-Back Contract

任务完成后必须更新：

1. `docs/specs/medical-assistant/EXECUTION_STATUS.yaml`
2. `docs/specs/medical-assistant/CHANGELOG.md`

只有在新增、删除或重命名 spec 文件时，才更新：

3. `docs/specs/medical-assistant/SPEC_MANIFEST.yaml`

状态字段和 changelog 写法分别参考：

- `templates/execution-status-template.yaml`
- `templates/changelog-entry-template.md`

## Validation Rules

- 不宣称自动诊断
- 不输出高风险医疗决策建议
- 不新增与 `PRODUCT_BRIEF.md` / `PRD.md` 冲突的产品口径
- 不绕过 `DEMO_DATA_CHECKLIST.md` 的来源与去敏要求
- 不绕过 `DEMO_SCENARIOS.md` 的引用要求与拒答边界

## Failure Handling

如果任务失败，至少记录：

- 失败任务
- 失败原因
- 已尝试动作
- 后续建议

并回写到：

- `EXECUTION_STATUS.yaml` 的 `blocked`
- `CHANGELOG.md` 的最新记录

## Typical Triggers

- “按医疗 spec 实施这个任务”
- “按 spec 校验医疗 demo”
- “同步医疗项目状态”
- “更新医疗项目 changelog”
- “把求职材料和真源 spec 对齐”


