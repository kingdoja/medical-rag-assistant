# Agent Runbook

## 目标

规定 agent 在本项目中如何读取 spec、执行任务、校验结果和回写记录。

## 真源目录

- 真源：`docs/specs/medical-assistant/`
- 展示层：`简历/项目改造方案-医疗知识助手/`

当两处内容冲突时，以真源目录为准。

## 执行前必须读取

1. `README.md`
2. `SPEC_MANIFEST.yaml`
3. `EXECUTION_STATUS.yaml`

## 按任务读取

### 产品与范围类任务

- `PRODUCT_BRIEF.md`
- `PRD.md`

### 开发与测试类任务

- `DEVELOPMENT_SPEC.md`
- `DEMO_DATA_CHECKLIST.md`
- `DEMO_DATA_SOURCES.md`
- `DEMO_SCENARIOS.md`
- `DEMO_SCENARIO_MAPPING.md`

### 状态与历史类任务

- `EXECUTION_STATUS.yaml`
- `CHANGELOG.md`

## 执行中规则

- 不得猜测产品边界，以 `PRODUCT_BRIEF.md` 和 `PRD.md` 为准
- 不得引入超出当前版本范围的高风险功能
- 处理 demo 数据时必须遵守 `DEMO_DATA_CHECKLIST.md`
- 做演示或回归时必须参考 `DEMO_SCENARIOS.md`

## 执行后回写

执行完成后必须更新：

1. `EXECUTION_STATUS.yaml`
2. `CHANGELOG.md`

如果新增或删除 spec 文件，还必须更新：

3. `SPEC_MANIFEST.yaml`

## 失败处理

若任务失败，至少记录：

- 失败任务
- 失败原因
- 已尝试动作
- 后续建议

并写入：

- `EXECUTION_STATUS.yaml` 的 `blocked`
- `CHANGELOG.md` 的最新记录
